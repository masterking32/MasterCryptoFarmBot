@echo off
setlocal enabledelayedexpansion

:: Set variables for easy updating
set "GIT_VERSION=2.47.0"
set "DOWNLOAD_URL=https://github.com/git-for-windows/git/releases/download/v%GIT_VERSION%.windows.1/Git-%GIT_VERSION%-64-bit.exe"
set "INSTALLER_NAME=Git-%GIT_VERSION%-64-bit.exe"

set "TEMP_DIR=%TEMP%\GitInstall_%RANDOM%"
mkdir "%TEMP_DIR%"
if %errorlevel% neq 0 (
    echo Failed to create temporary GIT install directory.
    timeout /t 5
    exit /b 1
)

cd /d "%TEMP_DIR%"
if %errorlevel% neq 0 (
    echo Failed to change to temporary GIT install directory.
    timeout /t 5
    exit /b 1
)

echo Downloading %INSTALLER_NAME%...
powershell -Command "$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -OutFile '%INSTALLER_NAME%' -Uri '%DOWNLOAD_URL%'"
if %errorlevel% neq 0 (
    echo Failed to download GIT installer.
    goto :error
)

echo Creating temporary git_options.ini file...
(
echo [Setup]
echo Lang=default
echo Dir=C:\Program Files\Git
echo Group=Git
echo NoIcons=0
echo SetupType=default
echo Components=ext,ext\shellhere,ext\guihere,gitlfs,assoc,assoc_sh
echo Tasks=
echo EditorOption=VIM
echo CustomEditorPath=
echo DefaultBranchOption=main
echo PathOption=Cmd
echo SSHOption=OpenSSH
echo TortoiseOption=false
echo CURLOption=OpenSSL
echo CRLFOption=CRLFAlways
echo BashTerminalOption=ConHost
echo GitPullBehaviorOption=Merge
echo UseCredentialManager=Enabled
echo PerformanceTweaksFSCache=Enabled
echo EnableSymlinks=Disabled
echo EnableFSMonitor=Disabled
) > "git_options.ini" 2>nul

if %errorlevel% neq 0 (
    echo Failed to create git_options.ini.
    goto :error
)

echo Installing %INSTALLER_NAME%...
start /wait %INSTALLER_NAME% /VERYSILENT /NORESTART /NOCANCEL /LOADINF="git_options.ini"
if %errorlevel% neq 0 (
    echo Failed to install GIT.
    goto :error
)

echo GIT installation completed successfully.
goto :cleanup

:error
echo An error occurred during the GIT installation process.
call :cleanup
exit /b 1

:cleanup
echo Cleaning up...
cd /d "%TEMP%"
if %errorlevel% neq 0 (
    echo Failed to change to temporary directory for GIT install cleanup.
)
rd /s /q "%TEMP_DIR%"
if %errorlevel% neq 0 (
    echo Failed to remove temporary GIT install directory. Please delete %TEMP_DIR% manually.
)
timeout /t 5

exit /b 0
