# This Makefile requires the following tools to be available:
# * python3.11

mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
cur_dir := $(dir $(mkfile_path))

.cache:
	@mkdir -p -v cache

.workspace:
	@mkdir -p -v workspace
	@cp -r -v ./src/* workspace/

.venv:
	@if [ ! -d "./workspace/venv" ]; then cd ./workspace/ && python3.11 -m venv venv && ./venv/bin/pip install --upgrade pip; fi
	@cd ./workspace/ && ./venv/bin/pip install git+https://github.com/kivy/kivy-ios


.prepare: .cache .workspace
	@echo "current version is:" && cat ./workspace/version && echo ""
	@echo "core version is:" && cat ./workspace/core_version && echo ""
	@git rev-list --count HEAD >./workspace/revnum
	@REVNUM=`cat ./workspace/revnum`
	@echo "revision number based on total amount of commits in the Git repository is:" && cat ./workspace/revnum
	@cd ./workspace/ && python3 -c "cv=open('core_version').read().strip().split('.');v=list(open('version').read().strip().split('.'));v[0]=cv[0];v[-2]=str(int(v[-2])+1);v[-1]=open('revnum').read().strip();open('version','w').write(('.'.join(v)).strip())"
	@echo "new version will be:" && cat ./workspace/version && echo ""
	@rm -rf ./workspace/app && mkdir -p -v ./workspace/app && cp -r -v ../../src/* ./workspace/app/
	@cd ./workspace/app/ && rm -rf deploy && rm -rf service && rm -rf tools && find . -type d -name __pycache__ -exec rm -rf {} +
	@python3 -c "v=open('./workspace/version').read().strip();open('./workspace/app/version.py','w').write('__version__ = \"%s\"' % v);"

build: .prepare .venv
	@cd ./workspace/ && ./venv/bin/toolchain build python3
	@cd ./workspace/ && ./venv/bin/toolchain build kivy freetype libffi libjpeg libpng pillow
	@cd ./workspace/ && ./venv/bin/toolchain pip3 install -r requirements.txt
	@if [ ! -d "./workspace/bitdust-p2p-app-ios" ]; then cd ./workspace/ && ./venv/bin/toolchain create bitdust-p2p-app ${cur_dir}/workspace/app; fi
	# @cp -v ./src/main.m ./workspace/bitdust-p2p-app-ios/
	@cp -v ./src/*.png ./workspace/bitdust-p2p-app-ios/
	@cp -v -r ./src/bitdust-p2p-app ./workspace/bitdust-p2p-app-ios/
	@cp -v ./src/bitdust-p2p-app-info.plist ./workspace/bitdust-p2p-app-ios/
	@cd ./workspace/ && ./venv/bin/toolchain update bitdust-p2p-app-ios/bitdust-p2p-app.xcodeproj
	@cd ./workspace/ && python3 -c "v=open('version').read().strip();s=open('bitdust-p2p-app-ios/bitdust-p2p-app-Info.plist').read();s=s.replace('1.1111',v);open('bitdust-p2p-app-ios/bitdust-p2p-app-Info.plist','wt').write(s);"
	@cp -v ./workspace/version ./src/version && cat ./src/version
	@echo "" && echo 'now run "make open_project" and click "build" in the Xcode dashboard'
	@echo 'next you need to update release version: open "Info" tab in .xcodeproj file properties, change "Bundle version" and "Bundle version string" values'
	@echo 'then click in the top menu [Product]->[Archive]->[Distribute app] to upload built package via AppConnect'
	@echo 'go to https://developer.apple.com/account -> Apps -> BitDust, create new version, fill in the form details and send fore app review'
	@cd ./workspace/ && open bitdust-p2p-app-ios/bitdust-p2p-app.xcodeproj

clean:
	@rm -rf ./workspace

clean_project:
	@rm -rf ./workspace/bitdust-p2p-app-ios/

update_project:
	@cp -r -v ../../src/* ./workspace/app/
	@cd ./workspace/app/ && rm -rf deploy && rm -rf service && rm -rf tools && find . -type d -name __pycache__ -exec rm -rf {} +
	@cp -v ./src/*.png ./workspace/bitdust-p2p-app-ios/
	@cp -v -r ./src/bitdust-p2p-app ./workspace/bitdust-p2p-app-ios/
	@cp -v ./src/bitdust-p2p-app-info.plist ./workspace/bitdust-p2p-app-ios/
	@cd ./workspace/ && ./venv/bin/toolchain update bitdust-p2p-app-ios/bitdust-p2p-app.xcodeproj
	@cd ./workspace/ && python3 -c "v=open('version').read().strip();s=open('bitdust-p2p-app-ios/bitdust-p2p-app-Info.plist').read();s=s.replace('1.1111',v);open('bitdust-p2p-app-ios/bitdust-p2p-app-Info.plist','wt').write(s);"

open_project:
	@cd ./workspace/ && open bitdust-p2p-app-ios/bitdust-p2p-app.xcodeproj
