# This Makefile requires the following commands to be available:
# * virtualenv
# * python3

REQUIREMENTS_TXT:=requirements.txt

REQUIREMENTS_ANDROID:="kivy==2.0.0,https://github.com/vesellov/KivyMD/archive/master.zip,sdl2_ttf==2.0.15,PIL,pyjnius,service_identity,pyparsing,appdirs,cffi,six,pycryptodome,attrs,hyperlink,idna,cryptography,automat,android,toml,incremental,twisted==20.3.0,python3"
# pillow

OS=$(shell lsb_release -si 2>/dev/null || uname)
PIP:="venv/bin/pip"
PYTHON="venv/bin/python"
PYTHON_VERSION=python3.7

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
	# @$(PIP) install Cython pygments docutils pillow
	@$(PIP) install -r $(REQUIREMENTS_TXT)

update:
	@git fetch
	@git reset --hard origin/master

run:
	@$(PYTHON) -u src/main.py


### Requirements & Dependencies

system_dependencies:
ifeq ($(OS), Ubuntu)
	@sudo apt-get update; sudo apt-get install --yes --no-install-recommends cmake python-setuptools python-pygame python-opengl python-enchant python-dev build-essential python-pip python-virtualenv libgl1-mesa-dev libgles2-mesa-dev zlib1g-dev xclip
endif

install: system_dependencies clean venv

download_google_binaries:
	@curl https://dl.google.com/dl/android/maven2/com/android/support/support-compat/27.0.0/support-compat-27.0.0.aar -o support-compat-27.0.0.aar
	@curl https://www.gstatic.com/play-apps-publisher-rapid/signing-tool/prod/pepk-src.jar -o pepk.jar

install_buildozer:
	@rm -rf buildozer/
	# @git clone https://github.com/kivy/buildozer buildozer
	@git clone https://github.com/vesellov/buildozer buildozer
	@cd ./buildozer/; ../venv/bin/python setup.py build; ../venv/bin/pip install -e .; cd ..

install_p4a:
	@rm -rf python-for-android/
	@git clone --single-branch --branch develop https://github.com/kivy/python-for-android.git
	# @git clone --single-branch --branch master https://github.com/vesellov/python-for-android.git
	# @git clone --single-branch --branch develop https://github.com/vesellov/python-for-android.git
	# @git clone --single-branch --branch develop_more https://github.com/vesellov/python-for-android.git
	@mkdir -p ./python-for-android/pythonforandroid/bootstraps/sdl2/build/src/main/res/xml/
	@cp -r -v etc/res/xml/network_security_config.xml ./python-for-android/pythonforandroid/bootstraps/sdl2/build/src/main/res/xml/

update_p4a:
	@cd ./python-for-android; git fetch --all; git reset --hard origin/develop; cd ..;
	# @cd ./python-for-android; git fetch --all; git reset --hard origin/develop_more; cd ..;

update_kivymd_icons:
	@./venv/bin/python ./venv/lib/python3.6/site-packages/kivymd/tools/update_icons.py

make_link_engine_repo:
	@rm -rf ./src/bitdust; ln -v -s ../../bitdust ./src/bitdust;

update_engine_repo:
	@cd ./src/bitdust; git fetch origin -v; git pull origin master; cd ../..; #  git reset --hard origin/master; cd ../..;


### Android release & development

clean_android_environment:
	@rm -rf .build_incremental
	@rm -rf .release_incremental
	@VIRTUAL_ENV=1 ./venv/bin/buildozer -v android clean

clean_android_environment_full:
	@rm -rf .build_incremental
	@rm -rf .release_incremental
	@rm -rf .buildozer

system_dependencies_android:
ifeq ($(OS), Ubuntu)
	@sudo apt-get update; sudo apt-get install --yes --no-install-recommends openjdk-8-jdk cython3 autoconf
	@$(PYTHON_VERSION) -m pip install Cython
endif

rewrite_android_dist_files:
	@mkdir -p ./python-for-android/pythonforandroid/bootstraps/sdl2/build/src/main/res/xml/
	@cp -r -v etc/res/xml/network_security_config.xml ./python-for-android/pythonforandroid/bootstraps/sdl2/build/src/main/res/xml/

refresh_android_environment: update_p4a rewrite_android_dist_files
	$(MAKE) spec requirements=$(REQUIREMENTS_ANDROID)

refresh_android_environment_full: update_p4a rewrite_android_dist_files update_engine_repo
	$(MAKE) spec requirements=$(REQUIREMENTS_ANDROID)

spec:
	@P_requirements="$(requirements)" ./venv/bin/python3 -c "tpl=open('buildozer.spec.template').read();import os,sys;sys.stdout.write(tpl.format(requirements=os.environ['P_requirements']));" > buildozer.spec

build_android: refresh_android_environment
	@rm -rfv ./bin/*.apk
	@PYTHONIOENCODING=utf-8 VIRTUAL_ENV=1 ./venv/bin/buildozer -v android release
	@cp -v -f ./bin/bitdust*.apk ./bin/BitDustAndroid_unsigned.apk

release_android: refresh_android_environment_full
	@rm -rfv ./bin/*.apk
	@PYTHONIOENCODING=utf-8 VIRTUAL_ENV=1 ./venv/bin/buildozer -v android release | grep -v "Listing " | grep -v "Compiling " | grep -v "\# Copy " | grep -v "\# Create directory " | grep -v "\- copy" | grep -v "running mv "
	@cp -v -f ./bin/bitdust*.apk ./bin/BitDustAndroid_unsigned.apk

test_apk:
	@adb install -r bin/BitDustAndroid.apk

log_adb:
	@adb logcat | grep -vE "python  : extracting|pythonutil: Checking pattern" | grep -E "WebViewConsole|python|DEBUG|Bitdustnode|BitDustActivity|PythonActivity|BitDust|SDL|PythonService|crush|Exception|WebViewManager|WebViewFactory"

log_adb_fast:
	@adb logcat | grep -E "WebViewConsole|python|DEBUG|Bitdustnode|PythonActivity|BitDust|SDL|PythonService|crush|bitdust1|bitdust_io|Exception|WebViewManager|WebViewFactory"

log_adb_brief:
	@adb logcat | grep -v "Notification.Badge:" | grep -v "GameManagerService:" | grep -v "GamePkgDataHelper:" | grep -v "Layer   :" | grep -v "SurfaceFlinger:" | grep -v "SurfaceControl:" | grep -v "RemoteAnimationController:" | grep -v "WindowManager:" | grep -v extracting | grep -v "Checking pattern" | grep -v "Library loading" | grep -v "Loading library" | grep -v "AppleWebKit/537.36 (KHTML, like Gecko)" | grep -v "I Bitdustnode:   " | grep -v "I Bitdustnode: DEBUG:jnius.reflect:" | grep -e python -e Bitdustnode -e "E AndroidRuntime" -e "F DEBUG" -e "PythonActivity:" -e "WebViewConsole:" -e "SDL     :" -e "PythonService:" -e "org.bitdust_io.bitdust1"

log_adb_short:
	@adb logcat | grep -v "python  : extracting" | grep -v "pythonutil: Checking pattern" | grep -e python -e Bitdustnode -e "E AndroidRuntime" -e "F DEBUG" -e "PythonActivity:" -e "WebViewConsole:" -e "SDL     :" -e "PythonService:"

log_adb_full:
	@adb logcat

log_main:
	@adb shell tail -f /storage/emulated/0/.bitdust/logs/android.log

log_states:
	@adb shell tail -f /storage/emulated/0/.bitdust/logs/automats.log

shell:
	@adb shell "cd /storage/emulated/0/.bitdust/; ls -la; sh;"

cat_main_log:
	@adb shell cat /storage/emulated/0/.bitdust/logs/android.log

cat_automat_log:
	@adb shell cat /storage/emulated/0/.bitdust/logs/automats.log
