# This Makefile requires the following commands to be available:
# * virtualenv
# * python3

REQUIREMENTS_TXT:=requirements.txt

OS=$(shell lsb_release -si 2>/dev/null || uname)
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

venv:
	@rm -rf venv
	@$(PYTHON_VERSION) -m venv venv
	@$(PIP) install --upgrade pip
	@$(PIP) install Cython pygments docutils pillow
	@$(PIP) install -r $(REQUIREMENTS_TXT)

update:
	@git fetch
	@git reset --hard origin/master

run:
	@$(PYTHON) src/main.py


### Requirements / Dependencies

system_dependencies:
ifeq ($(OS), Ubuntu)
	@sudo apt-get update; sudo apt-get install --yes --no-install-recommends python-setuptools python-pygame python-opengl python-enchant python-dev build-essential python-pip libgl1-mesa-dev libgles2-mesa-dev zlib1g-dev xclip
endif

install: system_dependencies clean venv

install_buildozer:
	@rm -rf buildozer/
	@git clone https://github.com/vesellov/buildozer
	@cd buildozer/; ../venv/bin/python setup.py build; ../venv/bin/pip install -e .; cd ..;

install_p4a:
	@rm -rf python-for-android/
	#@git clone --single-branch --branch master https://github.com/kivy/python-for-android.git
	@git clone --single-branch --branch master https://github.com/vesellov/python-for-android.git
	@mkdir -p ./python-for-android/pythonforandroid/bootstraps/sdl2/build/src/main/res/xml/
	@cp -r -v etc/res/xml/network_security_config.xml ./python-for-android/pythonforandroid/bootstraps/sdl2/build/src/main/res/xml/

update_p4a:
	@cd ./python-for-android; git fetch --all; git reset --hard origin/master; cd ..;

make_link_engine_repo:
	@rm -rf ./src/bitdust; ln -s ../../bitdust ./src/bitdust;

update_engine_repo:
	@cd ./src/bitdust; git fetch --all; git reset --hard origin/master; cd ../..;


### Android release

clean_android_build:
	@rm -rf .build_incremental
	@rm -rf .release_incremental
	@VIRTUAL_ENV=1 ./venv/bin/buildozer -v android clean

rewrite_android_dist_files:
	@mkdir -p ./python-for-android/pythonforandroid/bootstraps/sdl2/build/src/main/res/xml/
	@cp -r -v etc/res/xml/network_security_config.xml ./python-for-android/pythonforandroid/bootstraps/sdl2/build/src/main/res/xml/

refresh_android_environment: update_p4a update_engine_repo rewrite_android_dist_files

.build_android_incremental:
	@python3 -c "import os, re; s = re.sub('(requirements = .+?python3)','# \g<1>',open('buildozer.spec','r').read()); open('buildozer.spec','w').write(s);"
	@python3 -c "import os, re; s = re.sub('# requirements = incremental,kivy','requirements = incremental,kivy',open('buildozer.spec','r').read()); open('buildozer.spec','w').write(s);"
	@VIRTUAL_ENV=1 ./venv/bin/buildozer -v android debug
	@python3 -c "import os, re; s = re.sub('# (requirements = .+?python3)','\g<1>',open('buildozer.spec','r').read()); open('buildozer.spec','w').write(s);"
	@python3 -c "import os, re; s = re.sub('requirements = incremental,kivy','# requirements = incremental,kivy',open('buildozer.spec','r').read()); open('buildozer.spec','w').write(s);"
	@echo '1' > .build_android_incremental

build_android: refresh_environment .build_android_incremental
	@VIRTUAL_ENV=1 ./venv/bin/buildozer -v android debug

.release_android_incremental:
	@python3 -c "import os, re; s = re.sub('(requirements = .+?python3)','# \g<1>',open('buildozer.spec','r').read()); open('buildozer.spec','w').write(s);"
	@python3 -c "import os, re; s = re.sub('# requirements = incremental,kivy','requirements = incremental,kivy',open('buildozer.spec','r').read()); open('buildozer.spec','w').write(s);"
	@VIRTUAL_ENV=1 ./venv/bin/buildozer -v android release
	@python3 -c "import os, re; s = re.sub('# (requirements = .+?python3)','\g<1>',open('buildozer.spec','r').read()); open('buildozer.spec','w').write(s);"
	@python3 -c "import os, re; s = re.sub('requirements = incremental,kivy','# requirements = incremental,kivy',open('buildozer.spec','r').read()); open('buildozer.spec','w').write(s);"
	@echo '1' > .release_android_incremental

release_android: refresh_android_environment .release_android_incremental
	@rm -rfv ./bin/*.apk
	@VIRTUAL_ENV=1 ./venv/bin/buildozer -v android release  | grep -v "Listing " | grep -v "Compiling " | grep -v "\# Copy " | grep -v "\# Create directory " | grep -v "\- copy" | grep -v "running mv "
	@mv ./bin/bitdust*.apk ./bin/BitDustAndroid_unsigned.apk
