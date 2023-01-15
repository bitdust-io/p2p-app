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


make clone_engine_sources
make update_engine_sources
make prepare_build_location


rm -rf buildozer.spec.building
cp -v buildozer.spec buildozer.spec.building
echo "__version__ = \"$1\"" > ./src/version.py
make refresh_android_environment
make release_android
mv -v -f buildozer.spec.building buildozer.spec


pw=$(cat ".keystore_password")
zipalign -v 4 ./bin/BitDustAndroid_unsigned.aab  ./bin/BitDustAndroid.aab
apksigner sign --ks ~/keystores/bitdust.keystore --ks-pass file:.keystore_password --v1-signing-enabled true --v2-signing-enabled true --min-sdk-version 21 bin/BitDustAndroid.aab


rm -rfv ./bin/BitDustAndroid_unsigned.aab
rm -rfv ./bin/bitdust1-*-release.aab


echo "SUCCESS !!!"
