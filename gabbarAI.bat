@echo off
REM Ensure we're in the directory of the script
cd /d "%~dp0"

REM Define paths
set SCRIPT_PATH=%~f0
set SCRIPT_NAME=%~nx0
set SHORTCUT_NAME=Gabbar AI.lnk
set ICON_PATH=%~dp0gabbar-ai\assets\img\logo.ico
set DESKTOP=%USERPROFILE%\Desktop
set SHORTCUT_PATH=%DESKTOP%\%SHORTCUT_NAME%

REM Check if shortcut already exists
if not exist "%SHORTCUT_PATH%" (
    echo Creating shortcut on Desktop...

    REM Create VBS script to generate the shortcut
    set VBS_FILE=%TEMP%\create_shortcut.vbs
    > "%VBS_FILE%" echo Set oWS = WScript.CreateObject("WScript.Shell")
    >> "%VBS_FILE%" echo sLinkFile = "%SHORTCUT_PATH%"
    >> "%VBS_FILE%" echo Set oLink = oWS.CreateShortcut(sLinkFile)
    >> "%VBS_FILE%" echo oLink.TargetPath = "%SCRIPT_PATH%"
    >> "%VBS_FILE%" echo oLink.WorkingDirectory = "%~dp0"
    >> "%VBS_FILE%" echo oLink.IconLocation = "%ICON_PATH%"
    >> "%VBS_FILE%" echo oLink.Save

    REM Run the VBS script to create the shortcut
    cscript //nologo "%VBS_FILE%"

    REM Delete the temporary VBS script
    del "%VBS_FILE%"
)

REM Run the Python module
python -m gabbar-ai

pause
