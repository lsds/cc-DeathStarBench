## Deploying on a Kubernetes cluster

To interact with a running k8s cluster (or to install/remove it) you will need
to operate from _outside_ the container, and with the virtual environment
activated (i.e. `source ./bin/workon.sh`).

### Installation

You will first have to install the `kubectl` tool. From outside the container
do:

```bash
source ./bin/workon.sh

inv deploy.k8s.install-kubectl --system
```

The configuration of the actual k8s cluster will depend on the `kind` of
deployment you are using. We currently support microk8s (`uk8s`) and minikube
(`minikube`). For the particular installation details check the respective doc:
* [Microk8s (`uk8s`)](./docs/uk8s.md) - for local single-node clusters with microk8s.
* [Minikube (`minikube`)](./docs/minikube.md) - for local single-node clusters with minikube.

### Post-installation

You may also want to install the `k9s` monitoring tool to quickly control and
access the cluster. From outside the container do:

```bash
inv deploy.k9s.install --system
```

To run `k9s`, you will have to add some variables to your environment. To
get a direct shell in the cluster do:

```bash
eval $(inv deploy.k9s.get-cmd --kind [uk8s,minikube])
```

### Deployment

To deploy the microservice mesh on the cluster you need to specify the kind
of k8s cluster you will run on. For the moment, `uk8s` and `minikube` are valid
options.

```bash
inv deploy.k8s --kind [uk8s,minikube]
```

You may also want to deploy the cluster in a different namespace. You
can do it by setting the env. variable `DSB_K8S_NAMESPACE`.

After this, you should be able to run the tests normally:

```bash
inv tests.e2e
```

Note that this relies on the config file `dsb.ini` being generated succesfully.
You may force its re-generation by running:

```bash
inv deploy.k8s.ini-file --kind [uk8s,minikube]
```

Lastly, to remove the cluster run:

```bash
inv deploy.k8s.delete
```

The script will pick up the details in the config file. But if deployment
has failed (so ini file has not been re-generated) you can provide the kind
and namespace manually:

```bash
inv deploy.k8s.delete --kind [uk8s,minikube] --namespace <namespace>
```
