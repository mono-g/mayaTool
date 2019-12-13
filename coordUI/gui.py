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
# graphics view
# ---------------------------------------------------------
class GraphView(QtWidgets.QGraphicsView):
    # ---------------------------------------------------------
    # init
    # ---------------------------------------------------------
    # @param <obj>parent : parent
    # @return None
    def __init__(self, parent):
        super(GraphView, self).__init__(parent)

        # value
        self.parent = parent
        self.cursorPos = None

    # ---------------------------------------------------------
    # mouse press event
    # ---------------------------------------------------------
    # @param <event>event : event
    # @return None
    def mousePressEvent(self, event):
        # alt mode
        if event.modifiers() == QtCore.Qt.AltModifier:
            # right click menu setting
            self.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
            # mouse cursor
            self.cursorPos = event.globalPos()
            # case : click right button
            if event.button() == QtCore.Qt.RightButton:
                cursorShp = QtCore.Qt.SizeHorCursor
                QtWidgets.qApp.setOverrideCursor(QtGui.QCursor(cursorShp))
            # case : click middle button
            elif event.buttons() == QtCore.Qt.MidButton:
                cursorShp = QtCore.Qt.SizeAllCursor
                QtWidgets.qApp.setOverrideCursor(QtGui.QCursor(cursorShp))
            else:
                QtWidgets.qApp.restoreOverrideCursor()

    # ---------------------------------------------------------
    # mouse move event
    # ---------------------------------------------------------
    # @param <event>event : event
    # @return None
    def mouseMoveEvent(self, event):

        if not self.cursorPos:
            # run default function
            super(GraphView, self).mouseMoveEvent(event)
            return

        # val
        curPos = event.globalPos()
        deltaPos = curPos - self.cursorPos

        # mouse scale mode
        if event.buttons() == QtCore.Qt.RightButton:
            # dicide scale from cursor movement
            if abs(deltaPos.x()) < abs(deltaPos.y()):
                chpos = deltaPos.y()
            else:
                chpos = deltaPos.x()
            if chpos >= 0:
                scaleRatio = 1.05
            else:
                scaleRatio = 0.95
 
            localRect = self.mapToScene(curPos.x(), curPos.y())
            # move scale pivot
            trans = self.transform().translate(localRect.x(), localRect.y())
            # scale
            trans = trans.scale(scaleRatio, scaleRatio)
            # reset scale pivot
            trans = trans.translate(-localRect.x(), -localRect.y())
            # set transform
            self.setTransform(trans)
        # mouse move mode
        elif event.buttons() == QtCore.Qt.MidButton:
            hScrlBar = self.horizontalScrollBar()
            vScrlBar = self.verticalScrollBar()
            hScrlBar.setValue(hScrlBar.value() - deltaPos.x())
            vScrlBar.setValue(vScrlBar.value() - deltaPos.y())
        self.cursorPos = curPos

    # ---------------------------------------------------------
    # mouse release event
    # ---------------------------------------------------------
    # @param <event>event : event
    # @return None
    def mouseReleaseEvent(self, event):
        # run default function
        super(GraphView, self).mouseReleaseEvent(event)
        self.cursorPos = None
        # reset mouse cursor
        QtWidgets.qApp.restoreOverrideCursor()


# ---------------------------------------------------------
# window
# ---------------------------------------------------------
class toolGUI(object):
    windowName = 'coordWindow'
    windowTitle = 'Coordinate window'
    tabName = ['Coordinate']
    icName = 'coord'
    thumbName = '[coordID].png'
    defWidth = 640
    defHeight = 500
    thumbWidth = 500
    thumbHeight = 500
    oMenuWidth = 100
    runBtnCol = [0.120, 0.200, 0.350]
    thumbnailPath = scriptDir + '/img'
    uclLogo = 'UCL_logo'

    # ---------------------------------------------------------
    # init
    # ---------------------------------------------------------
    # @param None
    # @return None
    def __init__(self):
        if cmds.window(self.windowName, exists=True):
            cmds.deleteUI(self.windowName)

    # ---------------------------------------------------------
    # comboBox : reload option menu item
    # ---------------------------------------------------------
    # @param <obj>oMenu         : optionMenuGrp UI
    # @param <str/List>itemList : Item List
    # @return None
    def resetOptMenuItem(self, oMenu, itemList):
        menuitems = cmds.optionMenu(oMenu, q=True, ill=True)
        if menuitems:
            cmds.deleteUI(menuitems)
        # add items
        for item in itemList:
            itemUI = cmds.menuItem(l=item, p=oMenu)
            if item:
                cmds.menuItem(itemUI, e=True, l=item)

    # ---------------------------------------------------------
    # comboBox : reload all option menu in UI
    # ---------------------------------------------------------
    # @param None
    # @return None
    def reloadAllOptMenu(self):
        self.reloadHairOptMenu()
        self.reloadheadOptMenu()
        self.reloadlegOptMenu()
        self.reloadBodyOptMenu()
        self.reloadAcceOptMenu()

    # ---------------------------------------------------------
    # comboBox : get option menu item
    # ---------------------------------------------------------
    # @param <obj>oMenu : optionMenuGrp UI
    # @return <str>value : value
    def getOptMenuValue(self, oMenu):
        if cmds.optionMenu(oMenu, q=True, ni=True) == 0:
            value = ''
        else:
            value = cmds.optionMenu(oMenu, q=True, v=True)
        return value

    # ---------------------------------------------------------
    # comboBox : set option menu item
    # ---------------------------------------------------------
    # @param <obj>oMenu : optionMenuGrp UI
    # @param <str>value : value
    # @return None
    def setOptMenuItem(self, oMenu, value):
        if value:
            itemExst = False
            itemObjs = oMenu.getItemArray()
            if itemObjs:
                for iobj in itemObjs:
                    if value == cmds.menuItem(iobj, q=True, l=True):
                        itemExst = True
                        break
            if itemExst is True:
                oMenu.setValue(value)

    # ---------------------------------------------------------
    # comboBox : reload body option menu in UI
    # ---------------------------------------------------------
    # @param None
    # @return None
    def reloadBodyOptMenu(self):
        coordList = []
        globList = glob.glob(self.thumbnailPath + '/*_[bB]ody*')
        for gfile in globList:
            coordList.append(os.path.basename(gfile).split('.')[0])
        self.resetOptMenuItem(self.bodyOMenu, coordList)
        self.loadThumb()

    # ---------------------------------------------------------
    # comboBox : reload hair option menu in UI
    # ---------------------------------------------------------
    # @param None
    # @return None
    def reloadHairOptMenu(self):
        coordList = []
        globList = glob.glob(self.thumbnailPath + '/*_[hH]air*')
        for gfile in globList:
            coordList.append(os.path.basename(gfile).split('.')[0])
        coordList += ['None']
        self.resetOptMenuItem(self.hairOMenu, coordList)

    # ---------------------------------------------------------
    # comboBox : reload head option menu in UI
    # ---------------------------------------------------------
    # @param None
    # @return None
    def reloadheadOptMenu(self):
        coordList = []
        globList = glob.glob(self.thumbnailPath + '/*_[hH]ead*')
        for gfile in globList:
            coordList.append(os.path.basename(gfile).split('.')[0])
        self.resetOptMenuItem(self.headOMenu, coordList)

    # ---------------------------------------------------------
    # comboBox : reload leg option menu in UI
    # ---------------------------------------------------------
    # @param None
    # @return None
    def reloadlegOptMenu(self):
        coordList = []
        globList = glob.glob(self.thumbnailPath + '/*_[lL]eg*')
        for gfile in globList:
            coordList.append(os.path.basename(gfile).split('.')[0])
        self.resetOptMenuItem(self.legOMenu, coordList)

    # ---------------------------------------------------------
    # comboBox : reload acce option menu in UI
    # ---------------------------------------------------------
    # @param None
    # @return None
    def reloadAcceOptMenu(self):
        coordList = ['None']
        globList = glob.glob(self.thumbnailPath + '/*_[aA]cce*')
        for gfile in globList:
            coordList.append(os.path.basename(gfile).split('.')[0])
        self.resetOptMenuItem(self.acceOMenu, coordList)

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
        hairID = self.getOptMenuValue(self.hairOMenu)
        headID = self.getOptMenuValue(self.headOMenu)
        legID = self.getOptMenuValue(self.legOMenu)
        bodyID = self.getOptMenuValue(self.bodyOMenu)
        acceID = self.getOptMenuValue(self.acceOMenu)
        logo = self.uclLogo
        # check thumbnail path
        thumPathList = []
        imagepath = self.thumbnailPath + '/' + self.thumbName
        for partid in [headID, bodyID, legID, hairID, acceID, logo]:
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
        # coord row
        coordThumbformLayout = cmds.formLayout(p=coordformLayout)
        # # coord Menu row
        coordMenuformLayout = cmds.formLayout(p=coordThumbformLayout)
        self.hairOMenu = cmds.optionMenu(cc=lambda *args: self.ui_action(0), w=self.oMenuWidth,
                                         p=coordMenuformLayout)
        self.headOMenu = cmds.optionMenu(cc=lambda *args: self.ui_action(0), w=self.oMenuWidth,
                                         p=coordMenuformLayout)
        self.bodyOMenu = cmds.optionMenu(cc=lambda *args: self.ui_action(1), w=self.oMenuWidth,
                                         p=coordMenuformLayout)
        self.legOMenu = cmds.optionMenu(cc=lambda *args: self.ui_action(1), w=self.oMenuWidth,
                                        p=coordMenuformLayout)
        self.acceOMenu = cmds.optionMenu(cc=lambda *args: self.ui_action(0), w=self.oMenuWidth,
                                         p=coordMenuformLayout)
        cmds.formLayout(coordMenuformLayout, e=True, af=[self.hairOMenu, 'top', 12])
        cmds.formLayout(coordMenuformLayout, e=True, af=[self.hairOMenu, 'left', 4])
        cmds.formLayout(coordMenuformLayout, e=True, af=[self.hairOMenu, 'right', 4])
        cmds.formLayout(coordMenuformLayout, e=True, ac=[self.headOMenu, 'top', 34, self.hairOMenu])
        cmds.formLayout(coordMenuformLayout, e=True, af=[self.headOMenu, 'left', 4])
        cmds.formLayout(coordMenuformLayout, e=True, af=[self.headOMenu, 'right', 4])
        cmds.formLayout(coordMenuformLayout, e=True, ac=[self.bodyOMenu, 'top', 34, self.headOMenu])
        cmds.formLayout(coordMenuformLayout, e=True, af=[self.bodyOMenu, 'left', 4])
        cmds.formLayout(coordMenuformLayout, e=True, af=[self.bodyOMenu, 'right', 4])
        cmds.formLayout(coordMenuformLayout, e=True, ac=[self.legOMenu, 'top', 34, self.bodyOMenu])
        cmds.formLayout(coordMenuformLayout, e=True, af=[self.legOMenu, 'left', 4])
        cmds.formLayout(coordMenuformLayout, e=True, af=[self.legOMenu, 'right', 4])
        cmds.formLayout(coordMenuformLayout, e=True, ac=[self.acceOMenu, 'top', 34, self.legOMenu])
        cmds.formLayout(coordMenuformLayout, e=True, af=[self.acceOMenu, 'left', 4])
        cmds.formLayout(coordMenuformLayout, e=True, af=[self.acceOMenu, 'right', 4])
        cmds.setParent(coordThumbformLayout)
        # # thumbnail row
        self.coordThumbnailLayout = cmds.columnLayout(adj=True, p=coordThumbformLayout)
        thumbLayoutPyside = mayaToPySide(self.coordThumbnailLayout, QtWidgets.QWidget)
        # self.coordGView = QtWidgets.QGraphicsView()
        self.coordGView = GraphView(thumbLayoutPyside)
        # self.coordGView.setParent(thumbLayoutPyside)
        self.coordThumbScene = QtWidgets.QGraphicsScene()
        self.coordThumbScene.clear()
        self.coordThumbScene.addPixmap(QtGui.QPixmap())
        self.coordThumbScene.addPixmap(QtGui.QPixmap())
        self.coordThumbScene.addPixmap(QtGui.QPixmap())
        self.coordThumbScene.addPixmap(QtGui.QPixmap())
        self.coordThumbScene.addPixmap(QtGui.QPixmap())
        self.coordThumbScene.addPixmap(QtGui.QPixmap())
        self.coordGView.setScene(self.coordThumbScene)
        cmds.setParent(coordThumbformLayout)
        # # layout
        cmds.formLayout(coordThumbformLayout, e=True, af=[coordMenuformLayout, 'top', 4])
        cmds.formLayout(coordThumbformLayout, e=True, af=[coordMenuformLayout, 'left', 4])
        cmds.formLayout(coordThumbformLayout, e=True, af=[self.coordThumbnailLayout, 'top', 4])
        cmds.formLayout(coordThumbformLayout, e=True,
                        ac=[self.coordThumbnailLayout, 'left', 8, coordMenuformLayout])
        cmds.formLayout(coordThumbformLayout, e=True,
                        af=[self.coordThumbnailLayout, 'right', 4])
        cmds.setParent(coordformLayout)

        # run Btn row
        runbtnformLayout = cmds.formLayout(parent=coordformLayout)
        loadRigBtn = cmds.button(l='Coordinate', h=40, bgc=self.runBtnCol,
                                 c=lambda *args: self.do_button())
        cmds.formLayout(runbtnformLayout, e=True, af=[loadRigBtn, 'left', 8])
        cmds.formLayout(runbtnformLayout, e=True, af=[loadRigBtn, 'right', 8])
        cmds.formLayout(runbtnformLayout, e=True, af=[loadRigBtn, 'bottom', 4])
        cmds.setParent(coordformLayout)

        # coord frame formLayout
        thumbnailLayoutSpace = 0
        cmds.formLayout(coordformLayout, e=True, ap=[coordThumbformLayout, 'top', 0, 0])
        cmds.formLayout(coordformLayout, e=True,
                        af=[coordThumbformLayout, 'left', thumbnailLayoutSpace])
        cmds.formLayout(coordformLayout, e=True, af=[coordThumbformLayout, 'right', 0])
        cmds.formLayout(coordformLayout, e=True,
                        ac=[runbtnformLayout, 'top', 4, coordThumbformLayout])
        cmds.formLayout(coordformLayout, e=True, af=[runbtnformLayout, 'left', 0])
        cmds.formLayout(coordformLayout, e=True, af=[runbtnformLayout, 'right', 0])
        cmds.formLayout(coordformLayout, e=True, af=[runbtnformLayout, 'bottom', 0])

    # ---------------------------------------------------------
    # UI : build coord Tab layout
    # ---------------------------------------------------------
    # @param None
    # @return <uiObj>coordTabcLayout : tab layout
    def tab_coord(self):
        coordTabcLayout = cmds.columnLayout(adj=1, p=self.alltabLayout)
        # build coord frame
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

        self.reloadAllOptMenu()
        cmds.window(self.windowName, e=True, w=self.defWidth, h=self.defHeight)

    # ---------------------------------------------------------
    # UI action
    # ---------------------------------------------------------
    # @param <int>switch
    # @return None
    def ui_action(self, switch):
        # load thumbnail with resetting transform
        if switch == 0:
            self.loadThumb(True)
        # load thumbnail
        elif switch == 1:
            self.loadThumb()
        else:
            print("GUI switch Error")

    # ---------------------------------------------------------
    # button action
    # ---------------------------------------------------------
    # @param <int>switch
    # @return None
    def do_button(self):
        pass


# import sys
# sys.path.append(r'E:\_gonokami\scripts\python\maya\tools\tool_git')
# import coordUI.gui as ccgui;reload(ccgui)
# gui = ccgui.toolGUI()
# gui.show()
