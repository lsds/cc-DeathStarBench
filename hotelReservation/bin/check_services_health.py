#!/usr/bin/python3.8
from os import environ
from requests import get
from socket import socket, AF_INET, SOCK_STREAM
from subprocess import run
from sys import argv, exit

consul_env_vars = [
    "CONSUL_HTTP_ADDR",
    "CONSUL_GRPC_ADDR",
    "CONSUL_CACERT",
    "CONSUL_CLIENT_CERT",
    "CONSUL_CLIENT_KEY",
]

# We duplicate this here for simplicity
consul_dependencies = {
    "frontend": ["profile", "search", "recommendation", "user", "reservation"],
    "geo": [],
    "profile": [],
    "rate": [],
    "recommendation": [],
    "reservation": [],
    "search": ["geo", "rate"],
    "user": [],
}
compose_services = {
    "frontend": 5000,
    "geo": 8083,
    "profile": 8081,
    "rate": 8084,
    "recommendation": 8085,
    "reservation": 8087,
    "search": 8082,
    "user": 8086,
    "memcached-profile": 11211,
    "memcached-rate": 11211,
    "memcached-reservation": 11211,
    "mongodb-geo": 27017,
    "mongodb-profile": 27017,
    "mongodb-rate": 27017,
    "mongodb-recommendation": 27017,
    "mongodb-reservation": 27017,
    "mongodb-user": 27017,
}


def check_consul_env_vars():
    """
    Check that all required Consul env. vars are defined in the shell's
    environment
    """
    for var in consul_env_vars:
        if var not in environ:
            print(
                "Consul env. var {} not defined in shell environment!".format(
                    var
                )
            )
            raise RuntimeError("Consul env. var not defined in environment")


def get_all_nodes():
    out = (
        run(
            "consul catalog nodes",
            shell=True,
            capture_output=True,
            env=environ,
        )
        .stdout.decode("utf-8")
        .split("\n")[1:]
    )
    nodes = [o.split(" ")[0] for o in out]
    return [n for n in nodes if len(n) > 0 and n not in ["consul-server"]]


def get_all_services(consul_enabled):
    if consul_enabled:
        out = (
            run(
                "consul catalog services",
                shell=True,
                capture_output=True,
                env=environ,
            )
            .stdout.decode("utf-8")
            .split("\n")
        )
        return [o for o in out if len(o) > 0 and o not in ["consul", "cli"]]
    else:
        return list(compose_services.keys())


def get_service_dependencies(service_name, consul_enabled):
    # We start with a list of the high-level service-mesh dependencies
    deps = consul_dependencies[service_name]
    all_services = get_all_services(consul_enabled)
    deps.append(service_name)
    for base_service in deps:
        # We add all the dependencies with the service name as substring like
        # side-car proxies or databases
        for service in all_services:
            if service != base_service and base_service in service:
                deps.append(service)
    deps.remove(service_name)
    return deps


def check_service_health(service_name, consul_enabled):
    if consul_enabled:
        # To check for a service's health in Consul we query the health API
        url = "{}/v1/health/checks/{}".format(
            environ["CONSUL_HTTP_ADDR"], service_name
        )
        r = get(
            url,
            cert=(environ["CONSUL_CLIENT_CERT"], environ["CONSUL_CLIENT_KEY"]),
            verify=environ["CONSUL_CACERT"],
            proxies={"no_proxy": "localhost"},
        )
        return r.json()[0]["Status"] == "passing"
    else:
        # To check for a service's health without Consul, we just check that
        # the expected IP:port tuple is accepting connections. Note that we
        # rely on Docker's internal DNS for routing
        sock = socket(AF_INET, SOCK_STREAM)
        result = sock.connect_ex(
            (service_name, compose_services[service_name])
        )
        health = result == 0
        sock.close()
        return health


def check_node_health(node_name):
    url = "{}/v1/health/node/{}".format(environ["CONSUL_HTTP_ADDR"], node_name)
    r = get(
        url,
        cert=(environ["CONSUL_CLIENT_CERT"], environ["CONSUL_CLIENT_KEY"]),
        verify=environ["CONSUL_CACERT"],
        proxies={"no_proxy": "localhost"},
    )
    return r.json()[0]["Status"] == "passing"


def check(services_to_check, consul_enabled):
    if consul_enabled:
        check_consul_env_vars()

        # First, we check for the health of all consul client nodes
        all_nodes = get_all_nodes()
        node_count = len(all_nodes)
        node_health_count = 0
        for node in all_nodes:
            node_health = check_node_health(node)
            if node_health:
                node_health_count += 1
    else:
        node_count = 0
        node_health_count = 0

    # Second, check services health
    if services_to_check == "all":
        services = get_all_services(consul_enabled)
    else:
        services = get_service_dependencies(services_to_check, consul_enabled)
    service_count = len(services)
    service_health_count = 0
    for service in services:
        service_health = check_service_health(service, consul_enabled)
        if service_health:
            service_health_count += 1

    if consul_enabled:
        print(
            "CC-DSB CONSUL HEALTH CHECK: Nodes {}/{} - Services {}/{}".format(
                node_health_count,
                node_count,
                service_health_count,
                service_count,
            )
        )
    else:
        print(
            "CC-DSB HEALTH CHECK: Services {}/{}".format(
                service_health_count,
                service_count,
            )
        )

    if service_health_count == service_count and (
        services_to_check != "all"
        or (services_to_check == "all" and node_count == node_health_count)
    ):
        exit(0)
    else:
        exit(1)


if __name__ == "__main__":
    if len(argv) > 1:
        to_check = argv[1]
    else:
        to_check = "all"
    check(to_check, environ["ENABLE_CONSUL"] == "on")
