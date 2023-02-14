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

.prepare:
	@rm -rf bin/* && rm -rf workspace && mkdir workspace
	@if [ ! -f "./sdk/support-compat-27.0.0.aar" ]; then curl https://dl.google.com/dl/android/maven2/com/android/support/support-compat/27.0.0/support-compat-27.0.0.aar -o ./sdk/support-compat-27.0.0.aar; fi
	@if [ ! -f "./sdk/pepk.jar" ]; then curl https://www.gstatic.com/play-apps-publisher-rapid/signing-tool/prod/pepk-src.jar -o ./sdk/pepk.jar; fi
	@if [ ! -d "./sdk/buildozer" ]; then git clone --depth=1 https://github.com/kivy/buildozer ./sdk/buildozer; fi
	@cd ./sdk/buildozer && git fetch --all && git reset --hard origin/master
	@if [ ! -d "./sdk/python-for-android" ]; then git clone --single-branch --branch master --depth=1 https://github.com/kivy/python-for-android.git ./sdk/python-for-android; fi
	@cd ./sdk/python-for-android && git fetch --all && git reset --hard origin/master
	@# mkdir -p ./sdk/python-for-android/pythonforandroid/bootstraps/sdl2/build/src/main/res/xml/
	@# cp -r -v ./src/etc/res/xml/network_security_config.xml ./sdk/python-for-android/pythonforandroid/bootstraps/sdl2/build/src/main/res/xml/
	@# cp -r -v ./src/etc/AndroidManifest.tmpl.xml ./sdk/python-for-android/pythonforandroid/bootstraps/sdl2/build/templates/
	@# cp -r -v ./src/etc/build.tmpl.gradle ./sdk/python-for-android/pythonforandroid/bootstraps/common/build/templates/
	@# if [ ! -f "./sdk/bundletool.jar" ]; then curl https://github.com/google/bundletool/releases/download/1.13.2/bundletool-all-1.13.2.jar -o sdk/bundletool.jar; fi
	@cp -r src/* workspace/ && cp -v sdk/pepk.jar workspace/
	# cp -v sdk/bundletool.jar workspace/
	@cp -v sdk/support-compat-27.0.0.aar workspace/
	@cd workspace/ && ./prepare.sh

build: .prepare
	@cd workspace/ && make aab
	@cd workspace/ && zipalign -v 4 ./bin/BitDustAndroid_unsigned.aab ./bin/BitDustAndroid.aab
	@cd workspace/ && apksigner sign --ks ~/keystores/bitdust.keystore --ks-pass file:../.keystore_password --v1-signing-enabled true --v2-signing-enabled true --min-sdk-version 21 bin/BitDustAndroid.aab
	@rm -rfv ./workspace/bin/BitDustAndroid_unsigned.aab
	@rm -rfv ./workspace/bin/bitdust1-*-release.aab
	@mv -v ./workspace/bin/*.aab ./bin/
	@cp -v ./workspace/version ./src/version && cat ./src/version

debug:
	@cd workspace/ && make apk
	@cd workspace/ && zipalign -v 4 ./bin/BitDustAndroid_unsigned.apk  ./bin/BitDustAndroid.apk
	@cd workspace/ && apksigner sign --ks ~/keystores/bitdust.keystore --ks-pass file:../.keystore_password --v1-signing-enabled true --v2-signing-enabled true bin/BitDustAndroid.apk
	@mv -v ./workspace/bin/BitDustAndroid.apk ./workspace/bin/BitDustAndroid_arm64_v8a.apk
	@cp -v ./workspace/bin/BitDustAndroid_arm64_v8a.apk ./bin/
	@apktool d -o ./workspace/bin/apk/ -f ./workspace/bin/BitDustAndroid_arm64_v8a.apk
	@mkdir -p ./workspace/bin/apk/private_mp3/
	@cp -v ./workspace/bin/apk/assets/private.tar ./workspace/bin/apk/private_mp3/private_mp3.tar.gz
	@cd ./workspace/bin/apk/private_mp3/ && tar -p -xf private_mp3.tar.gz && find . -type d -exec chmod +x {} \;
	@rm -rfv ./workspace/bin/BitDustAndroid.apk
	@rm -rfv ./workspace/bin/BitDustAndroid_unsigned.apk
	@rm -rfv ./workspace/bin/bitdust1-*-release-unsigned.apk

system_dependencies:
	@sudo apt-get update; sudo apt-get install --yes --no-install-recommends openjdk-11-jdk cython3 autoconf automake libtool ccache lld zipalign apksigner
	@python3 -m pip install Cython

test:
	@adb install -r bin/BitDustAndroid_arm64_v8a.apk

shell:
	@adb shell "cd /storage/emulated/0/Android/data/org.bitdust_io.bitdust1/files/Documents/.bitdust/; ls -la; sh;"

log:
	@adb logcat | grep -E "python|Bitdustnode|Exception"

log_quick:
	@adb logcat | grep -E "python|Bitdustnode|PythonActivity|BitDust|SDL|PythonService|crush|bitdust|bitdust_io|Exception"

log_main:
	@adb shell tail -f /storage/emulated/0/Android/data/org.bitdust_io.bitdust1/files/Documents/.bitdust/logs/android.log

log_states:
	@adb shell tail -f /storage/emulated/0/Android/data/org.bitdust_io.bitdust1/files/Documents/.bitdust/logs/automats.log

cat_log_main:
	@adb shell cat /storage/emulated/0/Android/data/org.bitdust_io.bitdust1/files/Documents/.bitdust/logs/android.log

cat_log_automat:
	@adb shell cat /storage/emulated/0/Android/data/org.bitdust_io.bitdust1/files/Documents/.bitdust/logs/automats.log
