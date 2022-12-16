from invoke import task
from os import makedirs
from os.path import exists, join
from shutil import copy, rmtree
from tasks.deploy.env import BIN_DIR, MINIKUBE_VERSION
from tasks.deploy.utils.k8s import install_sgx_device_plugin
from tasks.deploy.utils.install import _symlink_global_bin
from tasks.deploy.utils.minikube import (
    MINIKUBE_KUBECONFIG_FILE,
    get_minikube_kubectl_cmd,
)
from tasks.env import DOCKER_REGISTRY_URL
from subprocess import run


@task
def install(ctx):
    """
    Install the K9s CLI
    """
    tar_name = "minikube-linux-amd64.tar.gz"
    url = (
        "https://github.com/kubernetes/minikube/releases/"
        "download/v{}/{}".format(MINIKUBE_VERSION, tar_name)
    )

    # Download the TAR
    workdir = "/tmp/minikube"
    makedirs(workdir, exist_ok=True)

    cmd = "curl -LO {}".format(url)
    run(cmd, shell=True, check=True, cwd=workdir)

    # Untar
    run("tar -xf {}".format(tar_name), shell=True, check=True, cwd=workdir)

    # Copy k9s into place
    if not exists(BIN_DIR):
        makedirs(BIN_DIR)
    binary_path = join(BIN_DIR, "minikube")
    copy(join(workdir, "out", "minikube-linux-amd64"), binary_path)

    # Remove tar
    rmtree(workdir)

    # Symlink for k9s command globally
    _symlink_global_bin(binary_path, "minikube")

    # Start minikube
    start(ctx)


@task
def start(ctx):
    """
    Start the minikube cluster with the docker driver
    """
    start_cmd = [
        "KUBECONFIG={} minikube start".format(MINIKUBE_KUBECONFIG_FILE),
        "--driver=docker",
        # Due to a bug in cri-docker we can't use the latest kubernetes version
        # with the docker driver. The issue is tracked here:
        # https://github.com/kubernetes/minikube/issues/14789
        "--kubernetes-version=1.23.10",
        "--insecure-registry {}".format(DOCKER_REGISTRY_URL),
        # TODO(carlosse): we may want to make the path to the SGX driver a
        # variable here (see #91)
        "--mount --mount-string /dev/sgx:/dev/sgx",
    ]
    start_cmd = " ".join(start_cmd)
    print(start_cmd)
    run(start_cmd, check=True, shell=True)

    # Test that we can query the cluster using kubectl
    kube_cmd = "{} get nodes".format(get_minikube_kubectl_cmd())
    print(kube_cmd)
    run(kube_cmd, check=True, shell=True)

    # Install the SGX device plugin
    install_sgx_device_plugin("minikube")


@task
def delete(ctx):
    """
    Delete the minikube cluster
    """
    delete_cmd = "minikube delete --all"
    run(delete_cmd, check=True, shell=True)
