#!/usr/bin/env python
# -*- coding: utf-8 -*-
##########################################################
#
#  @brief  clean up scene
#  @file   cleanup_scene.py
#  @author mono-g
#
#  Copyright(C) 2018 mono-g.
#
##########################################################
import pymel.core as pm


# ---------------------------------------------------------
# clean up PanelCallback
# ---------------------------------------------------------
# @param None
# @return None
def cleanupPanelCallback():
    viewName = ['Top View', 'Side View', 'Front View', 'Persp View']
    for vname in viewName:
        panelName = pm.sceneUIReplacement(gp=['modelPanel', pm.mel.localizedPanelLabel(vname)])
        if panelName != '':
            pm.modelEditor(panelName, e=True, ec='')
