from os.path import dirname, expanduser, join, realpath

# ---- Useful directories ----

PROJ_ROOT = dirname(dirname(realpath(__file__)))

# ----- Docker variables ----

DOCKER_CONFIG = expanduser("~/.docker/config.json")
DOCKER_PROJ_ROOT = "/code/DeathStarBench/hotelReservation"
DOCKER_ROOT = join(PROJ_ROOT, "docker")
DOCKER_USER = "ccdsb"

# ----- Go variables ----

GO_BINARY_PATH = "/usr/local/go/bin"
GO_CMD_DIR = join(PROJ_ROOT, "cmd")

# ----- Build directories ----

BASE_BUILD_DIR = join(PROJ_ROOT, "build")
EGO_BUILD_DIR = join(BASE_BUILD_DIR, "ego")
GRAMINE_BUILD_DIR = join(BASE_BUILD_DIR, "gramine")
NATIVE_BUILD_DIR = join(BASE_BUILD_DIR, "native")

# ---- Github variables ----

GH_REPO_NAME = "lsds/cc-DeathStarBench"
GH_ROOT = dirname(PROJ_ROOT)
# TODO(open-source): generate a new github token for the new repository
GH_TOKEN_PATH = join(PROJ_ROOT, "dev", "new_token_path")


def get_version():
    with open(join(PROJ_ROOT, "VERSION"), "r") as fh:
        version = fh.read()
        version = version.strip()
    return version
