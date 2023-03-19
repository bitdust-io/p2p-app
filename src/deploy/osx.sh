#!/bin/sh

# TODO: check "appdata" file and detect location of $ROOT_DIR if it is there

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

ROOT_DIR="$HOME/.bitdust"
LOG_FILE="${ROOT_DIR}/install.log"
SOURCE_DIR="${ROOT_DIR}/src"
VENV_DIR="${ROOT_DIR}/venv"
BITDUST_PY="${SOURCE_DIR}/bitdust.py"
BITDUST_COMMAND_FILE="${ROOT_DIR}/bitdust"
GLOBAL_COMMAND_LOCATION="/usr/local/bin"
GLOBAL_COMMAND_FILE="${GLOBAL_COMMAND_LOCATION}/bitdust"
PYTHON_BIN="${ROOT_DIR}/python/bin/python3.10"
PYTHON_VENV_BIN="${ROOT_DIR}/venv/bin/python3"
PIP_VENV_BIN="${ROOT_DIR}/venv/bin/pip"


if [[ "$1" == "stop" ]]; then
    echo ''
    echo '##### stopping application'
    $PYTHON_VENV_BIN $BITDUST_PY stop
    echo ''
    echo '##### done'
    exit 0;
fi


if [[ "$1" == "restart" ]]; then
    echo ''
    echo '##### restarting application'
    $PYTHON_VENV_BIN $BITDUST_PY restart
    echo ''
    echo '##### done'
    exit 0;
fi


if [[ "$1" == "redeploy" ]]; then
    echo ''
    echo '##### cleanup local application data'
    rm -rf $ROOT_DIR/venv
    rm -rf $ROOT_DIR/src
    rm -rf $ROOT_DIR/temp
    echo ''
    echo 'cleanup DONE'
fi


if [[ ! -e $ROOT_DIR ]]; then
    echo ''
    echo "##### creating home folder"
    mkdir -p $ROOT_DIR
else
    echo ''
    echo "##### home folder found locally"
fi


cd "$ROOT_DIR"

if [[ ! -e $SOURCE_DIR ]]; then
    echo ''
    echo "##### downloading source code files from Git repository"
    mkdir -p "$SOURCE_DIR"

    if [[ ! -f $PYTHON_VENV_BIN ]]; then
        echo ''
        echo "##### creating Python virtual environment"
        $PYTHON_BIN -m venv $VENV_DIR
        $PIP_VENV_BIN install -q --upgrade pip || (echo "pip upgrade failed" && exit 1)
    fi

    # $PYTHON_BIN -m pip install -q pygit2
    $PYTHON_BIN -c "import pygit2; pygit2.clone_repository('https://github.com/bitdust-io/public.git', '$SOURCE_DIR')" || (echo "git clone failed" && exit 1)
    # $GIT_BIN clone --depth=1 "git://github.com/bitdust-io/public.git" "$SOURCE_DIR"
else
    # echo ''
    # echo "##### BitDust source files already cloned locally"
    # cd "$SOURCE_DIR"
    echo ''
    echo "##### updating source files from Git repository"

    if [[ ! -f $PYTHON_VENV_BIN ]]; then
        echo ''
        echo "##### creating Python virtual environment"
        $PYTHON_BIN -m venv $VENV_DIR
        $PIP_VENV_BIN install -q --upgrade pip || (echo "pip upgrade failed" && exit 1)
    fi

    # $PYTHON_BIN -m pip install -q pygit2
    $PYTHON_BIN -c "import pygit2; repo=pygit2.init_repository('$SOURCE_DIR'); repo.remotes[0].fetch(); top=repo.lookup_reference('refs/remotes/origin/master').target; repo.reset(top, pygit2.GIT_RESET_HARD);" || (echo "git fetch & reset failed" && exit 1)
    # $GIT_BIN fetch --all
    # echo ''
    # echo "##### Refreshing BitDust source files"
    # $GIT_BIN reset --hard origin/master
    # cd ..
fi


if [[ ! -e $PIP_VENV_BIN ]]; then
    echo ''
    echo "##### installing Python packages"
    # $PYTHON_BIN $BITDUST_PY install
    $PIP_VENV_BIN --default-timeout=10 install -U -q -r "$SOURCE_DIR/requirements.txt" || (echo "pip requirements install failed" && exit 1)
    echo "#!/bin/sh" > $BITDUST_COMMAND_FILE
    echo "$PYTHON_VENV_BIN $ROOT_DIR/src/bitdust.py \"\$@\"" >> $BITDUST_COMMAND_FILE
    chmod +x $BITDUST_COMMAND_FILE
else
    # TODO: this is slow and can fail if user is offline...
    # this actually must be only executed when requirements.txt was changed
    echo ''
    echo "##### updating Python packages"
    $PIP_VENV_BIN --default-timeout=10 install -U -q -r "$SOURCE_DIR/requirements.txt" || (echo "pip requirements install failed" && exit 1)
    echo "#!/bin/sh" > $BITDUST_COMMAND_FILE
    echo "$PYTHON_VENV_BIN $ROOT_DIR/src/bitdust.py \"\$@\"" >> $BITDUST_COMMAND_FILE
    chmod +x $BITDUST_COMMAND_FILE
fi


echo ''
echo '##### starting main process in background'
# $BITDUST_COMMAND_FILE daemon
$PYTHON_VENV_BIN $BITDUST_PY daemon


echo ''
echo '##### ready'

exit 0
