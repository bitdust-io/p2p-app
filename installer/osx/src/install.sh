#!/bin/sh

ROOT_DIR="$HOME/.bitdust"
SOURCE_UI_DIR="${ROOT_DIR}/ui"
VENV_DIR="${ROOT_DIR}/venv"
PYTHON_BIN="${ROOT_DIR}/venv/bin/python"
PIP_BIN="${ROOT_DIR}/venv/bin/pip"
MAIN_PY="${SOURCE_UI_DIR}/src/main.py"


if [[ "$1" == "start" ]]; then
    cd $SOURCE_UI_DIR
    $PYTHON_BIN $MAIN_PY
    exit 0;
fi


PYTHON="$1"


echo "### 5%"

if [ ! -d $ROOT_DIR ]; then
    mkdir -p $ROOT_DIR
    echo "created application data folder"
fi
echo "### 10%"


cd "$ROOT_DIR"


if [ ! -d "$SOURCE_UI_DIR/src" ]; then
    echo "downloading source files from Git repository"
    mkdir -p $SOURCE_UI_DIR
    git clone --single-branch --branch master --depth=1 "https://github.com/bitdust-io/p2p-app.git" "$SOURCE_UI_DIR"
else
    cd $SOURCE_UI_DIR
    echo "updating source files from Git repository"
    git fetch --all
    echo "### 20%"
    echo "refreshing source files"
    git reset --hard origin/master
    cd ..
fi
echo "### 40%"


if [ ! -e $PIP_BIN ]; then
    echo "building Python virtual environment"
    $PYTHON -m virtualenv $VENV_DIR
fi
echo "### 60%"


echo "updating Python virtual environment"
$PIP_BIN --default-timeout=10 install -U -r $SOURCE_UI_DIR/requirements.txt
echo "### 80%"


echo "### 100%"
echo 'done, application is ready'

exit 0