@echo off

set CURRENT_PATH="%1"
echo Starting inside %CURRENT_PATH%
cd /D "%CURRENT_PATH%"

set BITDUST_GIT_REPO=https://github.com/bitdust-io/public.git
set BITDUST_APP_GIT_REPO=https://github.com/bitdust-io/p2p-app.git
set PYTHON_URL=https://www.python.org/ftp/python/3.8.6/python-3.8.6-embed-win32.zip
set GET_PIP_URL=https://bootstrap.pypa.io/get-pip.py

set _my_datetime=%date%_%time%
set _my_datetime=%_my_datetime: =_%
set _my_datetime=%_my_datetime::=%
set _my_datetime=%_my_datetime:/=_%
set _my_datetime=%_my_datetime:.=_%

echo ##### Verifying BitDust installation files
set BITDUST_FULL_HOME=%HOMEDRIVE%%HOMEPATH%\.bitdust

if not exist "%BITDUST_FULL_HOME%" echo Prepare destination folder
if not exist "%BITDUST_FULL_HOME%" mkdir "%BITDUST_FULL_HOME%"


rem TODO : to be able to correctly detect existing ".bitdust" folder need to check "appdata" file as well


echo ##### Prepare location for BitDust Home folder
set SHORT_PATH_SCRIPT=%BITDUST_FULL_HOME%\shortpath.bat
set SHORT_PATH_OUT=%BITDUST_FULL_HOME%\shortpath.txt
del /q /s /f "%SHORT_PATH_SCRIPT%" >nul 2>&1
del /q /s /f "%SHORT_PATH_OUT%" >nul 2>&1
echo @echo OFF > "%SHORT_PATH_SCRIPT%"
echo echo %%~s1 >> "%SHORT_PATH_SCRIPT%"
call "%SHORT_PATH_SCRIPT%" "%BITDUST_FULL_HOME%" > "%SHORT_PATH_OUT%"
set /P BITDUST_HOME=<"%SHORT_PATH_OUT%"
setlocal enabledelayedexpansion
for /l %%a in (1,1,300) do if "!BITDUST_HOME:~-1!"==" " set BITDUST_HOME=!BITDUST_HOME:~0,-1!
setlocal disabledelayedexpansion
del /q /s /f "%SHORT_PATH_SCRIPT%" >nul 2>&1
del /q /s /f "%SHORT_PATH_OUT%" >nul 2>&1


set BITDUST_NODE=%BITDUST_HOME%\venv\Scripts\BitDustNode.exe
set BITDUST_NODE_CONSOLE=%BITDUST_HOME%\venv\Scripts\BitDustConsole.exe


set PYTHON_EXE=%BITDUST_HOME%\python\python.exe
set GIT_EXE=%BITDUST_HOME%\git\bin\git.exe


if /I "%~1"=="stop" goto StopBitDustGo
goto RestartBitDust
:StopBitDustGo
echo ##### Stopping BitDust
cd /D "%BITDUST_HOME%"
if not exist %BITDUST_NODE_CONSOLE% goto KillBitDust
%BITDUST_NODE_CONSOLE% %BITDUST_HOME%\src\bitdust.py stop
:KillBitDust
taskkill /IM BitDustNode.exe /F /T
taskkill /IM bitdust-p2p-app.exe /F /T
:BitDustStopped
echo DONE
exit /b %errorlevel%


:RestartBitDust
if /I "%~1"=="restart" goto RestartBitDustGo
goto RedeployBitDust
:RestartBitDustGo
echo Restarting BitDust
cd /D "%BITDUST_HOME%"
if not exist %BITDUST_NODE_CONSOLE% goto BitDustRestarted
%BITDUST_NODE_CONSOLE% %BITDUST_HOME%\src\bitdust.py restart
:BitDustRestarted
echo DONE
exit /b %errorlevel%


:RedeployBitDust
if /I "%~1"=="redeploy" goto RedeployBitDustGo
goto StartBitDust
:RedeployBitDustGo
echo Redeploying BitDust
rmdir /S /Q %BITDUST_HOME%\venv
rmdir /S /Q %BITDUST_HOME%\src
rmdir /S /Q %BITDUST_HOME%\ui
rmdir /S /Q %BITDUST_HOME%\temp
echo Cleanup finished


:StartBitDust
echo Prepare to start BitDust


echo ##### Prepare Python interpretator files
if exist %PYTHON_EXE% goto PythonInstalled
:PythonToBeInstalled
cd /D "%BITDUST_HOME%"
echo Downloading Python interpretator
cscript /nologo "%CURRENT_PATH%\download_python.js"
if %errorlevel% neq 0 goto DEPLOY_ERROR
echo Extracting Python binaries
cd /D "%CURRENT_PATH%"
unzip.exe -o -q %BITDUST_HOME%\python-3.8.6-embed-win32.zip -d %BITDUST_HOME%\python
copy /B /Y python38._pth %BITDUST_HOME%\python
copy /B /Y bitdust.ico %BITDUST_HOME%\python\
copy /B /Y rcedit.exe %BITDUST_HOME%\python\
cd /D "%BITDUST_HOME%\python"
copy /B /Y pythonw.exe bitdust-p2p-app.exe
rcedit.exe bitdust-p2p-app.exe --set-version-string FileDescription "BitDust p2p-app"
if %errorlevel% neq 0 goto DEPLOY_ERROR
rcedit.exe bitdust-p2p-app.exe --set-icon bitdust.ico
if %errorlevel% neq 0 goto DEPLOY_ERROR
del /q /s /f %BITDUST_HOME%\python-3.8.6-embed-win32.zip >nul 2>&1
del /q /s /f %BITDUST_HOME%\python\rcedit.exe >nul 2>&1
echo Installing PIP package manager
cd /D "%BITDUST_HOME%"
cscript /nologo "%CURRENT_PATH%\download_pip.js"
if %errorlevel% neq 0 goto DEPLOY_ERROR
%PYTHON_EXE% %BITDUST_HOME%\get-pip.py
del /q /s /f %BITDUST_HOME%\get-pip.py >nul 2>&1
if %errorlevel% neq 0 goto DEPLOY_ERROR
echo Installing virtualenv package
%PYTHON_EXE% -m pip install -U virtualenv
if %errorlevel% neq 0 goto DEPLOY_ERROR
:PythonInstalled


echo ##### Prepare Git binaries
if exist %GIT_EXE% goto GitInstalled
echo Extracting Git binaries
cd /D "%BITDUST_HOME%"
copy /B /Y "%CURRENT_PATH%\git.zip" %BITDUST_HOME%
copy /B /Y "%CURRENT_PATH%\unzip.exe" %BITDUST_HOME%
unzip.exe -o -q git.zip
del /q /s /f %BITDUST_HOME%\git.zip >nul 2>&1
del /q /s /f %BITDUST_HOME%\unzip.exe >nul 2>&1
if %errorlevel% neq 0 goto DEPLOY_ERROR
:GitInstalled


echo ##### Prepare BitDust UI source files
if not exist %BITDUST_HOME%\ui mkdir %BITDUST_HOME%\ui

if exist %BITDUST_HOME%\ui\src goto UISourcesExist
echo Downloading BitDust UI files from GitHub repository
cd /D "%BITDUST_HOME%"
%BITDUST_HOME%\git\bin\git.exe -c http.sslBackend=schannel clone -q --single-branch --depth 1 %BITDUST_APP_GIT_REPO% ui
if %errorlevel% neq 0 goto DEPLOY_ERROR
:UISourcesExist

cd /D "%BITDUST_HOME%\ui\"
%BITDUST_HOME%\git\bin\git.exe -c http.sslBackend=schannel fetch --all
if %errorlevel% neq 0 goto DEPLOY_ERROR
%BITDUST_HOME%\git\bin\git.exe -c http.sslBackend=schannel reset --hard origin/master
if %errorlevel% neq 0 goto DEPLOY_ERROR


echo ##### Prepare environment for User Interface
%PYTHON_EXE% -m pip install -U -r %BITDUST_HOME%\ui\requirements-win.txt
if %errorlevel% neq 0 goto DEPLOY_ERROR


echo ##### Prepare BitDust source code files
if not exist %BITDUST_HOME%\src mkdir %BITDUST_HOME%\src


if exist %BITDUST_HOME%\src\bitdust.py goto SourcesExist
echo ##### Downloading BitDust source code from Git repository
cd /D "%BITDUST_HOME%\src"
%BITDUST_HOME%\git\bin\git.exe -c http.sslBackend=schannel clone -q --depth 1 %BITDUST_GIT_REPO% .
if %errorlevel% neq 0 goto DEPLOY_ERROR


:SourcesExist
echo ##### Updating BitDust source code from Git repository
cd /D "%BITDUST_HOME%\src"
%BITDUST_HOME%\git\bin\git.exe -c http.sslBackend=schannel fetch --all
if %errorlevel% neq 0 goto DEPLOY_ERROR
%BITDUST_HOME%\git\bin\git.exe -c http.sslBackend=schannel reset --hard origin/master
if %errorlevel% neq 0 goto DEPLOY_ERROR


echo ##### Prepare Python virtual environment
if exist %BITDUST_HOME%\venv\Scripts\pip.exe goto VenvUpdate
echo Creating BitDust virtual environment
cd /D "%BITDUST_HOME%\src"
copy /B /Y "%CURRENT_PATH%\requirements.txt" %BITDUST_HOME%\src\
%PYTHON_EXE% bitdust.py install
if %errorlevel% neq 0 goto DEPLOY_ERROR
goto VenvOk
:VenvUpdate


echo ##### Update Python virtual environment
copy /B /Y "%CURRENT_PATH%\requirements.txt" %BITDUST_HOME%\src\
%BITDUST_HOME%\venv\Scripts\pip.exe install -U -r %BITDUST_HOME%\src\requirements.txt
if %errorlevel% neq 0 goto DEPLOY_ERROR
:VenvOk


cd /D %BITDUST_HOME%


echo ##### Prepare BitDustNode process
if exist %BITDUST_NODE% goto BitDustNodeExeExist
copy /B /Y %BITDUST_HOME%\venv\Scripts\pythonw.exe %BITDUST_NODE%
:BitDustNodeExeExist


echo ##### Prepare BitDustConsole process
if exist %BITDUST_NODE_CONSOLE% goto BitDustConsoleExeExist
copy /B /Y %BITDUST_HOME%\venv\Scripts\python.exe %BITDUST_NODE_CONSOLE%
:BitDustConsoleExeExist


echo ##### SUCCESS
goto DEPLOY_SUCCESS


:DEPLOY_ERROR
echo ##### DEPLOYMENT FAILED
echo.
exit /b %errorlevel%


:DEPLOY_SUCCESS

rem  echo ##### Starting BitDust as a daemon process
rem cd /D "%BITDUST_HOME%"
rem %BITDUST_NODE% %BITDUST_HOME%\src\bitdust.py daemon

echo DONE
echo.
