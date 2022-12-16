## Minikube installation

Minikube is one of the possible k8s deployment kinds we support (see the [k8s](
./docs/k8s.md) docs for more details.

To install and start the cluster run from outside the container. Note that the
installation script also installs the SGX device plugin.

```bash
source ./bin/workon.sh
inv deploy.minikube.install
```

To troubleshoot the cluster you can always start and stop it again:

```bash
inv deploy.minikube.delete
inv deploy.minikube.start
```

To overwrite the installation you can install `minikube` again using:

```bash
inv deploy.minikube.install
```
