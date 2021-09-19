#!/bin/sh

ROOT_DIR="$HOME/.bitdust"
LOG_FILE="${ROOT_DIR}/venv.log"
SOURCE_DIR="${ROOT_DIR}/src"
VENV_DIR="${ROOT_DIR}/venv"
PYTHON_BIN="${ROOT_DIR}/venv/bin/python"
PIP_BIN="${ROOT_DIR}/venv/bin/pip"
BITDUST_PY="${SOURCE_DIR}/bitdust.py"
BITDUST_COMMAND_FILE="${ROOT_DIR}/bitdust"
GLOBAL_COMMAND_LOCATION="/usr/local/bin"
GLOBAL_COMMAND_FILE="${GLOBAL_COMMAND_LOCATION}/bitdust"


if [ "$1" = "stop" ]; then
    echo ''
    echo '##### stopping application'
    $PYTHON_BIN $BITDUST_PY stop
    echo ''
    echo '##### done'
    exit 0;
fi


if [ "$1" = "restart" ]; then
    echo ''
    echo '##### restarting application'
    $PYTHON_BIN $BITDUST_PY restart
    echo ''
    echo '##### done'
    exit 0;
fi


if [ "$1" = "redeploy" ]; then
    echo ''
    echo '##### cleanup local application data'
    rm -rf $ROOT_DIR/venv
    rm -rf $ROOT_DIR/src
    rm -rf $ROOT_DIR/identitycache
    rm -rf $ROOT_DIR/identityhistory
    rm -rf $ROOT_DIR/temp
    echo ''
    echo 'cleanup DONE'
fi


if [ ! -d $ROOT_DIR ]; then
    echo ''
    echo "##### creating home folder"
    mkdir -p $ROOT_DIR
else
    echo ''
    echo "##### home folder found locally"
fi


cd "$ROOT_DIR"


if [ ! -d $SOURCE_DIR ]; then
    echo ''
    echo "##### downloading source code files from Git repository"
    mkdir -p $SOURCE_DIR
    git clone --depth=1 https://github.com/bitdust-io/devel.git $SOURCE_DIR
    # git clone --depth=1 https://github.com/bitdust-io/public.git $SOURCE_DIR
else
    echo ''
    echo "##### source files already cloned locally"
    cd "$SOURCE_DIR"
    echo ''
    echo "##### updating source files from Git repository"
    git fetch --all
    echo ''
    echo "##### refreshing source code"
    git reset --hard origin/master
    cd ..
fi


if [ ! -f $PIP_BIN ]; then
    echo ''
    echo "##### preparing Python virtual environment"
    python3 $BITDUST_PY install  1>$LOG_FILE 2>$LOG_FILE
else
    # TODO: this is slow and can fail if user is offline...
    # this actually must be only executed when requirements.txt was changed
    echo ''
    echo "##### updating Python virtual environment"
    $PIP_BIN install -U -r $SOURCE_DIR/requirements.txt  1>$LOG_FILE 2>$LOG_FILE
fi

if [ -w $GLOBAL_COMMAND_LOCATION ]; then
    echo ''
    echo "##### create system-wide command line alias"
    ln -s -f $BITDUST_COMMAND_FILE $GLOBAL_COMMAND_FILE
fi

if [ -w $GLOBAL_COMMAND_LOCATION ]; then
    if [ ! -f $GLOBAL_COMMAND_FILE ]; then
        echo ''
        echo "##### create system-wide shell command"
        ln -s -f $BITDUST_COMMAND_FILE $GLOBAL_COMMAND_FILE
    fi
fi


echo ''
echo '##### starting main process in background'
if [ -f $GLOBAL_COMMAND_FILE ]; then
    $GLOBAL_COMMAND_FILE daemon
else
    $BITDUST_COMMAND_FILE daemon
fi

echo ''
echo '##### ready'


exit 0

