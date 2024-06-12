#!/bin/bash
SCRIPT_PATH="${BASH_SOURCE[0]}";

if([ -h "${SCRIPT_PATH}" ]) then
  while([ -h "${SCRIPT_PATH}" ]) do SCRIPT_PATH=`readlink "${SCRIPT_PATH}"`; done
fi
SCRIPT_PATH="$(dirname ${SCRIPT_PATH})"

# Get absolute path for SCRIPT_PATH
ABS_SCRIPT_PATH=$(cd "${SCRIPT_PATH}" && pwd)

ROOT_DIR="$HOME/.bitdust"
SOURCE_UI_DIR="${ROOT_DIR}/ui"
GIT_PATH="${ROOT_DIR}/git_scm"
MAIN_PY_PATH="${ROOT_DIR}/ui/src/main.py"
PYTHON_BIN_LINK_PATH="${ROOT_DIR}/bitdust-p2p-app"
GIT_BIN="${GIT_PATH}/git/bin/git"

export GIT_EXEC_PATH="${GIT_PATH}/git/libexec/git-core"
export GIT_TEMPLATE_DIR="${GIT_PATH}/git/share/git-core/templates"
export GIT_CONFIG_NOSYSTEM=1

if [ ! -e "${ROOT_DIR}" ]; then
    mkdir -p $ROOT_DIR
fi

if [ ! -e "${GIT_PATH}" ]; then
    cp -R "${ABS_SCRIPT_PATH}/git_scm" "${ROOT_DIR}"
fi

if [ ! -f "${MAIN_PY_PATH}" ]; then
    ${GIT_BIN} clone --single-branch --branch master --depth=1 https://github.com/bitdust-io/p2p-app.git "${ROOT_DIR}/ui" 1>"${ROOT_DIR}/git_scm_out.txt" 2>"${ROOT_DIR}/git_scm_err.txt"
else
    ${GIT_BIN} -C "${ROOT_DIR}/ui" fetch --all 1>"${ROOT_DIR}/git_scm_out.txt" 2>"${ROOT_DIR}/git_scm_err.txt" && ${GIT_BIN} -C "${ROOT_DIR}/ui" reset --hard origin/master 1>>"${ROOT_DIR}/git_scm_out.txt" 2>>"${ROOT_DIR}/git_scm_err.txt"
fi

# activate the virtualenv
pushd "${SCRIPT_PATH}/venv/bin"
# must be in current directory
source activate

# setup the environment to not mess with the system
export DYLD_FALLBACK_LIBRARY_PATH="${SCRIPT_PATH}/../lib:$DYLD_FALLBACK_LIBRARY_PATH"
export LD_PRELOAD_PATH="${SCRIPT_PATH}/../lib"
BUNDLE_ID=$(osascript -e 'id of app "../../../../"')
# We are not allowed to edit anything within the .app for security reasons.
export KIVY_HOME="~/Library/Application Support/$BUNDLE_ID"
export PYTHONHOME="${ABS_SCRIPT_PATH}/python3"

if [ -d "${ROOT_DIR}/ui/src" ]; then
  cd "${ROOT_DIR}/ui/src"
  exec "python" -m main "$@"

# default drag & drop support
elif [ $# -ne 0 ]; then
  exec "python" "$@"

# start a python shell, only if we didn't double-clicked
elif [ "$SHLVL" -gt 1 ]; then
  exec "python"

fi
