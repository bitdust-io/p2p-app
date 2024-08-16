#!/bin/bash

SCRIPT_PATH="${BASH_SOURCE[0]}";

if([ -h "${SCRIPT_PATH}" ]) then
  while([ -h "${SCRIPT_PATH}" ]) do SCRIPT_PATH=`readlink "${SCRIPT_PATH}"`; done
fi
SCRIPT_PATH="$(dirname ${SCRIPT_PATH})"

# Get absolute path for SCRIPT_PATH
ABS_SCRIPT_PATH=$(cd "${SCRIPT_PATH}" && pwd)

GIT_PATH="${ABS_SCRIPT_PATH}/git_scm"
GIT_BIN="${GIT_PATH}/git/bin/git"

ROOT_DIR_RELATIVE="$HOME/.bitdust"

if [ ! -e "${ROOT_DIR_RELATIVE}" ]; then
  mkdir -p $ROOT_DIR_RELATIVE
fi

ROOT_DIR=$(cd "${ROOT_DIR_RELATIVE}" && pwd)
UI_MAIN_PY_PATH="${ROOT_DIR}/ui/src/main.py"
ENGINE_DIR="${ROOT_DIR}/src"
ENGINE_VENV_DIR="${ROOT_DIR}/venv"
ENGINE_PIP_BIN="${ENGINE_VENV_DIR}/bin/pip"
ENGINE_PYTHON_BIN="${ENGINE_VENV_DIR}/bin/python"
ENGINE_PY_PATH="${ENGINE_DIR}/bitdust.py"

export GIT_EXEC_PATH="${GIT_PATH}/git/libexec/git-core"
export GIT_TEMPLATE_DIR="${GIT_PATH}/git/share/git-core/templates"
export GIT_CONFIG_NOSYSTEM=1

if [ "$1" == "deploy" ]; then
  if [ ! -f "${ENGINE_PY_PATH}" ]; then
    echo "downloading engine source code files from Git repository ..."
    ${GIT_BIN} clone --single-branch --branch master --depth=1 https://github.com/bitdust-io/public.git "${ROOT_DIR}/src" 1>"${ROOT_DIR}/git_scm_out.txt" 2>"${ROOT_DIR}/git_scm_err.txt" || echo "git clone failed"
  else
    echo "updating engine source files from Git repository ..."
    (${GIT_BIN} -C "${ROOT_DIR}/src" fetch --all 1>"${ROOT_DIR}/git_scm_out.txt" 2>"${ROOT_DIR}/git_scm_err.txt" && ${GIT_BIN} -C "${ROOT_DIR}/src" reset --hard origin/master 1>>"${ROOT_DIR}/git_scm_out.txt" 2>>"${ROOT_DIR}/git_scm_err.txt") || echo "git fetch failed"
  fi

  # setup the environment to not mess with the system
  export DYLD_FALLBACK_LIBRARY_PATH="${ROOT_DIR}/../lib:$DYLD_FALLBACK_LIBRARY_PATH"
  export LD_PRELOAD_PATH="${ROOT_DIR}/../lib"
  BUNDLE_ID=$(osascript -e 'id of app "../../../../"')
  # We are not allowed to edit anything within the .app for security reasons.
  export KIVY_HOME="~/Library/Application Support/$BUNDLE_ID"
  export PYTHONHOME="${ABS_SCRIPT_PATH}/python3"

  echo "updating Python packages ..."
  ${ENGINE_PIP_BIN} --default-timeout=10 install -q -U -r "${ENGINE_DIR}/requirements.txt" || echo "pip requirements install failed"
 
  echo 'starting engine process in background ...'
  ${ENGINE_PYTHON_BIN} "${ENGINE_PY_PATH}" daemon
  exit 0;

elif [ "$1" == "redeploy" ]; then
  rm -rf "${ROOT_DIR}/venv"
  rm -rf "${ROOT_DIR}/src"
  rm -rf "${ROOT_DIR}/temp"
  exit 0;

elif [ "$1" == "restart" ]; then
  ${ENGINE_PYTHON_BIN} "${ENGINE_PY_PATH}" restart
  exit 0;

elif [ "$1" == "stop" ]; then
  ${ENGINE_PYTHON_BIN} "${ENGINE_PY_PATH}" stop
  exit 0;
fi

if [ ! -f "${UI_MAIN_PY_PATH}" ]; then
  echo "downloading application source code files from Git repository ..."
  ${GIT_BIN} clone --single-branch --branch master --depth=1 https://github.com/bitdust-io/p2p-app.git "${ROOT_DIR}/ui" 1>"${ROOT_DIR}/git_scm_out.txt" 2>"${ROOT_DIR}/git_scm_err.txt" || echo "git clone failed"
else
  echo "updating application source files from Git repository ..."
  (${GIT_BIN} -C "${ROOT_DIR}/ui" fetch --all 1>"${ROOT_DIR}/git_scm_out.txt" 2>"${ROOT_DIR}/git_scm_err.txt" && ${GIT_BIN} -C "${ROOT_DIR}/ui" reset --hard origin/master 1>>"${ROOT_DIR}/git_scm_out.txt" 2>>"${ROOT_DIR}/git_scm_err.txt") || echo "git fetch failed"
fi

# activate the virtualenv
pushd "${SCRIPT_PATH}/venv/bin" 1>/dev/null 2>/dev/null
# must be in current directory
source activate

# setup the environment to not mess with the system
export DYLD_FALLBACK_LIBRARY_PATH="${SCRIPT_PATH}/../lib:$DYLD_FALLBACK_LIBRARY_PATH"
export LD_PRELOAD_PATH="${SCRIPT_PATH}/../lib"
BUNDLE_ID=$(osascript -e 'id of app "../../../../"')
# We are not allowed to edit anything within the .app for security reasons.
export KIVY_HOME="~/Library/Application Support/$BUNDLE_ID"
export PYTHONHOME="${ABS_SCRIPT_PATH}/python3"

if [ ! -d "${ENGINE_VENV_DIR}" ]; then
  echo "creating isolated Python environment ..."
  python -m virtualenv "${ENGINE_VENV_DIR}"
fi

echo "updating Python packages ..."
python -m pip --default-timeout=10 install -q -U -r "${ROOT_DIR}/ui/requirements.txt"
python -m pip --default-timeout=10 install -q -U "pyobjus==1.2.3"

if [ -d "${ROOT_DIR}/ui/src" ]; then
  echo "starting the application ..."
  cd "${ROOT_DIR}/ui/src"
  /usr/bin/screen -d -m python -c 'import os, sys; home_dir=os.path.join(os.environ["HOME"], ".bitdust"); os.system("python -m main 1>\"{}/app_std_out.txt\" 2>\"{}/app_std_err.txt\"".format(home_dir, home_dir));'
  sleep 2
  exit 0;

# default drag & drop support
elif [ $# -ne 0 ]; then
  exec "python" "$@"

# start a python shell, only if we didn't double-clicked
elif [ "$SHLVL" -gt 1 ]; then
  exec "python"

fi
