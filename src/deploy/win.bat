@echo off

rem Get the datetime in a format that can go in a filename.
set _my_datetime=%date%_%time%
set _my_datetime=%_my_datetime: =_%
set _my_datetime=%_my_datetime::=%
set _my_datetime=%_my_datetime:/=_%
set _my_datetime=%_my_datetime:.=_%


set BITDUST_GIT_REPO=https://github.com/bitdust-io/public.git


echo ##### Verifying BitDust installation files
set CURRENT_PATH=%cd%
set BITDUST_FULL_HOME=%HOMEDRIVE%%HOMEPATH%\.bitdust

set PYTHON_ZIP=%CURRENT_PATH%\resources\app\build_resources\win\python.zip
set GIT_ZIP=%CURRENT_PATH%\resources\app\build_resources\win\git.zip
set UNZIP_EXE=%CURRENT_PATH%\resources\app\build_resources\win\unzip.exe

if not exist "%PYTHON_ZIP%" set PYTHON_ZIP=%CURRENT_PATH%\build_resources\win\python.zip
if not exist "%GIT_ZIP%" set GIT_ZIP=%CURRENT_PATH%\build_resources\win\git.zip
if not exist "%UNZIP_EXE%" set UNZIP_EXE=%CURRENT_PATH%\build_resources\win\unzip.exe


rem echo My Home folder expected to be %BITDUST_FULL_HOME%
if not exist "%BITDUST_FULL_HOME%" echo Prepare destination folder
if not exist "%BITDUST_FULL_HOME%" mkdir "%BITDUST_FULL_HOME%"


rem TODO : check appdata file also


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
rem echo Safe path to BitDust Home folder is %BITDUST_HOME%


set BITDUST_NODE=%BITDUST_HOME%\venv\Scripts\BitDustNode.exe
set BITDUST_NODE_CONSOLE=%BITDUST_HOME%\venv\Scripts\BitDustConsole.exe


rem echo BitDust Home location is "%BITDUST_HOME%"
set PYTHON_EXE=%BITDUST_HOME%\python\python.exe
rem echo Python process is %PYTHON_EXE%
set GIT_EXE=%BITDUST_HOME%\git\bin\git.exe
rem echo GIT process is %GIT_EXE%


if /I "%~1"=="stop" goto StopBitDustGo
goto RestartBitDust
:StopBitDustGo
echo ##### Stopping BitDust
cd /D "%BITDUST_HOME%"
if not exist %BITDUST_NODE_CONSOLE% goto KillBitDust
%BITDUST_NODE_CONSOLE% %BITDUST_HOME%\src\bitdust.py stop
:KillBitDust
taskkill /IM BitDustNode.exe /F /T
rem taskkill /IM BitDustConsole.exe /F /T
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
rmdir /S /Q %BITDUST_HOME%\identitycache
rmdir /S /Q %BITDUST_HOME%\identityhistory
rmdir /S /Q %BITDUST_HOME%\temp
echo Cleanup finished


:StartBitDust
echo Prepare to start BitDust


echo ##### Prepare Python interpretator files
if exist %PYTHON_EXE% goto PythonInstalled
:PythonToBeInstalled
echo Extracting Python binaries
%UNZIP_EXE% -o -q %PYTHON_ZIP% -d %BITDUST_HOME%
if %errorlevel% neq 0 goto DEPLOY_ERROR
:PythonInstalled


echo ##### Prepare Git binaries
if exist %GIT_EXE% goto GitInstalled
echo Extracting Git binaries
%UNZIP_EXE% -o -q %GIT_ZIP% -d %BITDUST_HOME%
if %errorlevel% neq 0 goto DEPLOY_ERROR
:GitInstalled
rem echo Git binaries now located in %BITDUST_HOME%\git


echo ##### Prepare BitDust source code files
if not exist %BITDUST_HOME%\src mkdir %BITDUST_HOME%\src


cd /D %BITDUST_HOME%\src


if exist %BITDUST_HOME%\src\bitdust.py goto SourcesExist
echo ##### Downloading BitDust source code from Git repository
%BITDUST_HOME%\git\bin\git.exe clone -q --depth 1 %BITDUST_GIT_REPO% .
if %errorlevel% neq 0 goto DEPLOY_ERROR


:SourcesExist
echo ##### Updating BitDust source code from Git repository
rem %BITDUST_HOME%\git\bin\git.exe clean -q -d -f -x .
rem if %errorlevel% neq 0 goto DEPLOY_ERROR
rem echo Running command "git fetch" in BitDust repository
%BITDUST_HOME%\git\bin\git.exe fetch --all
if %errorlevel% neq 0 goto DEPLOY_ERROR
rem echo Running command "git reset" in BitDust repository
%BITDUST_HOME%\git\bin\git.exe reset --hard origin/master
if %errorlevel% neq 0 goto DEPLOY_ERROR


echo ##### Prepare Python virtual environment
if exist %BITDUST_HOME%\venv\Scripts\pip.exe goto VenvUpdate
echo Creating BitDust virtual environment
%PYTHON_EXE% bitdust.py install
if %errorlevel% neq 0 goto DEPLOY_ERROR
goto VenvOk
:VenvUpdate
rem TODO: this is slow and can fail if user is offline...
rem this actually must be only executed when requirements.txt was changed
echo ##### Update Python virtual environment
%BITDUST_HOME%\venv\Scripts\pip.exe install -U -r %BITDUST_HOME%\src\requirements.txt
if %errorlevel% neq 0 goto DEPLOY_ERROR
:VenvOk


cd /D %BITDUST_HOME%


echo ##### Prepare BitDustNode process
if exist %BITDUST_NODE% goto BitDustNodeExeExist
copy /B /Y %BITDUST_HOME%\venv\Scripts\pythonw.exe %BITDUST_NODE%
rem echo Copied %BITDUST_HOME%\venv\Scripts\pythonw.exe to %BITDUST_NODE% 
:BitDustNodeExeExist


echo ##### Prepare BitDustConsole process
if exist %BITDUST_NODE_CONSOLE% goto BitDustConsoleExeExist
copy /B /Y %BITDUST_HOME%\venv\Scripts\python.exe %BITDUST_NODE_CONSOLE%
rem echo Copied %BITDUST_HOME%\venv\Scripts\python.exe to %BITDUST_NODE_CONSOLE% 
:BitDustConsoleExeExist


echo ##### Prepare BitDust UI source files
if not exist %BITDUST_HOME%\ui mkdir %BITDUST_HOME%\ui

if exist %BITDUST_HOME%\ui\index.html goto UISourcesExist
echo Downloading BitDust UI files from GitHub repository
%BITDUST_HOME%\git\bin\git.exe clone -q --single-branch --branch gh-pages --depth 1 https://github.com/bitdust-io/ui.git ui
if %errorlevel% neq 0 goto DEPLOY_ERROR
:UISourcesExist


cd /D %BITDUST_HOME%\ui\


rem echo ##### Running command "git clean" in BitDust UI repository
rem %BITDUST_HOME%\git\bin\git.exe clean -q -d -f -x .
rem if %errorlevel% neq 0 goto DEPLOY_ERROR
rem echo Running command "git fetch" in BitDust UI repository
%BITDUST_HOME%\git\bin\git.exe fetch --all
if %errorlevel% neq 0 goto DEPLOY_ERROR
rem echo Running command "git reset" in BitDust UI repository
%BITDUST_HOME%\git\bin\git.exe reset --hard origin/gh-pages
if %errorlevel% neq 0 goto DEPLOY_ERROR


echo ##### SUCCESS
goto DEPLOY_SUCCESS


:DEPLOY_ERROR
echo ##### DEPLOYMENT FAILED
echo.
exit /b %errorlevel%


:DEPLOY_SUCCESS
echo ##### Starting BitDust as a daemon process
cd /D "%BITDUST_HOME%"
%BITDUST_NODE% %BITDUST_HOME%\src\bitdust.py daemon
cd /D "%CURRENT_PATH%"
echo DONE
echo.
