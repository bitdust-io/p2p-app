# This Makefile requires the following commands to be available:
# * python3
# * create-dmg
#

PYTHON_VERSION="3.10.9"
CURRENT_DIR="${PWD}"

.workspace:
	@rm -rf ./bin/* && rm -rf workspace && mkdir workspace
	@cp -rv ./src/BitDust-p2p-app.app workspace/
	@cp -rv ./src/bitdust-logo-color.icns workspace/
	# @cp -r ./.python-portable workspace/BitDust-p2p-app.app/Contents/MacOS/

.cache:
	@mkdir -p .cache
	@if [ ! -f "./cache/Python-${PYTHON_VERSION}.tgz" ]; then curl "https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz" -o "./cache/Python-${PYTHON_VERSION}.tgz"; fi
	@if [ ! -d "./cache/Python-${PYTHON_VERSION}" ]; then cd cache && tar -zxvf "Python-${PYTHON_VERSION}.tgz"; fi

.python-portable:
	@if [ ! -d ".python-portable" ]; then mkdir .python-portable && cd "./cache/Python-${PYTHON_VERSION}" && OPENSSL_ROOT=$(shell brew --prefix openssl) && ./configure MACOSX_DEPLOYMENT_TARGET=10.9 CPPFLAGS="-I${OPENSSL_ROOT}/include" LDFLAGS="-L${OPENSSL_ROOT}/lib" --prefix="${CURRENT_DIR}/.python-portable" && make altinstall; fi

build: .cache .python-portable .workspace
	@rm -rf bin/*.dmg
	@cd workspace && create-dmg --volname "BitDust-p2p-app Installer" --volicon "bitdust-logo-color.icns" --icon-size 100 --icon "BitDust-p2p-app.app" 200 200 --window-pos 200 120 --window-size 800 400 --hide-extension "BitDust-p2p-app.app" --app-drop-link 600 185 "BitDust-p2p-app.dmg" "${PWD}/workspace/BitDust-p2p-app.app"
	@mv -v workspace/BitDust-p2p-app.dmg bin/
	@echo "DONE"

clean:
	@rm -rf ./bin/* && rm -rf workspace

clean/cache:
	@rm -rf .cache

clean/python-portable:
	@rm -rf .python-portable
