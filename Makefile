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
	@sudo apt-get update; sudo apt-get install --yes --no-install-recommends python-setuptools python-pygame python-opengl python-enchant python-dev build-essential python-pip python-virtualenv libgl1-mesa-dev libgles2-mesa-dev zlib1g-dev xclip
endif

install: system_dependencies clean venv

install_buildozer:
	@rm -rf buildozer/
	@git clone https://github.com/vesellov/buildozer buildozer
	@cd ./buildozer/; ../venv/bin/python setup.py build; ../venv/bin/pip install -e .; cd ..

install_p4a:
	@rm -rf python-for-android/
	@git clone --single-branch --branch develop https://github.com/vesellov/python-for-android.git
	@mkdir -p ./python-for-android/pythonforandroid/bootstraps/sdl2/build/src/main/res/xml/
	@cp -r -v etc/res/xml/network_security_config.xml ./python-for-android/pythonforandroid/bootstraps/sdl2/build/src/main/res/xml/

update_p4a:
	@cd ./python-for-android; git fetch --all; git reset --hard origin/develop; cd ..;

update_kivymd_icons:
	@./venv/bin/python ./venv/lib/python3.6/site-packages/kivymd/tools/update_icons.py

make_link_engine_repo:
	@rm -rf ./src/bitdust; ln -v -s ../../bitdust ./src/bitdust;

update_engine_repo:
	@cd ./src/bitdust; git fetch origin -v; git reset --hard origin/master; cd ../..;


### Android release & development

clean_android_build:
	@rm -rf .build_incremental
	@rm -rf .release_incremental
	@VIRTUAL_ENV=1 ./venv/bin/buildozer -v android clean

clean_android_build_full:
	@rm -rf .build_incremental
	@rm -rf .release_incremental
	@rm -rf .buildozer

system_dependencies_android:
ifeq ($(OS), Ubuntu)
	@sudo apt-get update; sudo apt-get install --yes --no-install-recommends openjdk-8-jdk cython autoconf
endif

rewrite_android_dist_files:
	@mkdir -p ./python-for-android/pythonforandroid/bootstraps/sdl2/build/src/main/res/xml/
	@cp -r -v etc/res/xml/network_security_config.xml ./python-for-android/pythonforandroid/bootstraps/sdl2/build/src/main/res/xml/

refresh_android_environment: update_p4a rewrite_android_dist_files

refresh_android_environment_full: update_p4a update_engine_repo rewrite_android_dist_files

.build_android_incremental:
	# @python3 -c "import os, re; s = re.sub('(requirements = .+?python3)','# \g<1>',open('buildozer.spec','r').read()); open('buildozer.spec','w').write(s);"
	# @python3 -c "import os, re; s = re.sub('# requirements = incremental','requirements = incremental',open('buildozer.spec','r').read()); open('buildozer.spec','w').write(s);"
	# @VIRTUAL_ENV=1 ./venv/bin/buildozer -v android debug
	# @python3 -c "import os, re; s = re.sub('# (requirements = .+?python3)','\g<1>',open('buildozer.spec','r').read()); open('buildozer.spec','w').write(s);"
	# @python3 -c "import os, re; s = re.sub('requirements = incremental','# requirements = incremental',open('buildozer.spec','r').read()); open('buildozer.spec','w').write(s);"
	@echo '1' > .build_android_incremental

build_android: refresh_android_environment .build_android_incremental
	@VIRTUAL_ENV=1 ./venv/bin/buildozer -v android debug

.release_android_incremental:
	# @python3 -c "import os, re; s = re.sub('(requirements = .+?python3)','# \g<1>',open('buildozer.spec','r').read()); open('buildozer.spec','w').write(s);"
	# @python3 -c "import os, re; s = re.sub('# requirements = incremental','requirements = incremental',open('buildozer.spec','r').read()); open('buildozer.spec','w').write(s);"
	# @VIRTUAL_ENV=1 ./venv/bin/buildozer -v android release
	# @python3 -c "import os, re; s = re.sub('# (requirements = .+?python3)','\g<1>',open('buildozer.spec','r').read()); open('buildozer.spec','w').write(s);"
	# @python3 -c "import os, re; s = re.sub('requirements = incremental','# requirements = incremental',open('buildozer.spec','r').read()); open('buildozer.spec','w').write(s);"
	@echo '1' > .release_android_incremental

release_android: refresh_android_environment .release_android_incremental
	@rm -rfv ./bin/*.apk
	@VIRTUAL_ENV=1 ./venv/bin/buildozer -v android release | grep -v "Listing " | grep -v "Compiling " | grep -v "\# Copy " | grep -v "\# Create directory " | grep -v "\- copy" | grep -v "running mv "
	# @VIRTUAL_ENV=1 ./venv/bin/buildozer -v android release
	@mv ./bin/bitdust*.apk ./bin/BitDustAndroid_unsigned.apk

download_apk:
	@rm -rfv bin/*.apk
	@scp android.build:p2p-app/bin/BitDustAndroid.apk bin/.
	@ls -la bin/

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
