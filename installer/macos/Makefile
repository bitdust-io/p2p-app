# This Makefile requires the following commands to be available:
# * virtualenv
# * python3.11 -> must have same version that Kivy.dmg uses
# * curl
# * Cython (via pip install)
#
# To install those tools you can use "system_dependencies" make target

CURRENT_DIR="${PWD}"
GIT_SCM_VERSION="2.23.0"

.cache:
	@mkdir -p -v cache
	@if [ ! -f "./cache/git.dmg" ]; then cd cache && curl -L "https://sourceforge.net/projects/git-osx-installer/files/git-${GIT_SCM_VERSION}-intel-universal-mavericks.dmg/download?use_mirror=autoselect" -o "git.dmg"; fi
	@if [ ! -d "./cache/buildozer" ]; then git clone --depth=1 https://github.com/kivy/buildozer ./cache/buildozer; fi
	@cd ./cache/buildozer && git fetch --all && git reset --hard origin/master

.git_scm:
	@if [ ! -d "./cache/.git_scm" ]; then python3 extract_dmg.py "${CURRENT_DIR}/cache/git.dmg" "${CURRENT_DIR}/cache/.git_scm" && python3 extract_pkg.py "${CURRENT_DIR}/cache/.git_scm/git-${GIT_SCM_VERSION}-intel-universal-mavericks.pkg" && mv -v ./cache/.git_scm/git-${GIT_SCM_VERSION}-intel-universal-mavericks ./cache/.git_scm/git_scm && cd ./cache/.git_scm && zip --symlinks -r -X git_scm.zip git_scm && cd ../..; fi

.workspace:
	@rm -rf ./bin/* && mkdir -p -v ./workspace && rm -rf ./workspace/bitdust-p2p.app

.venv:
	@if [ ! -d "./workspace/venv" ]; then cd ./workspace/ && rm -rf venv && python3.11 -m venv venv && ./venv/bin/pip install --upgrade pip >pip.log && ./venv/bin/pip install -r requirements.txt >>pip.log; fi

.install_buildozer:
	@if [ ! -f ./workspace/venv/bin/buildozer ]; then cd ./cache/buildozer/ && ../../workspace/venv/bin/python setup.py build && ../../workspace/venv/bin/pip install -e . ; fi
	@mkdir -p -v ./cache/.buildozer/bin/

.prepare: .cache .git_scm .workspace
	@cp -v -r ./src/* ./workspace/

.spec: .prepare .venv .install_buildozer
	@cd ./workspace/ && BUILD_DIR="$(CURRENT_DIR)/cache/.buildozer" BIN_DIR="$(CURRENT_DIR)/workspace/bin" ./venv/bin/python3 -c "tpl=open('buildozer.spec.template').read();import os,sys;sys.stdout.write(tpl.format(build_dir=os.environ['BUILD_DIR'],bin_dir=os.environ['BIN_DIR']));" > buildozer.spec

build: .spec
	@mkdir -p ./bin/
	@rm -rf ./bin/*.app
	@if [ ! -d "./cache/bitdust-p2p.app" ]; then cd ./workspace/ && PYTHONIOENCODING=utf-8 VIRTUAL_ENV=1 ./venv/bin/buildozer -v osx release && cd .. && mv ./cache/.buildozer/osx/platform/kivy-sdk-packager-master/osx/bitdust-p2p.app ./cache/ && mv -v ./workspace/bitdust-logo-color.icns ./cache/bitdust-p2p.app/Contents/Resources/AppIcon.icns; fi
	@rm -rf ./workspace/bitdust-p2p.app
	@cp -R ./cache/bitdust-p2p.app ./workspace/
	@cp -R ./cache/.git_scm/git_scm ./workspace/bitdust-p2p.app/Contents/Resources
	@rm -rfv ./workspace/bitdust-p2p.app/Contents/Resources/yourapp
	@cp -v ./../../requirements.txt "$(CURRENT_DIR)/"
	@./workspace/bitdust-p2p.app/Contents/MacOS/Kivy -m pip install -r "$(CURRENT_DIR)/requirements.txt"
	@rm -rf "$(CURRENT_DIR)/requirements.txt"
	@mv -v ./workspace/launcher.sh ./workspace/bitdust-p2p.app/Contents/Resources/script

clean:
	@(cd ./workspace/ && PYTHONIOENCODING=utf-8 VIRTUAL_ENV=1 ./venv/bin/buildozer -v osx clean) || echo "done"

clean_full:
	@rm -rf ./workspace
	@rm -rf ./cache/*
	@rm -rf ./bin/*
