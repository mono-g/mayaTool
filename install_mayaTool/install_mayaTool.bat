@echo off

SET CURRENTDIR=%CD%
SET PYTHONPATH=%PYTHONPATH%;%CD%;
SET mayaVer=2018
SET PYTHONEXE="C:\Program Files\Autodesk\Maya%mayaVer%\bin\mayapy.exe"
SET toolName="toolName"
SET toolDir=C:/proj/Tool/Maya/%mayaVer%/python/*

echo.
echo ===============================================================================
echo.
echo                              Install mayaTool
echo.
echo ===============================================================================
echo.

%PYTHONEXE% %CURRENTDIR%\instal_mayaTool.py %toolName% "%mayaVer%"
p4 sync -f %toolDir%
pause

