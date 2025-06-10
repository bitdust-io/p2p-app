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
	# @cd ./cache/buildozer && git fetch --all && git reset --hard origin/master

.git_scm:
	@if [ ! -d "./cache/.git_scm" ]; then python3 extract_dmg.py "${CURRENT_DIR}/cache/git.dmg" "${CURRENT_DIR}/cache/.git_scm" && python3 extract_pkg.py "${CURRENT_DIR}/cache/.git_scm/git-${GIT_SCM_VERSION}-intel-universal-mavericks.pkg" && mv -v ./cache/.git_scm/git-${GIT_SCM_VERSION}-intel-universal-mavericks ./cache/.git_scm/git_scm && cd ./cache/.git_scm && zip --symlinks -r -X git_scm.zip git_scm && cd ../..; fi

.workspace:
	@rm -rf ./bin/* && mkdir -p -v ./workspace && rm -rf ./workspace/BitDust-p2p.app

.venv:
	@if [ ! -d "./workspace/venv" ]; then cd ./workspace/ && rm -rf venv && python3.11 -m venv venv && ./venv/bin/pip install --upgrade pip >pip.log && ./venv/bin/pip install -r requirements.txt >>pip.log; fi

.install_buildozer:
	@if [ ! -f ./workspace/venv/bin/buildozer ]; then cd ./cache/buildozer/ && ../../workspace/venv/bin/python setup.py build && ../../workspace/venv/bin/pip install -e . ; fi
	@mkdir -p -v ./cache/.buildozer/bin/

.prepare: .cache .git_scm .workspace
	@cp -v -R ./src/* ./workspace/

.spec: .prepare .venv .install_buildozer
	@cd ./workspace/ && BUILD_DIR="$(CURRENT_DIR)/cache/.buildozer" BIN_DIR="$(CURRENT_DIR)/workspace/bin" ./venv/bin/python3 -c "tpl=open('buildozer.spec.template').read();import os,sys;sys.stdout.write(tpl.format(build_dir=os.environ['BUILD_DIR'],bin_dir=os.environ['BIN_DIR']));" > buildozer.spec

build: .spec
	@mkdir -p ./bin/
	@rm -rf ./bin/*.app
	@if [ ! -d "./cache/BitDust-p2p.app" ]; then cd ./workspace/ && PYTHONIOENCODING=utf-8 VIRTUAL_ENV=1 ./venv/bin/buildozer --verbose osx release && cd .. && mv ./cache/.buildozer/osx/platform/kivy-sdk-packager-master/osx/BitDust-p2p.app ./cache/; fi
	@rm -rf ./workspace/BitDust-p2p.app
	@cp -R ./cache/BitDust-p2p.app ./workspace/
	@cp -R ./cache/.git_scm/git_scm ./workspace/BitDust-p2p.app/Contents/Resources
	@rm -rfv ./workspace/BitDust-p2p.app/Contents/Resources/yourapp
	@mv -v ./workspace/AppIcon.icns ./workspace/BitDust-p2p.app/Contents/Resources/
	@mv -v ./workspace/AppSettings.plist ./workspace/BitDust-p2p.app/Contents/Resources/
	@rm -rf ./workspace/BitDust-p2p.app/Contents/Resources/MainMenu.nib
	@mv -v ./workspace/MainMenu.nib ./workspace/BitDust-p2p.app/Contents/Resources/
	@mv -v ./workspace/Info.plist ./workspace/BitDust-p2p.app/Contents/Info.plist
	@mv -v ./workspace/launcher.sh ./workspace/BitDust-p2p.app/Contents/Resources/script
	@mv -v ./workspace/python.sh ./workspace/BitDust-p2p.app/Contents/Resources/
	@rm -v ./workspace/BitDust-p2p.app/Contents/MacOS/Kivy
	@mv -v ./workspace/BitDust-p2p ./workspace/BitDust-p2p.app/Contents/MacOS/
	@./workspace/BitDust-p2p.app/Contents/Resources/python.sh -m pip uninstall --yes pillow kivy Kivy_Garden
	@rm -rf ./workspace/BitDust-p2p.app/Contents/Resources/venv/lib/python3.11/site-packages/share/kivy-examples
	@cp ./create-osx-dmg.sh ./workspace
	@mkdir -p ./workspace/data && cp -v ./background.png ./workspace/data
	@cd ./workspace && sh -x create-osx-dmg.sh BitDust-p2p.app BitDust-p2p && mv BitDust-p2p.dmg BitDust-p2p-app.dmg
	@mv -v ./workspace/BitDust-p2p-app.dmg ./bin
	@echo "Now go to https://github.com/bitdust-io/p2p-app/releases/tag/alpha page and click [Edit] icon button in the top right corner."
	@echo "First remove the BitDust-p2p-app.dmg file from the attached binaries."
	@echo "Then upload bin/BitDust-p2p-app.dmg file and click [Update release] button."

clean:
	@(cd ./workspace/ && PYTHONIOENCODING=utf-8 VIRTUAL_ENV=1 ./venv/bin/buildozer -v osx clean) || echo "done"

clean_cache:
	@rm -rf ./cache/*
	@rm -rf ./cache/.git_scm
	@rm -rf ./cache/.buildozer

clean_full: clean_cache
	@rm -rf ./workspace
	@rm -rf ./bin/*
