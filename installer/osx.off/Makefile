# This Makefile requires the following commands to be available:
# * python3
# * create-dmg
#

PYTHON_VERSION="3.10.14"
PYTHON_VERSION_SHORT="3.10"
GIT_SCM_VERSION="2.23.0"
CURRENT_DIR="${PWD}"

.cache:
	@mkdir -p .cache
	@if [ ! -f "./.cache/git.dmg" ]; then cd .cache && curl -L "https://sourceforge.net/projects/git-osx-installer/files/git-${GIT_SCM_VERSION}-intel-universal-mavericks.dmg/download?use_mirror=autoselect" -o "git.dmg"; fi
	@if [ ! -d "./.cache/openssl" ]; then cd .cache && git clone https://github.com/openssl/openssl.git; fi
	@if [ ! -f "./.cache/Python-${PYTHON_VERSION}.tgz" ]; then cd .cache && curl "https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz" -o "Python-${PYTHON_VERSION}.tgz"; fi
	@if [ ! -d "./.cache/Python-${PYTHON_VERSION}" ]; then cd .cache && tar -zxvf "Python-${PYTHON_VERSION}.tgz"; fi

.git_scm:
	@if [ ! -d ".git_scm" ]; then python3 extract_dmg.py ${CURRENT_DIR}/.cache/git.dmg ${CURRENT_DIR}/.git_scm; python3 extract_pkg.py ${CURRENT_DIR}/.git_scm/git-${GIT_SCM_VERSION}-intel-universal-mavericks.pkg; mv -v ${CURRENT_DIR}/.git_scm/git-${GIT_SCM_VERSION}-intel-universal-mavericks ${CURRENT_DIR}/.git_scm/git_scm; cd .git_scm && zip --symlinks -r -X git_scm.zip git_scm && cd ..; fi

.openssl:
	@if [ ! -d ".openssl" ]; then mkdir .openssl && cd ./.cache/openssl && ./config shared no-ssl2 no-ssl3 no-comp --prefix="${CURRENT_DIR}/.openssl" --openssldir="${CURRENT_DIR}/.openssl" && make && make install; fi

.python-portable:
	@if [ ! -d ".python-portable" ]; then mkdir .python-portable && cd "./.cache/Python-${PYTHON_VERSION}" && ./configure MACOSX_DEPLOYMENT_TARGET=10.9 PY_UNSUPPORTED_OPENSSL_BUILD=static --with-openssl="${CURRENT_DIR}/.openssl" --enable-optimizations --prefix="${CURRENT_DIR}/.python-portable" && make altinstall; fi
	@rm -rf "./.python-portable/lib/python${PYTHON_VERSION_SHORT}/test"
	@cp -v "./.python-portable/bin/python${PYTHON_VERSION_SHORT}" "./.python-portable/bin/BitDust-p2p-app"
	@cp -v "./.python-portable/bin/python${PYTHON_VERSION_SHORT}" "./.python-portable/bin/python3"
	@cp -v "./.python-portable/bin/pip${PYTHON_VERSION_SHORT}" "./.python-portable/bin/pip3"
	@"./.python-portable/bin/pip3" install -r ../../requirements.txt
	@"./.python-portable/bin/pip3" install pyobjus
	@cd .python-portable && find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete
	@zip -r -X python.zip .python-portable/ && mv -v python.zip .cache/

.prepare:
	@rm -rf ./bin/* && rm -rf workspace && mkdir workspace
	@cp ./src/bitdust-logo-color.icns workspace/
	@cp -R ./src/BitDust-p2p-app._app workspace/
	@mv workspace/BitDust-p2p-app._app workspace/BitDust-p2p-app.app
	@cp -v ./.cache/python.zip workspace/BitDust-p2p-app.app/Contents/Resources/
	@cp -v ./.git_scm/git_scm.zip workspace/BitDust-p2p-app.app/Contents/Resources/

build: .cache .git_scm .openssl .python-portable .prepare
	@rm -rf bin && mkdir -p bin
	@cd workspace && create-dmg --volname "BitDust-p2p-app Installer" --volicon "bitdust-logo-color.icns" --icon-size 100 --icon "BitDust-p2p-app.app" 200 200 --window-pos 200 120 --window-size 800 400 --hide-extension "BitDust-p2p-app" --app-drop-link 600 185 "BitDust-p2p-app.dmg" "${PWD}/workspace/BitDust-p2p-app.app"
	@mv -v workspace/BitDust-p2p-app.dmg bin/
	@echo "DONE"

clean:
	@rm -rf ./bin/* && rm -rf workspace

clean_cache:
	@rm -rf .cache

clean_openssl:
	@rm -rf .openssl

clean_git_scm:
	@rm -rf .git_scm

clean_python:
	@rm -rf .python-portable

clean_full: clean clean_cache clean_openssl clean_python clean_git_scm
