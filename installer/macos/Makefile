# This Makefile requires the following commands to be available:
# * virtualenv
# * python3.11 -> must have same version that Kivy.dmg uses
# * curl
# * Cython (via pip install)
#
# To install those tools you can use "system_dependencies" make target

CURRENT_DIR="${PWD}"

.cache:
	@mkdir -p -v cache
	@if [ ! -d "./cache/buildozer" ]; then git clone --depth=1 https://github.com/kivy/buildozer ./cache/buildozer; fi
	@cd ./cache/buildozer && git fetch --all && git reset --hard origin/master

.workspace:
	@rm -rf ./bin/* && mkdir -p -v ./workspace && rm -rf ./workspace/bitdust-p2p.app && rm -rf ./workspace/app
	@cp -v -r ./src/* workspace/

.venv:
	@if [ ! -d "./workspace/venv" ]; then cd ./workspace/ && rm -rf venv && python3.11 -m venv venv && ./venv/bin/pip install --upgrade pip >pip.log && ./venv/bin/pip install -r requirements.txt >>pip.log; fi

.install_buildozer:
	@if [ ! -f ./workspace/venv/bin/buildozer ]; then cd ./cache/buildozer/ && ../../workspace/venv/bin/python setup.py build && ../../workspace/venv/bin/pip install -e . ; fi
	@mkdir -p -v ./cache/.buildozer/bin/

.prepare: .cache .workspace
	@mkdir -p -v ./workspace/app && cp -v ./src/launcher.py ./workspace/app/main.py

.spec: .prepare .venv .install_buildozer
	@cd ./workspace/ && BUILD_DIR="$(CURRENT_DIR)/cache/.buildozer" BIN_DIR="$(CURRENT_DIR)/workspace/bin" ./venv/bin/python3 -c "tpl=open('buildozer.spec.template').read();import os,sys;sys.stdout.write(tpl.format(build_dir=os.environ['BUILD_DIR'],bin_dir=os.environ['BIN_DIR']));" > buildozer.spec

build: .spec
	@mkdir -p ./bin/
	@rm -rf ./bin/*.app
	@if [ ! -d "./cache/bitdust-p2p.app" ]; then cd ./workspace/ && PYTHONIOENCODING=utf-8 VIRTUAL_ENV=1 ./venv/bin/buildozer -v osx release; fi
	@if [ ! -d "./workspace/bitdust-logo-color.icns" ]; then rm -rfv ./cache/.buildozer/osx/platform/kivy-sdk-packager-master/osx/bitdust-p2p.app/Contents/Resources/AppIcon.icns && mv -v ./workspace/bitdust-logo-color.icns ./cache/.buildozer/osx/platform/kivy-sdk-packager-master/osx/bitdust-p2p.app/Contents/Resources/AppIcon.icns; fi
	@if [ ! -d "./cache/bitdust-p2p.app" ]; then cp -v -R ./cache/.buildozer/osx/platform/kivy-sdk-packager-master/osx/bitdust-p2p.app ./cache/; fi
	@cp -R ./cache/bitdust-p2p.app ./workspace/
	@cp -R ./cache/.git_scm/git_scm ./workspace/bitdust-p2p.app/Contents/Resources/yourapp/
	@cp -R -v ./workspace/app/* ./workspace/bitdust-p2p.app/Contents/Resources/yourapp/
	@cp -v ./workspace/install.sh ./workspace/bitdust-p2p.app/Contents/Resources/yourapp/

clean:
	@(cd ./workspace/ && PYTHONIOENCODING=utf-8 VIRTUAL_ENV=1 ./venv/bin/buildozer -v osx clean) || echo "done"

clean_full:
	@rm -rf ./workspace
	@rm -rf ./cache/*
	@rm -rf ./bin/*
