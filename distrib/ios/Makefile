# This Makefile requires the following commands to be available:
# * brew
# * python3
# * git
#

mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
cur_dir := $(dir $(mkfile_path))

.cache:
	@mkdir -p -v ./cache
	@if [ ! -d "./cache/bitdust" ]; then git clone https://github.com/bitdust-io/public.git ./cache/bitdust; fi
	@cd ./cache/bitdust && git pull && git log --graph --oneline --decorate -1 && git rev-list --count HEAD >../revnum

.workspace:
	@rm -rf ./bin/* && mkdir -p -v workspace
	@cp -r ./src/* workspace/

.prepare: .cache .workspace
	@mkdir -p -v ./workspace/app && cp -r ../../src/* ./workspace/app/ && mkdir -p -v ./workspace/app/bitdust_copy
	@cd ./cache/bitdust && git checkout-index -a -f --prefix="../../workspace/app/bitdust_copy/"
	@rm -rf ./workspace/app/bitdust && mv ./workspace/app/bitdust_copy/bitdust ./workspace/app/
	@rm -rf ./workspace/app/bitdust_forks && mv ./workspace/app/bitdust_copy/bitdust_forks ./workspace/app/
	@mv ./workspace/app/bitdust_copy/default_network.json ./workspace/app/
	@rm -rf ./workspace/app/bitdust_copy/
	@rm -rf ./workspace/app/deploy
	@rm -rf ./workspace/app/bitdust/devops
	@rm -rf ./workspace/app/bitdust/regress
	@rm -rf ./workspace/app/bitdust/regression
	@rm -rf ./workspace/app/bitdust/tests
	@rm -rf ./workspace/app/bitdust/icons
	@rm -rf ./workspace/app/bitdust_forks/Bismuth/wallet
	@python3 -c "v=open('./workspace/version').read().strip();open('./workspace/app/version.py','w').write('__version__ = \"%s\"' % v);"

.kivy_ios_env:
	@cd ./workspace && toolchain build python3 kivy hostopenssl hostpython3 freetype libcurl libffi libjpeg libpng openssl pillow plyer pyobjus sdl2 sdl2_image sdl2_mixer sdl2_ttf
	@cd ./workspace && toolchain pip install Kivy==2.2.1 kivymd==1.0.2 Pillow==8.2.0 six
	@touch .kivy_ios_env

build: .prepare .kivy_ios_env
	@cd ./workspace/app/bitdust/ && find . -type f -name "*.py" -exec sed -i -e 's/_Debug = True/_Debug = False/g' {} +

bump:
	@echo "current version is:" && cat ./workspace/version && echo ""
	@echo "core version is:" && cat ./workspace/core_version && echo ""
	@REVNUM=`cat ./cache/revnum`
	@echo "revision number based on total amount of commits in the Git repository is:" && cat ./cache/revnum
	@cd ./workspace/ && python3 -c "cv=open('core_version').read().strip().split('.');v=list(open('version').read().strip().split('.'));v[0]=cv[0];v[-2]=str(int(v[-2])+1);v[-1]=open('../cache/revnum').read().strip();open('version','w').write(('.'.join(v)).strip())"
	@echo "new version will be:" && cat ./workspace/version && echo ""

open_xcode_project:
	@cd ./workspace/ && open bitdust-p2p-app-ios/bitdust-p2p-app.xcodeproj

create_xcode_project:
	@cd ./workspace/ && toolchain create BitDust-p2p-app ${cur_dir}/workspace/app

clean:
	@rm -rf ./workspace
	@rm -rf ./bin/*

system_dependencies:
	@brew install autoconf automake libtool pkg-config python3
	@brew link libtool
	@pip3 install Cython==0.29.36
	@pip3 install kivy-ios
