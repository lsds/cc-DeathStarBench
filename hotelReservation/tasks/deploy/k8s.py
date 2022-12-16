from invoke import task
from os import makedirs
from os.path import exists, join
from shutil import rmtree
from subprocess import run
from tasks.utils.config import get_config_value, write_config_file
from tasks.deploy.env import (
    K8S_VERSION,
    K8S_FILES_DIR,
    K8S_INGRESS_FILE,
    K8S_NAMESPACE_FILE,
    K8S_NODE_PORT_FILE,
    K8S_REGISTRY_SECRET_NAME,
    K8S_SERVICE_DIRS,
    K8S_TEMPLATED_DIR,
)
from tasks.deploy.utils.install import (
    _download_binary,
    _symlink_global_bin,
)
from tasks.deploy.utils.k8s import (
    create_registry_secret,
    get_k8s_namespace,
    get_k8s_env_vars,
    get_kubectl_cmd,
    template_and_apply_k8s_files,
    template_and_apply_k8s_dir,
    wait_for_pods_by_ns,
)
from tasks.deploy.utils.minikube import get_minikube_cluster_ip
from tasks.env import DOCKER_USER, get_version
from time import sleep


@task
def install_kubectl(ctx, system=False):
    """
    Install the k8s CLI (kubectl)
    """
    url = "https://dl.k8s.io/release/v{}/bin/linux/amd64/kubectl".format(
        K8S_VERSION,
    )

    binary_path = _download_binary(url, "kubectl")

    # Symlink for kubectl globally
    if system:
        _symlink_global_bin(binary_path, "kubectl")


# TODO(carlosse): make the default for enable_consul `on` when we support
# consul in k8s
@task(default=True)
def deploy(ctx, kind="uk8s", runtime="native", enable_consul="off"):
    """
    Deploy the microservice mesh on a k8s cluster
    """
    _deploy_services(kind, runtime, enable_consul)
    ini_file(ctx, kind)


def _deploy_services(kind, runtime, enable_consul):
    """
    Deploy all the pods and services for the microservice mesh
    """
    # Create the templated directory if it does not exist
    if not exists(K8S_TEMPLATED_DIR):
        makedirs(K8S_TEMPLATED_DIR)

    # Before anything else, create the namespace we will use for all pods,
    # services, and volumes
    k8s_namespace = get_k8s_namespace()
    template_and_apply_k8s_files(
        kind, [K8S_NAMESPACE_FILE], {"namespace": k8s_namespace}
    )

    # First, to pull images from the private registry, we need a docker secret
    # _in the same namespace_ we are deploying the pods. This step relies on
    # you having previously logged in (`docker login`) to your private
    # image registry
    create_registry_secret(kind, k8s_namespace)

    # Second, deploy the databases, as they have no dependencies
    template_vars = {
        "docker_user": DOCKER_USER,
        "registry_secret": K8S_REGISTRY_SECRET_NAME,
        "namespace": k8s_namespace,
    }
    template_and_apply_k8s_dir(
        kind, join(K8S_FILES_DIR, "memcached"), template_vars
    )
    template_and_apply_k8s_dir(
        kind, join(K8S_FILES_DIR, "mongodb"), template_vars
    )
    wait_for_pods_by_ns(kind, k8s_namespace, "intel.dsb.type=database")

    # Third, deploy the microservices
    template_vars = {
        "docker_user": DOCKER_USER,
        "dsb_code_dir": "/code/DeathStarBench/hotelReservation",
        "registry_secret": K8S_REGISTRY_SECRET_NAME,
        "namespace": k8s_namespace,
        "dsb_version": get_version(),
        "enable_consul": enable_consul,
        "runtime": runtime,
    }
    # If the chosen runtime requires SGX, template additional fields
    if runtime == "ego":
        template_vars.update(
            {
                "resources": {
                    "resources": {
                        "limits": {"sgx.intel.com/epc": "10Mi"},
                        "requests": {"sgx.intel.com/epc": "10Mi"},
                    }
                },
            }
        )
    for service_dir in K8S_SERVICE_DIRS:
        template_and_apply_k8s_dir(kind, service_dir, template_vars)
    wait_for_pods_by_ns(kind, k8s_namespace, "intel.dsb.type=microservice")

    # Lastly, deploy the component to hit the frontend endpoint. For local
    # clusters (i.e. uk8s) we use a NodePort service to allow for multiple
    # concurrent deployments under different namespaces. For remote deployments
    # we use Ingress
    if kind == "remote":
        template_and_apply_k8s_files(
            kind, [K8S_INGRESS_FILE], {"namespace": k8s_namespace}
        )
    else:
        template_and_apply_k8s_files(
            kind, [K8S_NODE_PORT_FILE], {"namespace": k8s_namespace}
        )


@task
def delete(ctx, kind=None, namespace=None, keep=False):
    """
    Remove the microservice k8s deployment
    """
    if kind and namespace:
        _kind = kind
        k8s_namespace = namespace
    else:
        _kind = get_config_value("kind")
        k8s_namespace = get_config_value("k8s_namespace")

    cmd = "{} -n {} delete --all -f {}".format(
        get_kubectl_cmd(_kind),
        k8s_namespace,
        K8S_TEMPLATED_DIR,
    )
    print(cmd)
    # Configure the env. variables to delete the deployment
    run(cmd, shell=True, check=True, env=get_k8s_env_vars(kind))

    # By default remove the templated files for a clean transition between
    # deployments
    if not keep:
        rmtree(K8S_TEMPLATED_DIR)
        makedirs(K8S_TEMPLATED_DIR)


@task
def ini_file(ctx, kind):
    """
    Generate ini-file to interact with DSB deployment
    """
    if kind == "uk8s" or kind == "minikube":
        # For a microk8s deployment we use a NodePort service that forwards
        # the frontend traffic to a random port in the localhost IP. Thus we
        # query for the port
        while True:
            if kind == "uk8s":
                frontend_ip = "127.0.0.1"
            elif kind == "minikube":
                frontend_ip = get_minikube_cluster_ip()
            cmd = [
                "{} -n {}".format(get_kubectl_cmd(kind), get_k8s_namespace()),
                "get service frontend-node-port",
                "-o='jsonpath={.spec.ports[0].nodePort}'",
            ]
            cmd = " ".join(cmd)
            frontend_port = run(
                cmd,
                shell=True,
                capture_output=True,
                env=get_k8s_env_vars(kind),
            ).stdout.decode("utf-8")
            if frontend_port != "":
                break
            else:
                print("NodePort port not ready yet")
                sleep(5)
    elif kind == "remote":
        # For an remote deployment we use an Ingress service that only accepts
        # HTTP/HTTPS traffic. Thus, the port is hardcoded to 80 and we need to
        # query for the IP assigned by the cluster
        frontend_port = 80
        while True:
            cmd = [
                "{} -n {}".format(get_kubectl_cmd(kind), get_k8s_namespace()),
                "get ingress http-ingress",
                "-o='jsonpath={.status.loadBalancer.ingress[0].ip}'",
            ]
            cmd = " ".join(cmd)
            frontend_ip = run(
                cmd,
                shell=True,
                capture_output=True,
                env=get_k8s_env_vars(kind),
            ).stdout.decode("utf-8")
            if frontend_ip != "":
                break
            else:
                print("Ingress IP not ready yet")
                sleep(5)
    else:
        print("Unrecognised deployment kind: {}".format(kind))
        raise RuntimeError("Unrecognised deployment kind")

    write_config_file(
        {
            "kind": kind,
            "k8s_namespace": get_k8s_namespace(),
            "frontend_host": frontend_ip,
            "frontend_port": frontend_port,
        }
    )


@task
def kubectl(ctx, kind, args):
    """
    Run kubectl command to the kind of deployment
    """
    kube_cmd = "{} {}".format(get_kubectl_cmd(kind), args)
    run(kube_cmd, shell=True, check=True, env=get_k8s_env_vars(kind))
