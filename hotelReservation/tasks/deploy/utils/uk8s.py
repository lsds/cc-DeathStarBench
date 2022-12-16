from copy import copy
from os import environ
from os.path import join
from subprocess import run
from tasks.env import PROJ_ROOT

UK8S_KUBECONFIG_FILE = join(PROJ_ROOT, "dev", "uk8s_kubeconfig")


def get_uk8s_cluster_ip():
    """
    Get the cluster IP address (used for `kubectl`)
    """
    ip_cmd = "microk8s config | grep server"
    out = run(ip_cmd, shell=True, capture_output=True)
    cluster_ip = out.stdout.decode("utf-8").split(":")[2][2:]
    return cluster_ip


def get_uk8s_env_vars():
    # This currently adds no env. variables, but we leave it just in case
    shell_env = copy(environ)
    return shell_env


def get_uk8s_kubectl_cmd():
    return "microk8s kubectl --kubeconfig={}".format(UK8S_KUBECONFIG_FILE)
