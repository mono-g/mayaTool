@echo off

cd /d %~dp0
SET CURRENTDIR=%CD%
SET PYTHONPATH=%PYTHONPATH%;%CD%;

rem check installed maya
for /F "tokens=2,*" %%I in ('reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" /s ^| find "Autodesk Maya"') do (
    SET mayaInstalled=%%J
)
echo Installed %mayaInstalled%
if "%mayaInstalled%" == "" (
    echo Maya is not installed
    goto end
)
for /F "usebackq tokens=3" %%I in (`echo %mayaInstalled%`) do (
    SET mayaInstallVer=%%I
)
for /F "usebackq tokens=1 delims==." %%I in (`echo %mayaInstallVer%`) do (
    SET mayaVer=%%I
)
SET PYTHONEXE="%PROGRAMW6432%\Autodesk\Maya%mayaVer%\bin\mayapy.exe"

rem main
echo.
echo ===============================================================================
echo.
echo                             Clean up Maya preference
echo.
echo ===============================================================================
echo.

SET hKeyFlg=True
SET /P mayaVer="set Maya version: "
echo Maya version = %mayaVer%
%PYTHONEXE% %CURRENTDIR%\cleanup_preference.py "%mayaVer%" %hKeyFlg%

:end
pause
