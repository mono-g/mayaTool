#!/usr/bin/env python
# -*- coding: utf-8 -*-
##########################################################
#
#  @brief  tool installer
#  @file   install_mayaTool.py
#  @author Satoshi Gonokami
#
#  Copyright(C) 2018 Satoshi Gonokami.
#
#  [log]\n
#  2018/03/15 作成\n
#
##########################################################
from __future__ import absolute_import, division, print_function
import os
import sys
import shutil
import glob

scriptDir = os.path.abspath(os.path.dirname(__file__)).replace('\\', '/')
projDir = os.path.abspath(os.path.join(scriptDir, u"../../../../..")).replace('\\', '/')
projName = 'projName'
shelfDir = os.environ['USERPROFILE'].replace('\\', '/') + '/Documents/maya/[mayaVer]/prefs/shelves'
shelfMelFile = 'shelf_' + projName + '.mel'
toolGUICmd = 'import [toolName].gui as [toolName]ui;reload([toolName]ui)\\n'
toolGUICmd += '[toolName]Window = [toolName]ui.toolGUI()\\n'
toolGUICmd += '[toolName]Window.show()'
shelfMel = '''global proc shelf_[projName] () {
    global string $gBuffStr;
    global string $gBuffStr0;
    global string $gBuffStr1;


[shelfBtnCmd]

}''' 
shelfMel = shelfMel.replace('[projName]', projName)
shelfBtnCmd = '''shelfButton
    -enableCommandRepeat 1
    -enable 1
    -width 34
    -height 34
    -manage 1
    -visible 1
    -preventOverride 0
    -annotation "[scriptName]"
    -enableBackground 0
    -backgroundColor 0 0 0
    -highlightColor 0.321569 0.521569 0.65098
    -align "center"
    -label "[scriptName]"
    -labelOffset 0
    -rotation 0
    -flipX 0
    -flipY 0
    -useAlpha 1
    -font "plainLabelFont"
    -imageOverlayLabel "[shortScriptName]"
    -overlayLabelColor 0.8 0.8 0.8
    -overlayLabelBackColor 0 0 0 0.5
    -image "pythonFamily.png"
    -image1 "pythonFamily.png"
    -style "iconOnly"
    -marginWidth 1
    -marginHeight 1
    -command "import sys\\nsys.path.append('[toolDir]')\\n[toolCmd]\\n"
    -sourceType "python"
    -commandRepeatable 1
    -flat 1
;'''
shelfBtnCmd = '    ' + shelfBtnCmd
shelfBtnCmd = shelfBtnCmd.replace('\n', '\n    ')
shelfBtnCmd = shelfBtnCmd.replace('\\n    ', '\\n')


# ---------------------------------------------------------
# check shelf
# ---------------------------------------------------------
# @param <str>toolName : tool name
# @param <str>mayaVer : maya version
# @return <bool>result : if exist tool, True
def checkShelf(toolName, mayaVer):

    global shelfDir
    result = False
    shelfPath = shelfDir.replace('[mayaVer]', mayaVer) + '/shelf_*.mel'
    shelfMelList = glob.glob(shelfPath)
    for shmel in shelfMelList:
        f = open(shmel, 'r')
        with f:
            shelfStr = f.read()
        if '"' + toolName + '"' in shelfStr:
            result = True

    return result


# ---------------------------------------------------------
# make short name
# ---------------------------------------------------------
# @param <str>toolName : tool name
# @return <str>shortName : short name
def makeShortName(toolName):

    checkStrs = ['_', '-', ' ']
    noSpaceName = ''
    for cstr in checkStrs:
        namesplit = toolName.split(cstr)
        if len(namesplit) > 1:
            for toolword in namesplit:
                if not noSpaceName:
                    noSpaceName = toolword
                else:
                    noSpaceName += toolword[0].upper() + toolword[1:]
        else:
            if not noSpaceName:
                noSpaceName = namesplit[0]

    shortNameTmp = noSpaceName[0]
    for nsstr in noSpaceName:
        if nsstr.isupper():
            shortNameTmp += nsstr
    if len(shortNameTmp) < 2:
        shortName = toolName[:4]
    elif len(shortNameTmp) > 4:
        shortName = shortNameTmp[:4]
    else:
        shortName = shortNameTmp

    return shortName


# ---------------------------------------------------------
# make shelf command
# ---------------------------------------------------------
# @param <str>toolName : tool name
# @param <str>mayaVer : maya version
# @param <str>cmdOwrite : set tool command
# @return <str>shelfStr : shelf mel string
def makeShelfCmd(toolName, mayaVer, cmdOwrite=None):

    global shelfDir
    global shelfMel
    global shelfBtnCmd
    global shelfMelFile
    global toolGUICmd

    # make tool Button command
    shelfPath = shelfDir.replace('[mayaVer]', mayaVer) + '/' + shelfMelFile
    if cmdOwrite is None:
        toolCmd = toolGUICmd.replace('[toolName]', toolName)
    shortName = makeShortName(toolName)
    toolBtnCmd = shelfBtnCmd.replace('[toolDir]', scriptDir)
    toolBtnCmd = toolBtnCmd.replace('[scriptName]', toolName)
    toolBtnCmd = toolBtnCmd.replace('[shortScriptName]', shortName)
    toolBtnCmd = toolBtnCmd.replace('[toolCmd]', toolCmd)

    if os.path.exists(shelfPath):
        f = open(shelfPath, 'r')
        with f:
            shelfLines = f.readlines()
        shelfBtnCmdTemp = ''
        remFlg = False
        for sline in shelfLines:
            if 'shelfButton' in sline:
                shelfBtnCmdTemp += sline
                remFlg = True
            elif (remFlg is True and
                  ';' in sline):
                shelfBtnCmdTemp += sline
                remFlg = False
            elif remFlg is True:
                shelfBtnCmdTemp += sline
        if not '"' + toolName + '"' in shelfBtnCmdTemp:
            toolBtnCmd = shelfBtnCmdTemp + toolBtnCmd
    shelfStr = shelfMel.replace('[shelfBtnCmd]', toolBtnCmd)

    return shelfStr


# ---------------------------------------------------------
# make shelf
# ---------------------------------------------------------
# @param <str>shelfStr : shelf mel string
# @param <str>mayaVer : maya version
# @return None
def makeShelf(shelfStr, mayaVer):
    shelfPath = shelfDir.replace('[mayaVer]', mayaVer) + '/' + shelfMelFile
    # back up
    if os.path.exists(shelfPath):
        backupPath = shelfPath.replace('.mel', '.mel.backup')
        if os.path.exists(backupPath):
            os.remove(backupPath)
        shutil.move(shelfPath, backupPath)
        print("# backup : '" + backupPath + "' #")

    # main
    f = open(shelfPath, 'w')
    with f:
        f.write(shelfStr)


# ---------------------------------------------------------
# main
# ---------------------------------------------------------
# @param <str>toolName : tool name
# @param <str>mayaVer : maya version
# @param <str>cmdOwrite : set tool command
# @return None
def main(toolName, mayaVer, cmdOwrite=None):
    # check shelf
    if checkShelf(toolName, mayaVer) is False:
        # make shelf
        shelfStr = makeShelfCmd(toolName, mayaVer, cmdOwrite)
        makeShelf(shelfStr, mayaVer)


# ----------------------------------------------------------------------------
if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
