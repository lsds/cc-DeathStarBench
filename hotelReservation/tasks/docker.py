#!/usr/bin/python3
from invoke import task
from os.path import join
from subprocess import run
from tasks.env import (
    DOCKER_REGISTRY_URL,
    DOCKER_ROOT,
    DOCKER_USER,
    PROJ_ROOT,
    PROXY_ENV_VARS,
    get_version,
)

# The order of the keys matters to ensure that build_all works
TARGET_2_FILE = {
    "consul": "consul",
    "memcached": "memcached",
    "mongo": "mongo",
    "root": "sof_root",
    "base": "base",
    "cli": "cli",
    "dsb": "dsb",
}


def _validate_target(target):
    """
    Validate that the given target is a valid one
    """
    if target not in TARGET_2_FILE:
        print("Unrecognised docker image target: {}".format(target))
        print("Valid targets are: {}".TARGET_2_FILE.keys())
        raise RuntimeError("Unrecognised docker image target")


def get_tag_from_file_name(file_name):
    """
    Get the image tag from the Dockerfile's file name
    """
    return "{}/{}:{}".format(DOCKER_USER, file_name, get_version())


def get_out_file_name_from_tag(tag):
    """
    Get the archived image file name from a tag
    """
    return "{}.{}.tar.gz".format(
        tag.split("/")[1].split(":")[0], tag.split(":")[1]
    )


@task(default=True, iterable=["target"])
def build(ctx, target, version=None, nocache=False, push=False):
    """
    Build docker container.
    Targets: 'base', 'consul', 'dsb', 'memcached', and 'mongo'
    """
    # consul_version = "1.13.1"
    # envoy_version = "1.23.1"
    consul_version = "1.12.3"
    envoy_version = "1.23.0"

    for t in target:
        _validate_target(t)
        file_name = TARGET_2_FILE[t]
        build_args = {}
        if t == "dsb" or t == "cli":
            build_args["DSB_VERSION"] = get_version()
        elif t == "mongo" or t == "memcached" or t == "root":
            build_args["CONSUL_VERSION"] = consul_version
            build_args["ENVOY_VERSION"] = envoy_version
            build_args["GRAMINE_VERSION"] = "1.2"
            if t == "memcached":
                build_args["MEMCACHED_VERSION"] = "1.6.17"
            if t == "mongo":
                build_args["MONGO_VERSION"] = "6.0.0"
        elif t == "consul":
            build_args["CONSUL_VERSION"] = consul_version
        tag = get_tag_from_file_name(file_name)
        cmd = [
            "docker",
            "build",
            "--no-cache" if nocache else "",
            "-t {}".format(tag),
            "{}".format(
                " ".join(
                    [
                        "--build-arg {}={}".format(arg, build_args[arg])
                        for arg in build_args
                    ]
                )
            ),
            "-f {}/{}.dockerfile".format(DOCKER_ROOT, file_name),
            ".",
        ]

        # Set environemnt variables
        env = PROXY_ENV_VARS
        env["DOCKER_BUILDKIT"] = "1"

        cmd = " ".join(cmd)
        print(cmd)
        run(cmd, shell=True, check=True, env=env, cwd=PROJ_ROOT)

        # Tag the image irrespective of wether we push or not
        registry_tag = join(DOCKER_REGISTRY_URL, tag)
        tag_cmd = "docker tag {} {}".format(tag, registry_tag)
        print(tag_cmd)
        run(tag_cmd, shell=True, check=True)

        if push:
            push_image(registry_tag)


def push_image(tag, extra_env=None):
    """
    Push image to an image registry
    """
    push_cmd = "docker push {}".format(tag)
    print(push_cmd)
    if extra_env:
        run(push_cmd, shell=True, check=True, env=extra_env)
    else:
        run(push_cmd, shell=True, check=True)


@task
def build_all(ctx, nocache=False, push=False):
    """
    Build all work-on containers
    """
    print("Building all targets: {}".format(TARGET_2_FILE.keys()))
    build(ctx, list(TARGET_2_FILE.keys()), nocache, push)
