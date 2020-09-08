# This Makefile requires the following commands to be available:
# * virtualenv
# * python3

REQUIREMENTS_TXT:=requirements.txt

PIP:="venv/bin/pip"
PYTHON="venv/bin/python"
PYTHON_VERSION=python3

.PHONY: clean pyclean

pyclean:
	@find . -name *.pyc -delete
	@rm -rf *.egg-info build
	@rm -rf coverage.xml .coverage

clean: pyclean
	@rm -rf venv
	@rm -rf .tox

venv:
	@rm -rf venv
	@$(PYTHON_VERSION) -m venv venv
	@$(PIP) install --upgrade pip
	@$(PIP) install Cython pygments docutils pillow
	@$(PIP) install -r $(REQUIREMENTS_TXT)

apt_install:
	@sudo apt-get install python-setuptools python-pygame python-opengl python-enchant python-dev build-essential python-pip libgl1-mesa-dev libgles2-mesa-dev zlib1g-dev xclip wkhtmltopdf

install: apt_install venv

update:
	@git fetch
	@git reset --hard origin/master

run:
	@$(PYTHON) main.py
