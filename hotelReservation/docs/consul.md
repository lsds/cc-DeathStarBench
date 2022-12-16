## Consul configuration

We use Consul as our service mesh. Consul is better suited for `k8s` deployments
but we also make the effort to run it in `docker compose`. The idea is to have
the same microservice code run on the same type of Consul infrastructure
regardless of the deployment kind.

We also use Envoy as our side-car proxy. In a `docker compose` setting, the
sidecar runs as a different process in the same container the microservice does.

To access the Consul UI, open your browser and navigate to `localhost:8501`. It
will complain about certificates, but just ignore the warnings

To disable Consul, you can deploy the application with the `--enable-consul`
flag disabled:

```bash
source ./bin/workon.sh
inv deploy.compose --enable-consul off
```

### Consul's Security

Our Consul configuration automatically handles TLS connections between side-car
proxies, and access control through service intentions. You can inspect the
[configuration files](./../consul/config) for further details.
