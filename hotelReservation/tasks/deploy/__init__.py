from invoke import Collection

from . import compose
from . import k8s
from . import k9s
from . import minikube
from . import uk8s

ns = Collection(
    compose,
    k8s,
    k9s,
    minikube,
    uk8s,
)
