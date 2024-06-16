#
# Makefile
#
# Copyright (C) 2008 Veselin Penev  https://bitdust.io
#
# This file (Makefile) is part of BitDust Software.
#
# BitDust is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BitDust Software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with BitDust Software.  If not, see <http://www.gnu.org/licenses/>.
#
# Please contact us if you have any questions at bitdust.io@gmail.com
#
# This Makefile requires the following commands to be available:
# * virtualenv
# * python3

REQUIREMENTS_TXT:=requirements.txt

REQUIREMENTS_ANDROID:="kivy==2.1.0,kivymd==1.0.2,PIL,sdl,plyer,pyjnius,service_identity,pyparsing,appdirs,cffi,six,pycryptodome,attrs,hyperlink,idna,cryptography,automat,android,toml,incremental,twisted,python3"

OS=$(shell lsb_release -si 2>/dev/null || uname)
PIP:="venv/bin/pip"
PYTHON="venv/bin/python"
PYTHON_VERSION=python3.9

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
	@$(PIP) install -r $(REQUIREMENTS_TXT)

update:
	@git pull

run:
	@$(PYTHON) -u src/main.py

check_no_debug:
	@grep --include=\*.py -rnw 'src' -e "_Debug = True" | tee /tmp/no_debug_report.txt
	@if [ -s /tmp/no_debug_report.txt ]; then rm -rf /tmp/no_debug_report.txt; echo "CODE CHECK FAILED: at least one time '_Debug = True' is present in the source code"; exit 1; fi
	@rm -rf /tmp/no_debug_report.txt;

debug_on:
	@find ./src -type f -name "*.py" -exec python3 -c 'import sys; inp=open(sys.argv[1]).read();outp=inp.replace("_Debug = False", "_Debug = True"); open(sys.argv[1],"w").write(outp); print(sys.argv[1], len(outp), "CHANGED" if inp != outp else "");' '{}' \;

debug_off:
	@find ./src -type f -name "*.py" -exec python3 -c 'import sys; inp=open(sys.argv[1]).read();outp=inp.replace("_Debug = True", "_Debug = False"); open(sys.argv[1],"w").write(outp); print(sys.argv[1], len(outp), "CHANGED" if inp != outp else "");' '{}' \;
