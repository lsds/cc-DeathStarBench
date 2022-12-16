# Confidential Hotel Reservation

This repository contains a port of the hotel reservation benchmark in the
[DeathStarBench](https://github.com/delimitrou/DeathStarBench) to run
confidential computing workloads.

The code in this repository has only been tested on Ubuntu 18.04 and 20.04
machines. Even though all the build and development environments are packaged
in containers, it is not guaranteed to work elsewhere. The only dependencies
are `python3.8`, `docker`, and `docker compose` (not `docker-compose`).

In addition, this code assumes you are using a kernel version `5.11` or higher.

## Quick Start

Before you start, make sure you have access to Intel's private Harbour registry.
See the [Docker docs](./docs/docker.md) for more details.

Then, to start the mesh do in `docker compose` do:

```bash
source ./bin/workon.sh
inv deploy.compose [--runtime=native,ego,ego-sim,gramine]
```

By default, the service mesh uses the `native` runtime.

You can check that all the containers are running by typing:

```bash
# All containers should be in `running` state
docker compose ps -a
```

Now you can, run the end-to-end tests:

```bash
docker compose exec cli bash -c 'source venv/bin/activate && inv tests.e2e'
```

And print the logs in the `frontend` container to ensure that the requests are
being processed:

```bash
docker compose logs frontend
```

## Docs

For further information, check the relevant documentation page:
* [Benchmarks](./bench/README.md) - running benchmarks.
* [Consul](./docs/consul.md) - notes on Consul's configuration.
* [Development](./docs/development.md) - developing in the project.
* [Docker](./docs/docker.md) - building the docker images.
* [Endpoints](./docs/endpoints.md) - information on the different endpoints and
the microservice graph.
* [K8s](./docs/k8s.md) - instructions to deploy on a kubernetes cluster.
  exposed by the mesh, and the dependency graph.
* [Releases](./docs/releases.md) - releasing and tagging code versions.
