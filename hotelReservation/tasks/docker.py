#!/usr/bin/python3
from invoke import task
from os.path import join
from subprocess import run
from tasks.env import (
    DOCKER_ROOT,
    DOCKER_USER,
    PROJ_ROOT,
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
    Targets: 'base', 'consul', 'dsb', 'memcached', 'mongo', and all
    """
    # consul_version = "1.13.1"
    # envoy_version = "1.23.1"
    consul_version = "1.12.3"
    envoy_version = "1.23.0"
    gramine_version = "1.3.1"
    ego_version = "1.0.0"
    mongo_version = "6.0.3"

    if "all" in target:
        target = list(TARGET_2_FILE.keys())

    for t in target:
        _validate_target(t)
        file_name = TARGET_2_FILE[t]
        build_args = {}
        if t == "dsb" or t == "cli":
            build_args["DSB_VERSION"] = get_version()
        elif t == "mongo" or t == "memcached" or t == "root":
            build_args["CONSUL_VERSION"] = consul_version
            build_args["ENVOY_VERSION"] = envoy_version
            build_args["GRAMINE_VERSION"] = gramine_version
            if t == "memcached":
                build_args["MEMCACHED_VERSION"] = "1.6.17"
            if t == "mongo":
                build_args["MONGO_VERSION"] = mongo_version
        elif t == "consul":
            build_args["CONSUL_VERSION"] = consul_version
        elif t == "root":
            build_args["CONSUL_VERSION"] = consul_version
            build_args["ENVOY_VERSION"] = envoy_version
            build_args["EGO_VERSION"] = ego_version
            build_args["GRAMINE_VERSION"] = gramine_version
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
        env = {}
        env["DOCKER_BUILDKIT"] = "1"

        cmd = " ".join(cmd)
        print(cmd)
        run(cmd, shell=True, check=True, env=env, cwd=PROJ_ROOT)

        if push:
            push_image(tag)


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
