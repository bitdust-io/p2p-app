# This Makefile requires the following commands to be available:
# * virtualenv
# * python3

REQUIREMENTS_TXT:=requirements.txt

REQUIREMENTS_ANDROID:="kivy==2.1.0,kivymd==1.0.2,PIL,sdl,plyer,pyjnius,service_identity,pyparsing,appdirs,cffi,six,pycryptodome,attrs,hyperlink,idna,cryptography,automat,android,toml,incremental,twisted,python3"

OS=$(shell lsb_release -si 2>/dev/null || uname)
PIP:="venv/bin/pip"
PYTHON="venv/bin/python"
PYTHON_VERSION=python3

.PHONY: clean pyclean

.system_dependencies:
ifeq ($(OS), Ubuntu)
	@sudo apt-get update && sudo apt-get install --yes --no-install-recommends cmake build-essential libgl1-mesa-dev libgles2-mesa-dev zlib1g-dev xclip python3-setuptools python3-pygame python3-opengl python3-enchant python3-dev python3-pip python3-virtualenv
endif

install: .system_dependencies clean venv

pyclean:
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@rm -rf *.egg-info build
	@rm -rf coverage.xml .coverage

clean: pyclean
	@rm -rf venv

venv:
	@rm -rf venv
	@$(PYTHON_VERSION) -m venv venv
	@$(PIP) install --upgrade pip
	@# @$(PIP) install Cython pygments docutils pillow
	@$(PIP) install -r $(REQUIREMENTS_TXT)

update:
	@# @git fetch
	@# @git reset --hard origin/master
	@git pull

run:
	@$(PYTHON) -u src/main.py
