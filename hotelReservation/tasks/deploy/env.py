from os.path import join
from tasks.env import PROJ_ROOT

DEPLOY_DIR = join(PROJ_ROOT, "deploy")

# ----- Binary installations -----

BIN_DIR = join(DEPLOY_DIR, "bin")
GLOBAL_BIN_DIR = "/usr/local/bin"
KUBECTL_BIN = join(BIN_DIR, "kubectl")

# ----- Software versions -----

K8S_VERSION = "1.24.2"
K9S_VERSION = "0.26.3"
MINIKUBE_VERSION = "1.26.0"

# ----- K8s files -----

K8S_FILES_DIR = join(DEPLOY_DIR, "k8s")
K8S_INGRESS_FILE = join(K8S_FILES_DIR, "ingress.yaml.j2")
K8S_NAMESPACE_FILE = join(K8S_FILES_DIR, "namespace.yaml.j2")
K8S_NODE_PORT_FILE = join(K8S_FILES_DIR, "frontend_node_port.yaml.j2")
K8S_REGISTRY_SECRET_NAME = "intel-registry-cred"
K8S_SERVICE_DIRS = [
    join(K8S_FILES_DIR, "frontend"),
    join(K8S_FILES_DIR, "geo"),
    join(K8S_FILES_DIR, "profile"),
    join(K8S_FILES_DIR, "rate"),
    join(K8S_FILES_DIR, "recommendation"),
    join(K8S_FILES_DIR, "reservation"),
    join(K8S_FILES_DIR, "search"),
    join(K8S_FILES_DIR, "user"),
]
K8S_TEMPLATED_DIR = join(K8S_FILES_DIR, "templated")

K8S_DEFAULT_NAMESPACE = "dsb"
