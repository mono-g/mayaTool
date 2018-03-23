#!/usr/bin/env python
# -*- coding: utf-8 -*-
##########################################################
#
#  @brief  clean up preference
#  @file   cleanup_preference.py
#  @author Satoshi Gonokami
#
#  Copyright(C) 2018 Satoshi Gonokami.
#
#  [log]\n
#  2018/03/22 作成\n
#
##########################################################
from __future__ import absolute_import, division, print_function
import os
import sys
import shutil
import subprocess
from datetime import datetime

scriptDir = os.path.abspath(os.path.dirname(__file__)).replace('\\', '/')
prefDir = os.environ['USERPROFILE'].replace('\\', '/') + '/Documents/maya/[mayaVer]/prefs'
mayaexe = os.path.dirname(os.environ['MAYA_LOCATION']) + '/Maya[mayaVer]/bin/maya.exe'
windowPrefFiles = ['shelves',
                   'windowPrefs.mel']
hotkeyPrefFiles = ['hotkeys',
                   'userRunTimeCommands.mel', # ちょっと怪しい
                   'userNamedCommands.mel']


# ---------------------------------------------------------
# make directory (if directory doesn't exist)
# ---------------------------------------------------------
# @param <str>directory : directory
# @return None
def makeDir(directory):

    if not os.path.exists(directory):
        os.makedirs(directory)
        print("# make Directory : '" + directory + "' #")


# ---------------------------------------------------------
# check process name
# ---------------------------------------------------------
# @param <str>procName : process name
# @return <str/List>pidList : pid list
def checkProcess(procName):

    procParamList = []
    pidList = []
    cmd = ['tasklist', '/FO', 'CSV', '/NH', '/FI', ('IMAGENAME eq ' + procName + '.exe')]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    for line in proc.stdout:
        procParamList.append(line.replace("\r\n", '').replace('"', '').split(","))
    for pparam in procParamList:
        if len(pparam) > 1:
            pidList.append(pparam[1])

    return pidList


# ---------------------------------------------------------
# task kill by PID
# ---------------------------------------------------------
# @param <str>pid : process ID
# @return <bool>
def taskKill(pid):
    killcmd = ['taskkill', '/pid', pid, '/f']
    try:
        subprocess.Popen(killcmd)
        return True
    except Exception:
        return False


# ---------------------------------------------------------
# back up directory
# ---------------------------------------------------------
# @param <str>tgtDir : target directory
# @return <str>backDir : back up directory
def backupDirs(tgtDir):
    filetimestamp = os.stat(tgtDir).st_mtime
    filetime = datetime.fromtimestamp(filetimestamp).strftime('%Y%m%d%H%M')
    backDir = tgtDir + '_' + filetime
    try:
        os.rename(tgtDir, backDir)
        # prefsフォルダを見て引継ぐかどうかを決めるので、あらかじめ作っておいてダイアログ出さないように
        makeDir(tgtDir)
        return backDir
    except Exception:
        print("## ERR : Couldn't back up preference ##")
        return None


# ---------------------------------------------------------
# start up  and close maya
# ---------------------------------------------------------
# @param <str>mayaVer : maya version
# @return None
def runMaya(mayaVer):
    global mayaexe
    curMayaexe = mayaexe.replace('[mayaVer]', mayaVer)
    cmd = [curMayaexe.replace('maya.exe', 'mayabatch.exe'), '-command', 'quit -force;']
    pipe = subprocess.Popen(cmd, stderr=subprocess.PIPE)
    outs, errs = pipe.communicate()


# ---------------------------------------------------------
# copy setting files
# ---------------------------------------------------------
# @param <str>curPrefDir : preference dorectory
# @param <str>backDir : back up directory
# @param <bool>hkeyFlag : flag restoring hotkey
# @return None
def copySetting(curPrefDir, backDir, hkeyFlag=True):

    global windowPrefFiles
    global hotkeyPrefFiles
    if hkeyFlag is True:
        tgPrefFiles = windowPrefFiles + hotkeyPrefFiles
    else:
        tgPrefFiles = windowPrefFiles
    for tpref in tgPrefFiles:
        backPrefpath = backDir + '/' + tpref
        prefpath = curPrefDir + '/' + tpref
        if os.path.exists(backPrefpath):
            if os.path.isdir(backPrefpath):
                if os.path.exists(prefpath):
                    shutil.rmtree(prefpath)
                shutil.copytree(backPrefpath, prefpath)
            else:
                shutil.copy2(backPrefpath, prefpath)


# ---------------------------------------------------------
# main
# ---------------------------------------------------------
# @param <str>mayaVer : maya version
# @param <bool>hkeyFlag : flag restoring hotkey
# @return None
def main(mayaVer, hkeyFlag=True):

    global prefDir

    # err check
    if not mayaVer.isdigit():
        print("## ERR : Please Enter a Number ##")
        return
    curPrefDir = prefDir.replace('[mayaVer]', mayaVer)
    if not os.path.exists(curPrefDir):
        print("## ERR : Please Enter Installed Maya version ##")
        return

    # close maya
    pidList = checkProcess('maya')
    if pidList:
        print("# Maya is Runnnig. #")
        print("# May I force shut-down Maya? #")
        inputStr = raw_input('>> y/n :')
        if inputStr == 'y' or inputStr == 'yes':
            for pid in pidList:
                taskKill(pid)
        else:
            print("# Canceled Task. #")
            print("# Please shut-down Maya. #")
            return

    # back up prefs
    backDir = backupDirs(curPrefDir)
    if backDir is None:
        return

    # start up maya
    pipe = runMaya(mayaVer)

    # copy setting files
    copySetting(curPrefDir, backDir, hkeyFlag)


# ----------------------------------------------------------------------------
if __name__ == '__main__':
    if (sys.argv[2] == 'True' or
       sys.argv[2] == '1'):
        argv = True
    elif sys.argv[2] == '0':
        argv = False
    else:
        argv = False
    
    main(sys.argv[1], argv)
