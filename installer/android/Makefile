# This Makefile requires the following commands to be available:
# * java
# * virtualenv
# * python3
# * curl
# * apksigner
# * zipalign
# * apktool
# * Cython (via pip install)
#
# To install those tools you can use "system_dependencies" make target
#
# To be able to publish on Android Play Market need to first prepare the keystore file and send it Google:
# java -jar pepk.jar --keystore=~/keystores/bitdust.keystore --alias=bitdust --output=output.zip --encryptionkey=xxx --include-cert
# create a file ".keystore_password" in the same folder and store the keystore password there

REQUIREMENTS_ANDROID:=$(shell python3 -c "import sys;l=open('src/requirements.txt').read().split('\n');l=[i.strip() for i in l if not i.strip().startswith('#')];sys.stdout.write(','.join(filter(None, l)));")

.cache:
	@mkdir -p -v cache
	@# if [ ! -f "./cache/support-compat-28.0.0.aar" ]; then curl https://dl.google.com/dl/android/maven2/com/android/support/support-compat/28.0.0/support-compat-28.0.0.aar -o ./cache/support-compat-28.0.0.aar; fi
	@if [ ! -f "./cache/pepk.jar" ]; then curl https://www.gstatic.com/play-apps-publisher-rapid/signing-tool/prod/pepk-src.jar -o ./cache/pepk.jar; fi
	@if [ ! -d "./cache/buildozer" ]; then git clone --depth=1 https://github.com/kivy/buildozer ./cache/buildozer; fi
	@cd ./cache/buildozer && git fetch --all && git reset --hard origin/master
	@# if [ ! -d "./cache/python-for-android" ]; then git clone --single-branch --branch master --depth=1 https://github.com/kivy/python-for-android.git ./cache/python-for-android; fi
	@# cd ./cache/python-for-android && git fetch --all && git reset --hard origin/master
	@# mkdir -p ./cache/python-for-android/pythonforandroid/bootstraps/sdl2/build/src/main/res/xml/
	@# cp -r -v ./src/etc/res/xml/network_security_config.xml ./cache/python-for-android/pythonforandroid/bootstraps/sdl2/build/src/main/res/xml/
	@# cp -r -v ./src/etc/AndroidManifest.tmpl.xml ./cache/python-for-android/pythonforandroid/bootstraps/sdl2/build/templates/
	@# cp -r -v ./src/etc/build.tmpl.gradle ./cache/python-for-android/pythonforandroid/bootstraps/common/build/templates/
	@# cp -r -v ./src/etc/gradle-wrapper.properties ./cache/python-for-android/pythonforandroid/bootstraps/common/build/gradle/wrapper/
	@# if [ ! -f "./cache/bundletool.jar" ]; then curl https://github.com/google/bundletool/releases/download/1.13.2/bundletool-all-1.13.2.jar -o cache/bundletool.jar; fi
	@cd ./cache && git rev-list --count HEAD >revnum

.workspace:
	@rm -rf ./bin/* && rm -rf workspace && mkdir -p -v workspace
	@cp -r ./src/* workspace/ && cp -v ./cache/pepk.jar ./workspace/
	@# cp -v ./cache/support-compat-28.0.0.aar workspace/

.venv:
	@cd ./workspace/ && rm -rf venv && python3 -m venv venv && ./venv/bin/pip install --upgrade pip >pip.log

.install_buildozer:
	@cd ./cache/buildozer/ && ../../workspace/venv/bin/python setup.py build && ../../workspace/venv/bin/pip install -e .

.prepare: .cache .workspace
	@echo "current version is:" && cat ./workspace/version && echo ""
	@echo "core version is:" && cat ./workspace/core_version && echo ""
	@REVNUM=`cat ./cache/revnum`
	@echo "revision number based on total amount of commits in the Git repository is:" && cat ./cache/revnum
	@cd ./workspace/ && python3 -c "cv=open('core_version').read().strip().split('.');v=list(open('version').read().strip().split('.'));v[0]=cv[0];v[-2]=str(int(v[-2])+1);v[-1]=open('../cache/revnum').read().strip();open('version','w').write(('.'.join(v)).strip())"
	@echo "new version will be:" && cat ./workspace/version && echo ""
	@rm -rf ./workspace/app && mkdir -p -v ./workspace/app && cp -r ../../src/* ./workspace/app/
	@python3 -c "v=open('./workspace/version').read().strip();open('./workspace/app/version.py','w').write('__version__ = \"%s\"' % v);"

.spec: .prepare .venv .install_buildozer
	@cd ./workspace/ && P_requirements="$(REQUIREMENTS_ANDROID)" ./venv/bin/python3 -c "tpl=open('buildozer.spec.template').read();import os,sys;sys.stdout.write(tpl.format(requirements=os.environ['P_requirements']));" > buildozer.spec

build: .spec
	@rm -rfv ./workspace/bin/*.aab
	@rm -rfv ./workspace/bin/*.apk
	@cd ./workspace/app/bitdust/ && find . -type f -name "*.py" -exec sed -i -e 's/_Debug = True/_Debug = False/g' {} +
	cd ./workspace/ && PYTHONIOENCODING=utf-8 VIRTUAL_ENV=1 ./venv/bin/buildozer -v android release 1>buildozer.log 2>buildozer.err
	@cp -f -T -v ./workspace/bin/bitdust*arm64-v8a_armeabi-v7a_x86_64-release.aab ./workspace/bin/BitDustAndroid_unsigned.aab
	@cd ./workspace/ && zipalign -v 4 ./bin/BitDustAndroid_unsigned.aab ./bin/BitDustAndroid.aab
	@cd ./workspace/ && apksigner sign --ks ~/keystores/bitdust.keystore --ks-pass file:../.keystore_password --v1-signing-enabled true --v2-signing-enabled true --min-sdk-version 21 bin/BitDustAndroid.aab
	@rm -rfv ./workspace/bin/BitDustAndroid_unsigned.aab
	@rm -rfv ./workspace/bin/bitdust1-*-release.aab
	@mv -v ./workspace/bin/*.aab ./bin/
	@cp -v ./workspace/version ./src/version && cat ./src/version && echo "" && echo "DONE"

# apk: build_arm64_v8a build_armeabi_v7a build_x86_64
# 	@rm -rfv ./workspace/bin/*.apk
# 	@cd ./workspace/app/bitdust/ && find . -type f -name "*.py" -exec sed -i -e 's/_Debug = True/_Debug = False/g' {} +
# 	cd ./workspace/ && PYTHONIOENCODING=utf-8 VIRTUAL_ENV=1 ./venv/bin/buildozer -v --profile arm64_v8a android release 1>buildozer.log 2>buildozer.err
# 	@cp -v -T -f ./workspace/bin/bitdust*.apk ./workspace/bin/BitDustAndroid_unsigned.apk
# 	@cd ./workspace/ && zipalign -v 4 ./bin/BitDustAndroid_unsigned.apk  ./bin/BitDustAndroid.apk
# 	@cd ./workspace/ && apksigner sign --ks ~/keystores/bitdust.keystore --ks-pass file:../.keystore_password --v1-signing-enabled true --v2-signing-enabled true ./bin/BitDustAndroid.apk
# 	@mv -v ./workspace/bin/BitDustAndroid.apk ./workspace/bin/BitDustAndroid_arm64_v8a.apk
# 	@cp -v ./workspace/bin/BitDustAndroid_arm64_v8a.apk ./bin/
# 	@apktool d -o ./workspace/bin/apk/ -f ./workspace/bin/BitDustAndroid_arm64_v8a.apk
# 	@mkdir -p -v ./workspace/bin/apk/private_mp3/
# 	@cp -v ./workspace/bin/apk/assets/private.tar ./workspace/bin/apk/private_mp3/private_mp3.tar.gz
# 	@cd ./workspace/bin/apk/private_mp3/ && tar -p -xf private_mp3.tar.gz && find . -type d -exec chmod +x {} \;
# 	@rm -rfv ./workspace/bin/BitDustAndroid.apk
# 	@rm -rfv ./workspace/bin/BitDustAndroid_unsigned.apk
# 	@rm -rfv ./workspace/bin/bitdust1-*-release-unsigned.apk

debug: .spec
	~/.gradle/wrapper/dists/gradle-8.0.2-all/14bt34ptcsg1ikmfn78tdh1keu/gradle-8.0.2/bin/gradle --stop || echo "gradle daemon was not stopped"
	@rm -rfv ./workspace/bin/*.apk
	@# cd ./workspace/app/ && find . -type f -name "bpmain.py" -exec sed -i -e 's/_Debug = False/_Debug = True/g' {} +
	cd ./workspace/ && GRADLE_OPTS="-Xms1724m -Xmx5048m -Dorg.gradle.jvmargs='-Xms1724m -Xmx5048m'" PYTHONIOENCODING=utf-8 VIRTUAL_ENV=1 ./venv/bin/buildozer -v --profile arm64_v8a android debug  
	@# 1>buildozer.log 2>buildozer.err
	@cp -v -T -f ./workspace/bin/bitdust*.apk ./workspace/bin/BitDustAndroid_unsigned.apk
	@cd ./workspace/ && zipalign -v 4 ./bin/BitDustAndroid_unsigned.apk  ./bin/BitDustAndroid.apk
	@cd ./workspace/ && apksigner sign --ks ~/keystores/bitdust.keystore --ks-pass file:../.keystore_password --v1-signing-enabled true --v2-signing-enabled true ./bin/BitDustAndroid.apk
	@mv -v ./workspace/bin/BitDustAndroid.apk ./workspace/bin/BitDustAndroid_arm64_v8a.apk
	@cp -v ./workspace/bin/BitDustAndroid_arm64_v8a.apk ./bin/
	@apktool d -o ./workspace/bin/apk/ -f ./workspace/bin/BitDustAndroid_arm64_v8a.apk
	@mkdir -p -v ./workspace/bin/apk/private_mp3/
	@cp -v ./workspace/bin/apk/assets/private.tar ./workspace/bin/apk/private_mp3/private_mp3.tar.gz
	@cd ./workspace/bin/apk/private_mp3/ && tar -p -xf private_mp3.tar.gz && find . -type d -exec chmod +x {} \;
	@rm -rfv ./workspace/bin/BitDustAndroid.apk
	@rm -rfv ./workspace/bin/BitDustAndroid_unsigned.apk
	@rm -rfv ./workspace/bin/bitdust1-*-release-unsigned.apk

build_arm64_v8a:
	~/.gradle/wrapper/dists/gradle-8.0.2-all/14bt34ptcsg1ikmfn78tdh1keu/gradle-8.0.2/bin/gradle --stop || echo "gradle daemon was not stopped"
	@cd ./workspace/app/bitdust/ && find . -type f -name "*.py" -exec sed -i -e 's/_Debug = True/_Debug = False/g' {} +
	cd ./workspace/ && PYTHONIOENCODING=utf-8 VIRTUAL_ENV=1 ./venv/bin/buildozer -v --profile arm64_v8a android release 1>buildozer.arm64_v8a.log 2>buildozer.arm64_v8a.err
	@cp -v -T -f ./workspace/bin/bitdust*.apk ./workspace/bin/BitDustAndroid_unsigned.apk
	@cd ./workspace/ && zipalign -v 4 ./bin/BitDustAndroid_unsigned.apk  ./bin/BitDustAndroid.apk
	@cd ./workspace/ && apksigner sign --ks ~/keystores/bitdust.keystore --ks-pass file:../.keystore_password --v1-signing-enabled true --v2-signing-enabled true ./bin/BitDustAndroid.apk
	@mv -v ./workspace/bin/BitDustAndroid.apk ./workspace/bin/BitDustAndroid_arm64_v8a.apk
	@cp -v ./workspace/bin/BitDustAndroid_arm64_v8a.apk ./bin/
	@apktool d -o ./workspace/bin/apk/ -f ./workspace/bin/BitDustAndroid_arm64_v8a.apk
	@cp -v ./workspace/version ./src/version && cat ./src/version && echo "" && echo "DONE"

build_armeabi_v7a:
	~/.gradle/wrapper/dists/gradle-8.0.2-all/14bt34ptcsg1ikmfn78tdh1keu/gradle-8.0.2/bin/gradle --stop || echo "gradle daemon was not stopped"
	@cd ./workspace/app/bitdust/ && find . -type f -name "*.py" -exec sed -i -e 's/_Debug = True/_Debug = False/g' {} +
	cd ./workspace/ && PYTHONIOENCODING=utf-8 VIRTUAL_ENV=1 ./venv/bin/buildozer -v --profile armeabi_v7a android release 1>buildozer.armeabi_v7a.log 2>buildozer.armeabi_v7a.err
	@cp -v -T -f ./workspace/bin/bitdust*.apk ./workspace/bin/BitDustAndroid_unsigned.apk
	@cd ./workspace/ && zipalign -v 4 ./bin/BitDustAndroid_unsigned.apk  ./bin/BitDustAndroid.apk
	@cd ./workspace/ && apksigner sign --ks ~/keystores/bitdust.keystore --ks-pass file:../.keystore_password --v1-signing-enabled true --v2-signing-enabled true ./bin/BitDustAndroid.apk
	@mv -v ./workspace/bin/BitDustAndroid.apk ./workspace/bin/BitDustAndroid_armeabi_v7a.apk
	@cp -v ./workspace/bin/BitDustAndroid_armeabi_v7a.apk ./bin/
	@apktool d -o ./workspace/bin/apk/ -f ./workspace/bin/BitDustAndroid_armeabi_v7a.apk
	@cp -v ./workspace/version ./src/version && cat ./src/version && echo "" && echo "DONE"

build_x86_64:
	~/.gradle/wrapper/dists/gradle-8.0.2-all/14bt34ptcsg1ikmfn78tdh1keu/gradle-8.0.2/bin/gradle --stop || echo "gradle daemon was not stopped"
	@cd ./workspace/app/bitdust/ && find . -type f -name "*.py" -exec sed -i -e 's/_Debug = True/_Debug = False/g' {} +
	cd ./workspace/ && PYTHONIOENCODING=utf-8 VIRTUAL_ENV=1 ./venv/bin/buildozer -v --profile x86_64 android release 1>buildozer.x86_64.log 2>buildozer.x86_64.err
	@cp -v -T -f ./workspace/bin/bitdust*.apk ./workspace/bin/BitDustAndroid_unsigned.apk
	@cd ./workspace/ && zipalign -v 4 ./bin/BitDustAndroid_unsigned.apk  ./bin/BitDustAndroid.apk
	@cd ./workspace/ && apksigner sign --ks ~/keystores/bitdust.keystore --ks-pass file:../.keystore_password --v1-signing-enabled true --v2-signing-enabled true ./bin/BitDustAndroid.apk
	@mv -v ./workspace/bin/BitDustAndroid.apk ./workspace/bin/BitDustAndroid_x86_64.apk
	@cp -v ./workspace/bin/BitDustAndroid_x86_64.apk ./bin/
	@apktool d -o ./workspace/bin/apk/ -f ./workspace/bin/BitDustAndroid_x86_64.apk
	@cp -v ./workspace/version ./src/version && cat ./src/version && echo "" && echo "DONE"

clean:
	@(cd ./workspace/ && PYTHONIOENCODING=utf-8 VIRTUAL_ENV=1 ./venv/bin/buildozer -v android clean) || echo "done"

clean_full:
	@rm -rf ./workspace
	@rm -rf ./cache/.buildozer
	@rm -rf ./cache/*
	@rm -rf ./bin/*

system_dependencies:
	@sudo apt-get update; sudo apt-get install --yes --no-install-recommends openjdk-11-jdk cython3 autoconf automake libtool ccache lld zipalign apksigner
	@python3 -m pip install --upgrade Cython

test:
	@adb install -r -d bin/BitDustAndroid_arm64_v8a.apk

shell:
	@echo "run-as org.bitdust_io.bitdust1"
	@adb shell "run-as org.bitdust_io.bitdust1; bash"

log:
	@cd ./workspace/ && PYTHONIOENCODING=utf-8 VIRTUAL_ENV=1 ./venv/bin/buildozer -v android logcat

log_full:
	@adb logcat *:V python:V

log_quick:
	@adb logcat | grep -E "python|Bitdustnode|PythonActivity|BitDust|SDL|PythonService|crush|bitdust|bitdust_io|Exception"

log_main:
	@adb exec-out run-as org.bitdust_io.bitdust1 tail -f /data/user/0/org.bitdust_io.bitdust1/files/.bitdust/logs/android.log

log_states:
	@adb exec-out run-as org.bitdust_io.bitdust1 tail -f /data/user/0/org.bitdust_io.bitdust1/files/.bitdust/logs/automats.log

cat_log_main:
	@adb exec-out run-as org.bitdust_io.bitdust1 cat /data/user/0/org.bitdust_io.bitdust1/files/.bitdust/logs/android.log

cat_log_automat:
	@adb exec-out run-as org.bitdust_io.bitdust1 cat /data/user/0/org.bitdust_io.bitdust1/files/.bitdust/logs/automats.log
