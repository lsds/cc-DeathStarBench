from invoke import task
from os import environ
from time import time
from tasks.deploy.utils.compose import get_consul_ui_port_string
from tasks.utils.sgx import get_sgx_device_mount_path
from tasks.utils.config import write_config_file
from tasks.env import DOCKER_PROJ_ROOT, PROJ_ROOT
from subprocess import run, Popen, PIPE


def get_docker_env(runtime="native", enable_consul="on", enable_marbles="on"):
    # We manually prepend environment variables instead of inheriting the shell
    # environment to have more control over the execution environment and
    # prevent things like the proxy config to be leaked in
    docker_env = {}
    docker_env["DSB_CODE_DIR"] = DOCKER_PROJ_ROOT
    docker_env["ENABLE_MARBLES"] = enable_marbles
    docker_env["ENABLE_CONSUL"] = enable_consul
    docker_env["CONSUL_UI_PORT_STRING"] = get_consul_ui_port_string()
    if runtime in ["native", "ego", "ego-sim", "gramine"]:
        docker_env["USERVICE_RUNTIME"] = runtime
    else:
        print("Unrecognised u-service runtime: {}".format(runtime))
        raise RuntimeError("Unrecognised uservice runtime")
    if runtime == "ego" or runtime == "gramine":
        (
            docker_env["SGX_DEVICE_PATH"],
            docker_env["SGX_PROVISION_DEVICE_PATH"],
        ) = get_sgx_device_mount_path()
    if "COMPOSE_PROJECT_NAME" in environ:
        docker_env["COMPOSE_PROJECT_NAME"] = environ["COMPOSE_PROJECT_NAME"]
    return docker_env


@task(default=True)
def deploy(ctx, runtime="native", enable_consul="off", enable_marbles="off"):
    """
    Start the microservice mesh: Options --runtime, --enable_consul, --enable_marbles
    """
    docker_env = get_docker_env(runtime, enable_consul, enable_marbles)
    if enable_marbles == "on":

        # Start the coordinator
        docker_cmd = "docker compose up -d coordinator"
        run(
            docker_cmd,
            shell=True,
            check=True,
            cwd=PROJ_ROOT,
            env=docker_env,
        )

        # Wait for coordinator to start
        #     wait_for_server("localhost", 4433, 10)
        docker_cmd = "sleep 3"
        print(docker_cmd)
        run(
            docker_cmd,
            shell=True,
            check=True,
            cwd=PROJ_ROOT,
            env=docker_env,
        )
        # Upload the manifest
        docker_cmd = "curl -k --data-binary @marblerun-manifests/coordinator-manifest.json https://localhost:4433/manifest"
        print(docker_cmd)
        run(
            docker_cmd,
            shell=True,
            check=True,
            cwd=PROJ_ROOT,
            env=docker_env,
        )

    docker_cmd = "docker compose up -d frontend cli"
    print(docker_cmd)
    run(
        docker_cmd,
        shell=True,
        check=True,
        cwd=PROJ_ROOT,
        env=docker_env,
    )

    ini_file(ctx, runtime)


def wait_for_server(host, port, timeout):
    stop = time() + max(0.0, timeout)
    while True:
        if is_port_in_use(port):
            break
        if time() > stop:
            raise ConnectionTimeoutError(
                "Timeout after {:.1f} seconds. Could not connect to {}:{}".format(
                    timeout, host, port
                )
            )


def is_port_in_use(port):
    """
    Checks whether the network port is in use.
    """

    cmd = ["netstat", "-an"]
    p = Popen(cmd, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    if err:
        raise RuntimeError(err.decode(errors="ignore"))
    return out.find(b":%d " % port) > 0


@task
def delete(ctx):
    """
    Stop (and remove) the microservice mesh
    """
    docker_cmd = "docker compose down -v"
    docker_env = get_docker_env()
    print(docker_cmd)
    run(docker_cmd, shell=True, check=True, cwd=PROJ_ROOT, env=docker_env)


@task
def restart(ctx, dbs=False):
    """
    Restart all the services with user-defined logic
    """
    if dbs:
        service_list = [
            "memcached-profile",
            "memcached-rate",
            "memcached-reservation",
            "mongodb-geo",
            "mongodb-profile",
            "mongodb-rate",
            "mongodb-recommendation",
            "mongodb-reservation",
            "mongodb-user",
        ]
    else:
        service_list = [
            "frontend",
            "geo",
            "profile",
            "rate",
            "recommendation",
            "reservation",
            "search",
            "user",
            "coordinator",
        ]

    docker_cmd = "docker compose restart {}".format(" ".join(service_list))
    docker_env = get_docker_env()
    print(docker_cmd)
    run(docker_cmd, shell=True, check=True, cwd=PROJ_ROOT, env=docker_env)


@task
def ini_file(ctx, runtime):
    """
    Set-up ini file for a compose deployment
    """
    write_config_file(
        {
            "kind": "compose",
            "k8s_namespace": "foo-bar",
            "frontend_host": "frontend",
            "frontend_port": 5000,
            "runtime": runtime,
        }
    )
