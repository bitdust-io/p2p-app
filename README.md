# BitDust p2p-app

This is BitDust Application written in Python using Kivy framework.


### Install and run inside development environment

At first clone the files locally and change to the repository folder:

        git clone https://github.com/bitdust-io/p2p-app.git bitdust.p2p-app
        cd bitdust.p2p-app


To be able to run the application from command line you must first install Kivy dependencies (tested on Linux Debian) and create Python virtual environment:

        make clean install


Also to make sure you are running the most recent version you can run following command that will use Git to fetch latest commits from GitHub:

        make update


Then you should be able to start the application inside development environment:

        make run



### Build for Android

##### Prepare application folders

First you must clone BitDust Engine and BitDust UI repositories to your local machine next to the current repository folder on the same level.

BitDust p2p-app APK bundle will include files from both repositories, so we need to create a sym-links to BitDust Engine repository:

        cd ..
        git clone https://github.com/bitdust-io/public.git bitdust
        cd bitdust.p2p-app/src/
        ln -s ../../bitdust bitdust
        cd ..


##### Install dependencies (tested on Ubuntu 18.04 Desktop)

        make system_dependencies
        make system_dependencies_android


##### Create Python virtual environment

        make venv


##### Install Buildozer into the virtual environment

        make install_buildozer


##### Install python-for-android (in a separate folder)

        make install_p4a


##### Get some additional libraries and tools provided by Google as binaries

        make download_google_binaries


##### Prepare keystore to protect your .APK

To be able to publish BitDust on Google Play Market .APK file must be digitaly signed.

First create a keystore file:

        mkdir ~/keystores/
        keytool -genkey -v -keystore ~/keystores/bitdust.keystore -alias bitdust -keyalg RSA -keysize 4096 -validity 60000


Make sure you have backup copy of the `bitdust.keystore` file and the keystore password!

Now you need to get from Google Play Console "Encryption Key" which you will use to prepare `output.zip` file.

You need to do that only one time - the `output.zip` file must be uploaded back to Google.

This way Google will be able to verify the .APK file you built before publish it on the Play Market:

        java -jar pepk.jar --keystore=~/keystores/bitdust.keystore --alias=bitdust --encryptionkey=<Encryption Key> --include-cert --output=output.zip



##### Make sure BitDust Engine is up to date before the build

        make update_engine_repo


##### Build APK image with specific version

        ./release_ubuntu.sh 1.0.5



### Build for MacOS

TODO:


### Build for Windows

TODO:

