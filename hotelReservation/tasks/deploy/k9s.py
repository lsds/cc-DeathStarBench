from invoke import task
from os import makedirs
from os.path import exists, join
from shutil import copy, rmtree
from subprocess import run
from tasks.deploy.env import BIN_DIR, K9S_VERSION
from tasks.deploy.utils.install import _symlink_global_bin
from tasks.deploy.utils.minikube import MINIKUBE_KUBECONFIG_FILE
from tasks.deploy.utils.uk8s import UK8S_KUBECONFIG_FILE


@task(default=True)
def install(ctx, system=False):
    """
    Install the K9s CLI
    """
    tar_name = "k9s_Linux_x86_64.tar.gz"
    url = "https://github.com/derailed/k9s/releases/download/v{}/{}".format(
        K9S_VERSION, tar_name
    )

    # Download the TAR
    workdir = "/tmp/k9s"
    makedirs(workdir, exist_ok=True)

    cmd = "curl -LO {}".format(url)
    run(cmd, shell=True, check=True, cwd=workdir)

    # Untar
    run("tar -xf {}".format(tar_name), shell=True, check=True, cwd=workdir)

    # Copy k9s into place
    if not exists(BIN_DIR):
        makedirs(BIN_DIR)
    binary_path = join(BIN_DIR, "k9s")
    copy(join(workdir, "k9s"), binary_path)

    # Remove tar
    rmtree(workdir)

    # Symlink for k9s command globally
    if system:
        _symlink_global_bin(binary_path, "k9s")


@task()
def get_cmd(ctx, kind="uk8s"):
    """
    Get the command to run k9s with the right env. variables
    """
    if kind == "uk8s":
        kubeconfig_file = UK8S_KUBECONFIG_FILE
    elif kind == "minikube":
        kubeconfig_file = MINIKUBE_KUBECONFIG_FILE
    cmd = "k9s --kubeconfig {}".format(
        kubeconfig_file,
    )
    print(cmd)
