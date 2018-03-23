@echo off

cd /d %~dp0
SET CURRENTDIR=%CD%
SET PYTHONPATH=%PYTHONPATH%;%CD%;
SET mayaVer=2018
SET PYTHONEXE="C:\Program Files\Autodesk\Maya%mayaVer%\bin\mayapy.exe"

echo.
echo ===============================================================================
echo.
echo                             Clean up Maya preference
echo.
echo ===============================================================================
echo.

SET /P mayaVer="set Maya version: "
echo Maya version = %mayaVer%
%PYTHONEXE% %CURRENTDIR%\cleanup_preference.py "%mayaVer%"
pause

