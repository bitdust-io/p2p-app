@echo off

set BITDUST_GIT_REPO=https://github.com/bitdust-io/public.git

set _my_datetime=%date%_%time%
set _my_datetime=%_my_datetime: =_%
set _my_datetime=%_my_datetime::=%
set _my_datetime=%_my_datetime:/=_%
set _my_datetime=%_my_datetime:.=_%

set BITDUST_FULL_HOME=%HOMEDRIVE%%HOMEPATH%\.bitdust
rem TODO : to be able to correctly detect existing ".bitdust" folder need to check "appdata" file as well

if not exist "%BITDUST_FULL_HOME%" echo Prepare destination folder
if not exist "%BITDUST_FULL_HOME%" mkdir "%BITDUST_FULL_HOME%"


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


set BITDUST_NODE=%BITDUST_HOME%\venv\Scripts\bitdust-node.exe
set BITDUST_NODE_CONSOLE=%BITDUST_HOME%\venv\Scripts\bitdust-console.exe


set PYTHON_EXE=%BITDUST_HOME%\python\python.exe
set GIT_EXE=%BITDUST_HOME%\git\bin\git.exe


if /I "%~1"=="stop" goto StopBitDustGo
goto RestartBitDust
:StopBitDustGo
echo ##### Preparing to stop BitDust Node
cd /D "%BITDUST_HOME%"
if not exist %BITDUST_NODE_CONSOLE% goto KillBitDust
%BITDUST_NODE_CONSOLE% %BITDUST_HOME%\src\bitdust.py stop
if %errorlevel% neq 0 goto KillBitDust
goto BitDustStopped
:KillBitDust
taskkill /IM bitdust-node.exe /F /T 2>nul 1>nul
taskkill /IM bitdust-console.exe /F /T 2>nul 1>nul
:BitDustStopped
echo ##### Done
exit /b %errorlevel%


:RestartBitDust
if /I "%~1"=="restart" goto RestartBitDustGo
goto RedeployBitDust
:RestartBitDustGo
echo ##### Preparing to restart BitDust Node
cd /D "%BITDUST_HOME%"
if not exist %BITDUST_NODE_CONSOLE% goto BitDustRestarted
%BITDUST_NODE_CONSOLE% %BITDUST_HOME%\src\bitdust.py restart
if %errorlevel% neq 0 goto DEPLOY_ERROR
:BitDustRestarted
echo ##### Done
exit /b %errorlevel%


:RedeployBitDust
if /I "%~1"=="redeploy" goto RedeployBitDustGo
goto StartBitDust
:RedeployBitDustGo
echo ##### Preparing to redeploy BitDust Node
rmdir /S /Q %BITDUST_HOME%\venv
rmdir /S /Q %BITDUST_HOME%\src
echo ##### Cleanup finished


:StartBitDust


if not exist %BITDUST_HOME%\src mkdir %BITDUST_HOME%\src
if exist %BITDUST_HOME%\src\bitdust.py goto SourcesExist
echo ##### Downloading source code files from Git repository
cd /D "%BITDUST_HOME%\src"
%BITDUST_HOME%\git\bin\git.exe -c http.sslBackend=schannel clone -q --depth 1 %BITDUST_GIT_REPO% .
if %errorlevel% neq 0 goto DEPLOY_ERROR


:SourcesExist
echo ##### Updating source code files from Git repository
cd /D "%BITDUST_HOME%\src"
%BITDUST_HOME%\git\bin\git.exe -c http.sslBackend=schannel fetch --all
if %errorlevel% neq 0 goto DEPLOY_ERROR
%BITDUST_HOME%\git\bin\git.exe -c http.sslBackend=schannel reset --hard origin/master
if %errorlevel% neq 0 goto DEPLOY_ERROR


if exist %BITDUST_HOME%\venv\Scripts\pip.exe goto VenvUpdate
echo ##### Building Python virtual environment
cd /D "%BITDUST_HOME%\src"
%PYTHON_EXE% bitdust.py install
if %errorlevel% neq 0 goto DEPLOY_ERROR
goto VenvOk
:VenvUpdate


echo ##### Updating Python virtual environment
%BITDUST_HOME%\venv\Scripts\pip.exe install -U -r %BITDUST_HOME%\src\requirements.txt
if %errorlevel% neq 0 goto DEPLOY_ERROR
:VenvOk


if exist %BITDUST_NODE% goto BitDustNodeExeExist
cd /D %BITDUST_HOME%\venv\Scripts
copy /B /Y pythonw.exe %BITDUST_NODE%
copy /B /Y %BITDUST_HOME%\python\bitdust.ico %BITDUST_HOME%\venv\Scripts
%BITDUST_HOME%\python\rcedit.exe %BITDUST_NODE% --set-icon bitdust.ico --set-version-string FileDescription "BitDust Node"
:BitDustNodeExeExist


if exist %BITDUST_NODE_CONSOLE% goto BitDustConsoleExeExist
cd /D %BITDUST_HOME%\venv\Scripts\pythonw.exe
copy /B /Y python.exe %BITDUST_NODE_CONSOLE%
copy /B /Y %BITDUST_HOME%\python\bitdust.ico %BITDUST_HOME%\venv\Scripts
%BITDUST_HOME%\python\rcedit.exe %BITDUST_NODE_CONSOLE% --set-icon bitdust.ico --set-version-string FileDescription "BitDust Console"
:BitDustConsoleExeExist


echo ##### Environment successfully prepared
goto DEPLOY_SUCCESS


:DEPLOY_ERROR
echo ##### FAILED
echo.
exit /b %errorlevel%


:DEPLOY_SUCCESS
echo ##### Starting BitDust Node process
cd /D "%BITDUST_HOME%"
%BITDUST_NODE% %BITDUST_HOME%\src\bitdust.py daemon


echo ##### Ready
echo.
