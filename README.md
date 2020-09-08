# BitDust User App

BitDust user App written in Python using Kivy framework 

At first clone the files locally and change to the repository folder:

                git clone https://github.com/bitdust-io/user-app.git
                cd user-app


To be able to run the application from command line you must first install Kivy dependencies (tested on Linux Debian) and create Python virtual environment:

                make clean install


Also to make sure you are running the most recent version you can run following command that will use Git to fetch latest commits from GitHub:

                make update


Then you should be able to start the application inside development environment:

                make run
