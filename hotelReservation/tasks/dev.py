from copy import copy
from invoke import task
from os import environ, makedirs
from os.path import exists, join
from shutil import rmtree
from subprocess import run
from sys import exit
from tasks.env import (
    EGO_BUILD_DIR,
    GO_BINARY_PATH,
    GRAMINE_BUILD_DIR,
    GO_CMD_DIR,
    NATIVE_BUILD_DIR,
    PROJ_ROOT,
    PROXY_ENV_VARS,
)
from tasks.utils.ego import sign as ego_sign
from tasks.utils.gramine import sign as gramine_sign
from tasks.utils.gramine import generate_private_key as gramine_gen_private_key

service_list = [
    "frontend",
    "geo",
    "profile",
    "rate",
    "recommendation",
    "reservation",
    "search",
    "user",
]

BUILD_DETAILS = {
    "native": {
        "build_dir": NATIVE_BUILD_DIR,
        "compiler_path": join(GO_BINARY_PATH, "go"),
    },
    "ego": {
        "build_dir": EGO_BUILD_DIR,
        "compiler_path": "ego-go",
    },
    "gramine": {
        "build_dir": GRAMINE_BUILD_DIR,
        "compiler_path": "ego-go",
    },
}


@task(default=True)
def build(ctx, runtime="native", clean=False):
    """
    Build all the targets for one runtime: 'ego', 'ego-sim', 'gramine','native'
    , or 'all'
    """
    # Include proxy env. vars in case we need to fetch any dependency from the
    # internet
    shell_env = copy(environ)
    shell_env.update(PROXY_ENV_VARS)

    build_kinds = []
    if runtime in ["all", "native"]:
        build_kinds.append("native")
    # With Gramine, we first build the binary using ego-go build which uses
    # the modified go compiler that redirects syscalls to libc.
    if runtime in ["all", "gramine"]:
        build_kinds.append("gramine")
    if runtime in ["all", "ego", "ego-sim"]:
        build_kinds.append("ego")

    for kind in build_kinds:
        build_dir = BUILD_DETAILS[kind]["build_dir"]
        if exists(build_dir) and clean:
            rmtree(build_dir)
        if not exists(build_dir):
            makedirs(build_dir)
        # For a clean Gramine build, we generate a key to sign the binaries
        if kind == "gramine":
            gramine_gen_private_key(clean)

        print("Building go targets for runtime: {}".format(kind))
        for service_name in service_list:
            # For EGo builds, each service needs to be in a separate directory,
            # so we do the same for native builds to keep the same directory
            # structure
            service_path = join(build_dir, service_name)
            if not exists(service_path):
                makedirs(service_path)

            cmd = [
                "{} build".format(BUILD_DETAILS[kind]["compiler_path"]),
                "-o {}/{}".format(service_path, service_name),
                "{}/{}".format(GO_CMD_DIR, service_name),
            ]
            cmd = " ".join(cmd)
            run(cmd, shell=True, check=True, cwd=PROJ_ROOT)

            # Unlike normal go binaries, SGX binaries need to be signed
            if kind == "ego":
                ego_sign(service_name, service_path)
            if kind == "gramine":
                gramine_sign(service_name, service_path)


@task
def format(ctx, check=False):
    """
    Format Go and Python code
    """
    # Include shell environment for out-of-tree builds to find the right go
    # binary
    shell_env = copy(environ)
    shell_env.update(PROXY_ENV_VARS)

    if check:
        go_cmd = 'gofmt -l $(find . -type f -name "*.go")'
        py_cmd_black = (
            "python3 -m black --check $(find . -type f -name "
            '"*.py" -not -path "./venv/*" -not -path "./venv-bm/*")'
        )
        py_cmd_flake = (
            "python3 -m flake8 --count $(find . -type f -name "
            '"*.py" -not -path "./venv/*" -not -path "./venv-bm/*")'
        )
    else:
        go_cmd = 'gofmt -w $(find . -type f -name "*.go")'
        py_cmd_black = (
            'python3 -m black $(find . -type f -name "*.py" -not '
            '-path "./venv/*" -not -path "./venv-bm/*")'
        )
        py_cmd_flake = (
            "python3 -m flake8 --exit-zero $(find . -type f -name "
            '"*.py" -not -path "./venv/*" -not -path "./venv-bm/*")'
        )

    # Run Go formatting
    print(go_cmd)
    result = run(
        go_cmd,
        shell=True,
        check=True,
        cwd=PROJ_ROOT,
        capture_output=True,
        env=shell_env,
    )
    if check and result.stdout:
        print("Found errors checking Go formatting: {}".format(result.stdout))
        exit(1)

    # Run Python formatting. Note that running with the --check flag already
    # returns an error code if code is not adequately formatted
    print(py_cmd_black)
    run(py_cmd_black, shell=True, check=True, cwd=PROJ_ROOT)
    # Same for flake8's --count flag
    print(py_cmd_flake)
    run(py_cmd_flake, shell=True, check=True, cwd=PROJ_ROOT)
