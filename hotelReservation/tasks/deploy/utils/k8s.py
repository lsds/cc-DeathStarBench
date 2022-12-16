from jinja2 import Environment, FileSystemLoader
from os import environ, listdir
from os.path import basename, dirname, join
from subprocess import run
from tasks.deploy.env import (
    K8S_DEFAULT_NAMESPACE,
    K8S_REGISTRY_SECRET_NAME,
    K8S_TEMPLATED_DIR,
)
from tasks.deploy.utils.minikube import (
    get_minikube_env_vars,
    get_minikube_kubectl_cmd,
)
from tasks.deploy.utils.uk8s import get_uk8s_env_vars, get_uk8s_kubectl_cmd
from tasks.env import DOCKER_CONFIG
from time import sleep


def get_kubectl_cmd(kind):
    """
    Set the kubectl cmd to interact with the underlying cluster manager
    """
    if kind == "uk8s":
        kubectl_cmd = get_uk8s_kubectl_cmd()
    elif kind == "minikube":
        kubectl_cmd = get_minikube_kubectl_cmd()
    else:
        print("Unrecognised deployment kind: {}".format(kind))
        raise RuntimeError("Unrecognised deployment kind")

    return kubectl_cmd


def get_k8s_env_vars(kind):
    """
    Get the environment variables for the underlying cluster manager
    """
    if kind == "uk8s":
        env_vars = get_uk8s_env_vars()
    elif kind == "minikube":
        env_vars = get_minikube_env_vars()
    else:
        print("Unrecognised deployment kind: {}".format(kind))
        raise RuntimeError("Unrecognised deployment kind")

    return env_vars


def template_k8s_file(template_file_path, output_file_path, template_vars):
    # Load and render the template using jinja
    env = Environment(
        loader=FileSystemLoader(dirname(template_file_path)),
        trim_blocks=True,
        lstrip_blocks=True,
        extensions=["jinja2_ansible_filters.AnsibleCoreFiltersExtension"],
        autoescape=True,
    )
    template = env.get_template(basename(template_file_path))
    output_data = template.render(template_vars)

    # Write to output file
    with open(output_file_path, "w") as fh:
        fh.write(output_data)


def template_and_apply_k8s_files(kind, file_list, template_vars):
    """
    Given a list of templated files, apply the template variables to each
    one of them and apply them to the cluster
    """
    for file_name in file_list:
        output_file = join(K8S_TEMPLATED_DIR, basename(file_name)[:-3])
        template_k8s_file(file_name, output_file, template_vars)
        kube_cmd = "{} apply -f {}".format(get_kubectl_cmd(kind), output_file)
        print(kube_cmd)
        run(kube_cmd, shell=True, check=True, env=get_k8s_env_vars(kind))


def template_and_apply_k8s_dir(kind, dir_path, template_vars):
    """
    Given a directory, apply the template variables to each file in the
    directory with the right file extension and apply them to the cluster
    """
    templated_files = [
        join(dir_path, fn)
        for fn in listdir(dir_path)
        if fn.endswith(".yaml.j2")
    ]
    template_and_apply_k8s_files(kind, templated_files, template_vars)


def get_k8s_namespace():
    """
    Get default k8s namespace unless overwritten by environment variable
    """
    env_value = environ.get("DSB_K8S_NAMESPACE", None)

    if env_value:
        return env_value

    return K8S_DEFAULT_NAMESPACE


def create_registry_secret(kind, k8s_namespace):
    """
    Create a secret in the k8s cluster to pull images from a private container
    registry. Note that the secret must be _in the same_ namespace than the
    pods that are using it
    """
    secret_file = join(K8S_TEMPLATED_DIR, "secret.yaml")

    kube_cmd = [
        "{} create secret generic".format(get_kubectl_cmd(kind)),
        "{}".format(K8S_REGISTRY_SECRET_NAME),
        "--from-file=.dockerconfigjson={}".format(DOCKER_CONFIG),
        "--type=kubernetes.io/dockerconfigjson",
        "--dry-run=client --output=yaml",
        "> {}".format(secret_file),
    ]
    kube_cmd = " ".join(kube_cmd)
    run(kube_cmd, shell=True, check=True)

    sed_cmd = [
        "sed -i",
        "'/name: {}$/a \\  namespace: {}'".format(
            K8S_REGISTRY_SECRET_NAME, k8s_namespace
        ),
        "{}".format(secret_file),
    ]
    sed_cmd = " ".join(sed_cmd)
    print(sed_cmd)
    run(sed_cmd, shell=True, check=True)

    kube_cmd = "{} apply -f {}".format(get_kubectl_cmd(kind), secret_file)
    print(kube_cmd)
    run(kube_cmd, shell=True, check=True)


def wait_for_pods_by_ns(kind, k8s_namespace, label=None):
    """
    Wait for pods to be in `Ready` state. Filter by namespace and, additionally
    if set, by label.
    """
    while True:
        print("Waiting for pods...")
        # Sometimes the filter-by-status command does not list all the pods so
        # we first count how many pods we have to wait for in total
        cmd = [
            "{} -n {}".format(get_kubectl_cmd(kind), k8s_namespace),
            "get pods",
            "-l {}".format(label) if label else "",
        ]
        cmd = " ".join(cmd)
        output = run(
            cmd, shell=True, capture_output=True, env=get_k8s_env_vars(kind)
        ).stdout.decode("utf-8")
        num_pods = max(len(output.split("\n")) - 2, 0)
        cmd = [
            "{} -n {}".format(get_kubectl_cmd(kind), k8s_namespace),
            "get pods",
            "-l {}".format(label) if label else "",
            "-o jsonpath='{..status.conditions[?(@.type==\"Ready\")].status}'",
        ]
        cmd = " ".join(cmd)
        output = run(
            cmd, shell=True, capture_output=True, env=get_k8s_env_vars(kind)
        ).stdout.decode("utf-8")
        statuses = [o.strip() for o in output.split(" ") if o.strip()]
        if all([s == "True" for s in statuses]) and len(statuses) == num_pods:
            print("All pods ready, continuing...")
            break

        print(
            "Pods not ready, waiting for {} pods (status: {})".format(
                num_pods, output
            )
        )
        sleep(5)


def install_sgx_device_plugin(kind):
    """
    Install device plugin following the online instructions:
    https://github.com/intel/intel-device-plugins-for-kubernetes/blob/main/cmd/sgx_plugin/README.md
    """
    if kind == "uk8s":
        kube_cmd = get_uk8s_kubectl_cmd()
    elif kind == "minikube":
        kube_cmd = get_minikube_kubectl_cmd()
    else:
        raise RuntimeError(
            "Unrecognised kind to install SGX plugin ({})".format(kind)
        )

    plugin_release_version = "v0.24.0"
    cert_manager_version = "v1.9.1"

    # Install cert-manager (dependency)
    kubectl_cmd = [
        "{} apply -f".format(kube_cmd),
        (
            "https://github.com/cert-manager/cert-manager/releases/download/"
            "{}/cert-manager.yaml".format(cert_manager_version)
        ),
    ]
    kubectl_cmd = " ".join(kubectl_cmd)
    print(kubectl_cmd)
    run(kubectl_cmd, shell=True, check=True)

    wait_for_pods_by_ns(kind, "cert-manager")

    # Deploy Node-Feature-Discovery (NFD)
    kubectl_cmd = [
        "{} apply -k".format(kube_cmd),
        (
            "https://github.com/intel/intel-device-plugins-for-kubernetes/"
            "deployments/nfd/overlays/sgx?ref={}".format(
                plugin_release_version
            )
        ),
    ]
    kubectl_cmd = " ".join(kubectl_cmd)
    print(kubectl_cmd)
    run(kubectl_cmd, shell=True, check=True)

    kubectl_cmd = [
        "{} apply -k".format(kube_cmd),
        (
            "https://github.com/intel/intel-device-plugins-for-kubernetes/"
            "deployments/nfd/overlays/node-feature-rules"
            "?ref={}".format(plugin_release_version)
        ),
    ]
    kubectl_cmd = " ".join(kubectl_cmd)
    print(kubectl_cmd)
    run(kubectl_cmd, shell=True, check=True)

    wait_for_pods_by_ns(kind, "node-feature-discovery")

    # Deploy the SGX device plugin (first the operator, then the plugin)
    kubectl_cmd = [
        "{} apply -k".format(kube_cmd),
        (
            "https://github.com/intel/intel-device-plugins-for-kubernetes/"
            "deployments/operator/default?ref={}".format(
                plugin_release_version
            )
        ),
    ]
    kubectl_cmd = " ".join(kubectl_cmd)
    print(kubectl_cmd)
    run(kubectl_cmd, shell=True, check=True)

    wait_for_pods_by_ns(kind, "node-feature-discovery")

    # DaemonSet (is this needed?)
    kubectl_cmd = [
        "{} apply -k".format(kube_cmd),
        (
            "https://github.com/intel/intel-device-plugins-for-kubernetes/"
            "deployments/sgx_plugin/base?ref={}".format(plugin_release_version)
        ),
    ]
    kubectl_cmd = " ".join(kubectl_cmd)
    print(kubectl_cmd)
    run(kubectl_cmd, shell=True, check=True)

    # EPC Registration
    kubectl_cmd = [
        "{} apply -k".format(kube_cmd),
        (
            "https://github.com/intel/intel-device-plugins-for-kubernetes/"
            "deployments/sgx_plugin/overlays/"
            "epc-nfd?ref={}".format(plugin_release_version)
        ),
    ]
    kubectl_cmd = " ".join(kubectl_cmd)
    print(kubectl_cmd)
    run(kubectl_cmd, shell=True, check=True)

    # Verify SGX device plugin is registered
    node_name = (
        run(
            "{} get nodes".format(kube_cmd),
            shell=True,
            check=True,
            capture_output=True,
        )
        .stdout.decode("utf-8")
        .split("\n")[1]
        .split(" ")[0]
    )
    kubectl_cmd = [
        kube_cmd,
        "describe node {}".format(node_name),
        "| grep sgx.intel.com",
    ]
    kubectl_cmd = " ".join(kubectl_cmd)
    print(kubectl_cmd)
    run(kubectl_cmd, shell=True, check=True)
