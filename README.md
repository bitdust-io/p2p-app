# BitDust p2p-app

BitDust p2p-app is an open-source, peer-to-peer network application for secure data storage and private online communications. The application is written in Python using the Kivy framework and published under GNU AGPLv3.



### Install and run inside development environment locally

At first clone the files locally and change to the repository folder:

        git clone https://github.com/bitdust-io/p2p-app.git bitdust.p2p-app
        cd bitdust.p2p-app


To be able to run the application from the command line, you must first install Kivy dependencies (tested on Linux Debian) and create Python virtual environment:

        make clean install


Also, to ensure you are running the most recent version, you can run the following command that will use Git to fetch the latest commits from GitHub:

        make update


Then you should be able to start the application inside the development environment:

        make run
