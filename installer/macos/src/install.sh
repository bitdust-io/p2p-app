#!/bin/sh

# TODO: check "appdata" file and detect location of $ROOT_DIR if it is there

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

echo "CURRENT_DIR: ${CURRENT_DIR}"

ROOT_DIR="$HOME/.bitdust"

echo "ROOT_DIR: ${ROOT_DIR}"


LOG_FILE="${ROOT_DIR}/install.log"

SOURCE_DIR="${ROOT_DIR}/src"
VENV_DIR="${ROOT_DIR}/venv"

BITDUST_PY="${SOURCE_DIR}/bitdust.py"
BITDUST_COMMAND_FILE="${ROOT_DIR}/bitdust"


PYTHON_BIN="$1"

if [[ ! -f $PYTHON_BIN ]]; then
    PYTHON_BIN="${ROOT_DIR}/python/bin/BitDust-p2p-app"
    PYTHON_VENV_BIN="${ROOT_DIR}/venv/bin/BitDust-node"
fi

if [[ ! -f $PYTHON_BIN ]]; then
    PYTHON_BIN="python3"
    PYTHON_VENV_BIN="${ROOT_DIR}/venv/bin/python3"
fi

PIP_VENV_BIN="${ROOT_DIR}/venv/bin/pip"

echo "PYTHON_BIN: ${PYTHON_BIN}"


GIT_BIN="$2"

if [[ ! -f $GIT_BIN ]]; then
    GIT_BIN="${CURRENT_DIR}/git_scm/bin/git"
fi

echo "GIT_BIN: ${GIT_BIN}"




if [[ "$1" == "stop" ]]; then
    echo ''
    echo '### stopping application'
    $PYTHON_VENV_BIN $BITDUST_PY stop
    echo ''
    echo '### done'
    exit 0;
fi


if [[ "$1" == "restart" ]]; then
    echo ''
    echo '### restarting application'
    $PYTHON_VENV_BIN $BITDUST_PY restart
    echo ''
    echo '### done'
    exit 0;
fi


if [[ "$1" == "redeploy" ]]; then
    echo ''
    echo '### cleanup local application data'
    rm -rf $ROOT_DIR/venv
    rm -rf $ROOT_DIR/src
    rm -rf $ROOT_DIR/temp
    echo ''
    echo 'cleanup DONE'
fi


if [[ ! -e $ROOT_DIR ]]; then
    echo ''
    echo "### creating home folder"
    mkdir -p $ROOT_DIR
else
    echo ''
    echo "### home folder found locally"
fi


cd "$ROOT_DIR"

if [[ ! -e $SOURCE_DIR ]]; then

    if [[ ! -f $BITDUST_COMMAND_FILE ]]; then
        echo ''
        echo "### downloading source code files from Git repository"
        mkdir -p "$SOURCE_DIR"

        if [[ ! -f $PYTHON_VENV_BIN ]]; then
            echo ''
            echo "### creating Python virtual environment"
            $PYTHON_BIN -m venv --clear --copies $VENV_DIR
            cp "${ROOT_DIR}/venv/bin/python3" "${PYTHON_VENV_BIN}"
            $PIP_VENV_BIN install -q --upgrade pip || (echo "pip upgrade failed" && exit 1)
        fi

        $GIT_BIN clone git@github.com:bitdust-io/public.git src 1>"${ROOT_DIR}/git_scm_out.txt" 2>"${ROOT_DIR}/git_scm_err.txt" || (echo "git clone failed" && exit 1)
    fi

else
    echo ''
    echo "### updating source files from Git repository"

    if [[ ! -f $PYTHON_VENV_BIN ]]; then
        echo ''
        echo "### creating Python virtual environment"
        $PYTHON_BIN -m venv --clear --copies $VENV_DIR
        cp "${ROOT_DIR}/venv/bin/python3" "${PYTHON_VENV_BIN}"
        $PIP_VENV_BIN install -q --upgrade pip || (echo "pip upgrade failed" && exit 1)
    fi

    cd src
    ($GIT_BIN fetch --all 1>"${ROOT_DIR}/git_scm_out.txt" 2>"${ROOT_DIR}/git_scm_err.txt" && $GIT_BIN reset --hard origin/master 1>>"${ROOT_DIR}/git_scm_out.txt" 2>>"${ROOT_DIR}/git_scm_err.txt") || (echo "git fetch & reset failed" && exit 1)
    cd ..
fi


if [[ ! -e $PIP_VENV_BIN ]]; then
    echo ''
else
    # TODO: this is slow and can fail if user is offline...
    # this actually must be only executed when requirements.txt was changed
    if [[ -f $SOURCE_DIR/requirements.txt ]]; then
        echo ''
        echo "### updating Python packages"
        $PIP_VENV_BIN --default-timeout=10 install -U -q -r "$SOURCE_DIR/requirements.txt" || (echo "pip requirements install failed" && exit 1)
    fi
fi


echo ''
echo '### starting main process in background'

if [[ ! -f $BITDUST_COMMAND_FILE ]]; then
    $PYTHON_VENV_BIN $BITDUST_PY daemon
else
    $BITDUST_COMMAND_FILE daemon
fi


echo ''
echo '### ready'

exit 0
