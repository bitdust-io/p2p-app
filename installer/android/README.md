### Build for Android

##### Install dependencies

Several system tools and libraries are required for building and compiling project file binaries. For Android, there are also a few additional requirements:

        make system_dependencies



##### Prepare keystore to protect your .APK

To publish BitDust on Google Play Market, the .APK file must be digitally signed.

First create a keystore file:

        mkdir ~/keystores/
        keytool -genkey -v -keystore ~/keystores/bitdust.keystore -alias bitdust -keyalg RSA -keysize 4096 -validity 60000


Ensure you have a backup copy of the `bitdust.keystore` file and the keystore password!

Now you need to get from Google Play Console "Encryption Key," which you will use to prepare the `output.zip` file.

You only need to do this once. Also, the `output.zip` file must be uploaded back to Google. This way Google can verify the .APK file you built before publishing it on the Play Market:

        java -jar pepk.jar --keystore=~/keystores/bitdust.keystore --alias=bitdust --encryptionkey=<Encryption Key> --include-cert --output=output.zip



##### Build AAR bundle file

        make



##### Build APK bundle file

        make apk
