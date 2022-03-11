#!/bin/bash

# Usage:
#
#   ./release.sh <version number>
#
#
# to be able to publish on Android Play Market need to first prepare the keystore file and send it Google:
# java -jar pepk.jar --keystore=~/keystores/bitdust.keystore --alias=bitdust --output=output.zip --encryptionkey=xxx --include-cert
# create a file ".keystore_password" in the same folder and store the keystore password there

set -e


make prepare_build_location
make clone_engine_sources


rm -rf buildozer.spec.building
cp -v buildozer.spec buildozer.spec.building


echo "__version__ = \"$1\"" > ./src/version.py
make refresh_android_environment_full


rm -rfv ./bin/BitDustAndroid.aab
rm -rfv ./bin/BitDustAndroid_unsigned.aab
rm -rfv ./bin/bitdust1-*-release.aab
(PYTHONIOENCODING=utf-8 VIRTUAL_ENV=1 ./venv/bin/buildozer -v android release || PYTHONIOENCODING=utf-8 VIRTUAL_ENV=1 ./venv/bin/buildozer -v android release)


cp -T -v ./bin/bitdust*arm64-v8a_armeabi-v7a_x86_64-release.aab ./bin/BitDustAndroid_unsigned.aab
mv -v -f buildozer.spec.building buildozer.spec
pw=$(cat ".keystore_password")
zipalign -v 4 ./bin/BitDustAndroid_unsigned.aab  ./bin/BitDustAndroid.aab
apksigner sign --ks ~/keystores/bitdust.keystore --ks-pass file:.keystore_password --v1-signing-enabled true --v2-signing-enabled true --min-sdk-version 21 bin/BitDustAndroid.aab


rm -rfv ./bin/BitDustAndroid_unsigned.aab
rm -rfv ./bin/bitdust1-*-release.aab


echo "SUCCESS !!!"
