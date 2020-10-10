#!/bin/bash

# Usage:
#
#   ./release.sh <version number>
#
#
# to be able to publish on Android Play Market need to first prepare the keystore file and send it Google:
# java -jar pepk.jar --keystore=~/keystores/bitdust.keystore --alias=bitdust --output=output.zip --encryptionkey=xxx --include-cert
#

set -e

rm -rf buildozer.spec.bk

cp -v buildozer.spec buildozer.spec.bk

# sed -i "s/^version = [0-9]*.[0-9]*.[0-9]*$/version = $1/g" buildozer.spec

echo "__version__ = \"$1\"" > src/version.py

make release

mv -v -f buildozer.spec.bk buildozer.spec

jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore ~/keystores/bitdust.keystore bin/BitDustAndroid_unsigned.apk bitdust

~/.buildozer/android/platform/android-sdk/build-tools/30.0.1/zipalign -v 4 ./bin/BitDustAndroid_unsigned.apk  ./bin/BitDustAndroid.apk

echo "SUCCESS !!!"
