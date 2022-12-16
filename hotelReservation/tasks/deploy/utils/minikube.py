from copy import copy
from os import environ
from os.path import join
from subprocess import run
from tasks.env import PROJ_ROOT

MINIKUBE_KUBECONFIG_FILE = join(PROJ_ROOT, "dev", "minikube_kubeconfig")


def get_minikube_cluster_ip():
    """
    Get the cluster IP address (used for `kubectl`)
    """
    ip_cmd = "KUBECONFIG={} minikube ip".format(MINIKUBE_KUBECONFIG_FILE)
    out = run(ip_cmd, shell=True, capture_output=True)
    cluster_ip = out.stdout.decode("utf-8").strip()
    return cluster_ip


def get_minikube_env_vars():
    # This currently adds no env. variables, we leave it here just in case we
    # need it
    shell_env = copy(environ)
    return shell_env


def get_minikube_kubectl_cmd():
    return "minikube kubectl -- --kubeconfig={}".format(
        MINIKUBE_KUBECONFIG_FILE
    )
