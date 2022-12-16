## Development

The recommended development environment for the project is the CLI container.
To access it, run:

```bash
./bin/cli.sh dsb
```

Inside the container, you can build the code for all Go services using:

```bash
inv dev.build [--runtime=all,ego,ego-sim,gramine,native] [--clean]
```

This builds it both natively and with [ego](https://github.com/edgelesssys/ego).

If you want the microservices to run the code built with EGo, you will need to
stop the containers (`inv deploy.compose.delete`) and start it again with the
`--runtime=ego` flag (`inv deploy.compose --runtime=ego`).

### Re-building a microservice

In a `docker compose` deployment, all service containers share a mount with
the built files. Thus, to update a running container, you just need to: (i)
modify the code, (ii) re-build it, and (iii) restart it using
`docker compose restart <service_name>` (outside the CLI).

If you change any of the protobuf files, run:

```bash
TODO: this still does not work
inv dev.build --proto
```

### Code formatting

The code formatting rules for the project are:
* Go: as enforced by the `gofmt` tool.
* Python: as enforced by `black` and `flake8`.
* Markdown: best-effort 80 char lines.
Go and Python formatting are checked-for as part of the CI/CD, so you will have
to submit PRs with properly formatted code. There's a script to do so, from
the CLI container run:

```bash
inv dev.format
```

### Code editors

The container ships with a configured VIM and the necessary language servers
(i.e. `gopls` and `pyls`) for code completion. If you want to use a different
editor, check its docs to see how to attach to a running container.

