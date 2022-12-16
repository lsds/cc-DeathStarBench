## Marblerun

We use include Marblerun as a confidential service mesh. It is also possible to enable consul and marblerun in a deployment by using:


```bash
source ./bin/workon.sh
inv deploy.compose --runtime=ego-sim --enable-consul on --enable-marbles on
```

To disable Marblerun restart the microservices by using:


```bash
source ./bin/workon.sh
inv deploy.compose --runtime=ego-sim --enable-consul on --enable-marbles off
```

The script starts the coordinator and loads the [manifest](../marblerun-manifests) where the microservices are enabled as marbles. [Transparent TLS](https://docs.edgeless.systems/marblerun/#/workflows/define-manifest?id=tls) feature is not yet available with Gramine runtime. It is possible to customize the marblerun manifest and restart the deployment. This means that elevating the connection to TLS between the microservices and database likes mongodb and memcached is not possible because they run in a Gramine enclave.