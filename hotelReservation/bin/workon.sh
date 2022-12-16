#!/bin/bash

# NOTE - this is primary designed to be run inside the cli Docker container

# ----------------------------
# Container-specific settings
# ----------------------------

MODE="undetected"
if [[ -z "$DSB_DOCKER" ]]; then
    THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
    PROJ_ROOT="${THIS_DIR}/.."
    VENV_PATH="${PROJ_ROOT}/venv-bm"

    # Normal terminal
    MODE="terminal"
else
    # Running inside the container, we know the project root
    PROJ_ROOT="/code/DeathStarBench/hotelReservation"
    VENV_PATH="${PROJ_ROOT}/venv"

	# Container mode
    MODE="container"
fi

pushd ${PROJ_ROOT} >> /dev/null

# ----------------------------
# Virtualenv
# ----------------------------

if [ ! -d ${VENV_PATH} ]; then
    ${PROJ_ROOT}/bin/create_venv.sh
fi

export VIRTUAL_ENV_DISABLE_PROMPT=1
source ${VENV_PATH}/bin/activate

# ----------------------------
# Invoke tab-completion
# (http://docs.pyinvoke.org/en/stable/invoke.html#shell-tab-completion)
# ----------------------------

_complete_invoke() {
    local candidates
    candidates=`invoke --complete -- ${COMP_WORDS[*]}`
    COMPREPLY=( $(compgen -W "${candidates}" -- $2) )
}

# If running from zsh, run autoload for tab completion
if [ "$(ps -o comm= -p $$)" = "zsh" ]; then
    autoload bashcompinit
    bashcompinit
fi
complete -F _complete_invoke -o default invoke inv

# ----------------------------
# Environment vars
# ----------------------------

# Related to building outside a container
VERSION_FILE=${PROJ_ROOT}/VERSION
export DSB_ROOT=$(pwd)
export DSB_VERSION=$(cat ${VERSION_FILE})

# Exporting the path is necessary for development mode
export DSB_CODE_DIR=/code/DeathStarBench/hotelReservation

export PS1="(cc-dsb) $PS1"

# -----------------------------
# Splash
# -----------------------------

echo ""
echo "----------------------------------"
echo "CC-DSB CLI"
echo "Version: ${DSB_VERSION}"
echo "Project root: ${PROJ_ROOT}"
echo "Mode: ${MODE}"
echo "----------------------------------"
echo ""

popd >> /dev/null
