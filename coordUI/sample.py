#!/usr/bin/env python
# -*- coding: utf-8 -*-
# #########################################################
#
#  @brief  coordinate GUI
#  @file   gui.py
#  @author Satoshi Gonokami
#
#  Copyright(C) 2019 Satoshi Gonokami.
#
# #########################################################
from __future__ import absolute_import, division

import glob
import os

from PySide2 import QtGui
from PySide2 import QtWidgets
from PySide2 import QtCore
try:
    import shiboken2
except ImportError:
    from PySide2 import shiboken2
import maya.cmds as cmds
import maya.OpenMayaUI as omUI


# path
scriptName = os.path.basename(os.path.dirname(__file__))
scriptDir = os.path.abspath(os.path.dirname(__file__)).replace('\\', '/')


# ---------------------------------------------------------
# mayaUI to pyside(thanks to takkyun)
# ---------------------------------------------------------
# @param <str>name    : maya UI name
# @param <type>toType : pyside type
# @return <obj> : pyside obj
def mayaToPySide(name, toType):

    ptr = omUI.MQtUtil.findControl(name)
    if not ptr:
        ptr = omUI.MQtUtil.findLayout(name)    
    if not ptr:
        ptr = omUI.MQtUtil.findMenuItem(name)
    if not ptr:
        return None
 
    return shiboken2.wrapInstance(long(ptr), toType)


# ---------------------------------------------------------
# window
# ---------------------------------------------------------
class toolGUI(object):
    windowName = 'coordWindow'
    windowTitle = 'Coordinate window'
    tabName = ['Coordinate']
    icName = 'coord'
    thumbName = '[coordID].png'
    defWidth = 510
    defHeight = 530
    thumbWidth = 500
    thumbHeight = 500
    oMenuWidth = 100
    runBtnCol = [0.120, 0.200, 0.350]
    thumbnailPath = scriptDir + '/img'

    # ---------------------------------------------------------
    # init
    # ---------------------------------------------------------
    # @param None
    # @return None
    def __init__(self):
        if cmds.window(self.windowName, exists=True):
            cmds.deleteUI(self.windowName)

    # ---------------------------------------------------------
    # thumbnail : get imageItem from scene
    # ---------------------------------------------------------
    # @param <QtWidgets.QGraphicsScene>scene : scene object
    # @return <QtWidgets.QGraphicsPixmapItem/List>bgimgList : image object
    def getImgItemFromScn(self, scene):
        bgimgList = []
        for item in scene.items():
            if type(item) == QtWidgets.QGraphicsPixmapItem:
                bgimgList.append(item)
        return bgimgList

    # ---------------------------------------------------------
    # thumbnail : load thumbnail
    # ---------------------------------------------------------
    # @param <bool>keepGviewTrans : keep Gview transform
    # @return None
    def loadThumb(self, keepGviewTrans=False):
        widthHeight = [self.thumbWidth, self.thumbHeight]
        hairID = os.path.basename(glob.glob(self.thumbnailPath + '/*_[hH]air*')[0]).split('.')[0]
        headID = os.path.basename(glob.glob(self.thumbnailPath + '/*_[hH]ead*')[0]).split('.')[0]
        legID = os.path.basename(glob.glob(self.thumbnailPath + '/*_[lL]eg*')[0]).split('.')[0]
        bodyID = os.path.basename(glob.glob(self.thumbnailPath + '/*_[bB]ody*')[0]).split('.')[0]
        acceID = 'None'
        # check thumbnail path
        thumPathList = []
        imagepath = self.thumbnailPath + '/' + self.thumbName
        for partid in [headID, bodyID, legID, hairID, acceID]:
            thumbPath = imagepath.replace('[coordID]', partid)
            if not os.path.exists(thumbPath):
                thumbPath = ''
            thumPathList.append(thumbPath)
        # reload this UI
        self.reloadPicture(thumPathList, self.coordThumbnailLayout,
                           widthHeight, keepGviewTrans)

    # ---------------------------------------------------------
    # pictureWidget : reload picture widget
    # ---------------------------------------------------------
    # @param <str/List>imgpathList : image path
    # @param <obj>parent           : parent Layout
    # @param <int/List>wh          : width and height
    # @param <bool>keepGviewTrans  : keep Gview transform
    # @return None
    def reloadPicture(self, imgpathList, parent, wh, keepGviewTrans=False):
        pixmapList = []
        gView = self.coordGView
        thumbScn = self.coordThumbScene

        # resize
        for imagepath in imgpathList:
            pixmap = QtGui.QPixmap(imagepath)
            picWidth = pixmap.size().width()
            picHeight = pixmap.size().height()
            if picWidth == 0:
                pass
            elif picWidth > picHeight:
                pixmap = pixmap.scaledToWidth(wh[0])
                xsize = wh[0]
                ysize = pixmap.size().height()
                scale = (wh[0] - 16) / pixmap.size().width()
            else:
                pixmap = pixmap.scaledToHeight(wh[1])
                xsize = pixmap.size().width()
                ysize = wh[1]
                scale = (wh[1] - 8) / pixmap.size().height()
            pixmapList.append(pixmap)
        if keepGviewTrans is False:
            gView.resetTransform()
            gView.scale(scale, scale)
        colWidth = (wh[0] - xsize) / 2
        if keepGviewTrans is False:
            gView.resize(wh[0], ysize)
            gView.translate(colWidth, 0)
        thumbScn.setSceneRect(0, 0, xsize, ysize)
        cmds.columnLayout(parent, e=True, h=ysize)
        gView.update()

        # set image
        bgimgList = self.getImgItemFromScn(thumbScn)
        for n, pixmap in enumerate(pixmapList):
            bgimgList[n].setPixmap(pixmap)
        else:
            bgimgList[0].setPixmap(pixmapList[0])

    # ---------------------------------------------------------
    # UI : coord frame layout
    # ---------------------------------------------------------
    # @param <uiObj>parent : parent UI
    # @return <uiObj>coordformLayout : form layout
    def frame_coord(self, parent):
        coordformLayout = cmds.formLayout(p=parent)
        # thumbnail row
        self.coordThumbnailLayout = cmds.columnLayout(adj=False, p=coordformLayout)
        thumbLayoutPyside = mayaToPySide(self.coordThumbnailLayout, QtWidgets.QWidget)
        self.coordGView = QtWidgets.QGraphicsView(thumbLayoutPyside)
        # self.coordGView.setParent(thumbLayoutPyside)
        self.coordThumbScene = QtWidgets.QGraphicsScene()
        self.coordThumbScene.clear()
        # self.coordThumbScene.addPixmap(QtGui.QPixmap(self.thumbnailPath + '/uc01.png'))
        self.coordThumbScene.addPixmap(QtGui.QPixmap())
        self.coordThumbScene.addPixmap(QtGui.QPixmap())
        self.coordThumbScene.addPixmap(QtGui.QPixmap())
        self.coordThumbScene.addPixmap(QtGui.QPixmap())
        self.coordThumbScene.addPixmap(QtGui.QPixmap())
        self.coordGView.setScene(self.coordThumbScene)
        cmds.setParent(coordformLayout)
        # # size 
        # self.coordGView.resize(self.thumbWidth, self.thumbHeight)
        # cmds.columnLayout(self.coordThumbnailLayout, e=True, w=self.thumbWidth, h=self.thumbHeight)

        # coord frame formLayout
        cmds.formLayout(coordformLayout, e=True, ap=[self.coordThumbnailLayout, 'top', 0, 0])
        cmds.formLayout(coordformLayout, e=True, af=[self.coordThumbnailLayout, 'left', 0])
        cmds.formLayout(coordformLayout, e=True, af=[self.coordThumbnailLayout, 'right', 0])
        cmds.setParent('..')

    # ---------------------------------------------------------
    # UI : coord Tab layout
    # ---------------------------------------------------------
    # @param None
    # @return <uiObj>coordTabcLayout : tab layout
    def tab_coord(self):
        coordTabcLayout = cmds.columnLayout(adj=1, p=self.alltabLayout)
        # coord frame
        self.frame_coord(coordTabcLayout)

        return coordTabcLayout

    # ---------------------------------------------------------
    # UI : show window
    # ---------------------------------------------------------
    # @param None
    # @return None
    def show(self):
        windowlayout = cmds.window(self.windowName, title=self.windowTitle,
                                   iconName=self.icName, menuBar=True)
        # window layout
        allformLayout = cmds.formLayout()
        self.alltabLayout = cmds.tabLayout(p=allformLayout)
        # build coord Tab
        coordTabcLayout = self.tab_coord()
        # set tab
        cmds.tabLayout(self.alltabLayout, e=True,
                        tabLabel=((coordTabcLayout, self.tabName[0])))
        # all form
        cmds.formLayout(allformLayout, e=True, af=[self.alltabLayout, 'top', 0])
        cmds.formLayout(allformLayout, e=True, af=[self.alltabLayout, 'left', 0])
        cmds.formLayout(allformLayout, e=True, af=[self.alltabLayout, 'right', 0])
        cmds.formLayout(allformLayout, e=True, af=[self.alltabLayout, 'bottom', 0])
        cmds.setParent('..')
        cmds.showWindow()

        cmds.window(self.windowName, e=True, w=self.defWidth, h=self.defHeight)
        self.loadThumb()

# import sys
# sys.path.append(r'E:\_gonokami\scripts\python\maya\tools\tool_git')
# import coordUI.sample as cogui;reload(cogui)
# gui = cogui.toolGUI()
# gui.show()
