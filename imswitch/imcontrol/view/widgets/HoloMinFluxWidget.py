import numpy as np
import pyqtgraph as pg
from pyqtgraph.parametertree import ParameterTree
from qtpy import QtCore, QtWidgets
from pyqtgraph.dockarea import DockArea
from pyqtgraph.dockarea import Dock

from imswitch.imcommon.model import initLogger

from imswitch.imcontrol.view import guitools
from .basewidgets import NapariHybridWidget


class HoloMinFluxWidget(NapariHybridWidget):
    """ Widget containing interface for HoloMinFlux. """

    sigLiveUpdateToggled = QtCore.Signal(bool)  # (enabled)
    sigUpdateParameters = QtCore.Signal()

    def __post_init__(self, *args, **kwargs):
        #super().__init__(*args, **kwargs)

        self.__logger = initLogger(self)

        self.__logger.debug('HoloMinFlux Widet initialised')

        # layer in the napari widget for display of slm Image
        self.layer = None


        # 1. Panel - Selection Parameter

        self.parameterPanel = QtWidgets.QFrame()
        self.parameterPanel.gridLayout = QtWidgets.QGridLayout()
        self.parameterPanel.setLayout(self.parameterPanel.gridLayout)

        # create parameters three as a docking area
        self.channelParameterTree = ParameterTree()
        
        generalProperties = [
            {
                "name": "global phase wrap value",
                "type": "int",
                "value": 0
            },
            {
                "name": "apply global phase wrap",
                "type": "bool",
                "value": False
            },
            {
                "name": "SLM reflection value",
                "type": "int",
                "value": 0
            },
            {
                "name": "apply SLM reflection value",
                "type": "bool",
                "value": False
            },
        ]

        displayMode = [
            {
                "name": "type",
                "type": "list",
                "value": "mirror",
                "values": ["mirror","grating", "phasebox", "calibration"]
            },

        ]

        mirror = [
            {
                "name": "value",
                "type": "int",
                "value": 0
            }

        ]

        grating = [
            {
                "name": "grating type",
                "type": "list",
                "value": "0Pi",
                "values": ["0Pi", "blased"]
            },
            {
                "name": "grating constant",
                "type": "int",
                "value": 0
            },
            {
                "name": "grating shift",
                "type": "int",
                "value": 0
            },
            {
                "name": "value 0",
                "type": "int",
                "value": 0
            },
            {
                "name": "value pi",
                "type": "int",
                "value": 100
            },
            {
                "name": "orientation",
                "type": "list",
                "value": "horisontal",
                "values": ["horisontal","vertical"]
            }
        ]

        phaseBox = [
            {
                "name": "active",
                "type": "bool",
                "value": False 
            },
            {
                "name": "position x",
                "type": "int",
                "value": 0
            },
            {
                "name": "position y",
                "type": "int",
                "value": 0
            },
            {
                "name": "box height",
                "type": "int",
                "value": 6
            },
            {
                "name": "box half-width",
                "type": "int",
                "value": 6
            },
            {
                "name": "orientation",
                "type": "list",
                "value": "horisontal",
                "values": ["horisontal","vertical"]
            },
            {
                "name": "phi 1",
                "type": "int",
                "value": 0
            },
            {
                "name": "phi 2",
                "type": "int",
                "value": 100
            },
            {
                "name": "phi 3",
                "type": "int",
                "value": 50
            }
        ]

        phaseBoxes = [
                    {
                        "name": "Number of phase boxes",
                        "type": "int",
                        "value": 1
                    }]
        for ii in range(phaseBoxes[0]["value"]):
            phaseBoxes.append(
                {
                    "name": f"phase box {ii+1}",
                    "type": "group",
                    "childern": phaseBox
                }
            )

        calibration = [
            {
                "name": "Method",
                "type": "list",
                "value": "Phase Wrap Value",
                "values": ["Phase Wrap Value","SLM Reflection Value", "Dark Image Value"]
            } 
        ]

        generalparams = [
                    {
                        "name": "general properties",
                        "type": "group",
                        "childern": generalProperties
                    },
                    {
                        "name": "display mode",
                        "type": "group",
                        "childern": displayMode
                    },
                    {
                        "name": "mirror",
                        "type": "group",
                        "childern": mirror
                    },
                    {
                        "name": "grating",
                        "type": "group",
                        "childern": grating
                    },
                    {
                        "name": "phasebox",
                        "type": "group",
                        "childern": phaseBoxes
                    },
                    {
                        "name": "calibration",
                        "type": "group",
                        "childern": calibration
                    }
                ]

        self.channelParameterTree.p = pg.parametertree.Parameter.create(
            name="params", type="group", children=generalparams
        )
        self.channelParameterTree.setParameters(
            self.channelParameterTree.p, showTop=False
        )
        self.channelParameterTree._writable = True

        self.parameterPanel.paramtreeDockArea = DockArea()
        pmtreeDock = Dock("SLM parameters", size=(1, 1))
        pmtreeDock.addWidget(self.channelParameterTree)
        self.parameterPanel.paramtreeDockArea.addDock(pmtreeDock)

        # create button for showing SLM display
        self.slmUpdateButton = guitools.BetterPushButton('SLM Update')
        self.slmUpdateButton.setCheckable(True)

        # create button to update parameters
        self.buttonUP = guitools.BetterPushButton("Update Parameters")
        self.buttonUP.setCheckable(True)

        # place the items on the grid
        self.parameterPanel.gridLayout.addWidget(
            self.parameterPanel.paramtreeDockArea, 0, 0, 1, 0
        )
        self.parameterPanel.gridLayout.addWidget(
            self.buttonUP, 1, 0, 1, 1
        )
        self.parameterPanel.gridLayout.addWidget(
            self.slmUpdateButton, 2, 0, 1, 1
        )

        # Panels  -place them on the widget
        self.gridLayout = QtWidgets.QGridLayout()
        self.setLayout(self.gridLayout)
        self.gridLayout.addWidget(self.parameterPanel)

        # Connect signals
        self.slmUpdateButton.toggled.connect(self.sigLiveUpdateToggled)
        self.buttonUP.pressed.connect(self.sigUpdateParameters)


    def getParameterValue(self,parameterName:str):
        ''' return the channel parameter 
            parameterName ... different level separated by "/" sign'''
        splitName = parameterName.split("/")
        if len(splitName)==1:
            return self.channelParameterTree.p.param(splitName[0]).value()
        elif len(splitName)==2:
            return self.channelParameterTree.p.param(splitName[0]).param(splitName[1]).value()
        else:
            raise RuntimeError(f'Not such parameter {parameterName}')

    def setParameterValue(self,parameterName:str, value,default=True):
        ''' set the value of the paramter
            parameterName ... different level separated by "/" sign'''

        splitName = parameterName.split("/")
        if len(splitName)==1:
            self.channelParameterTree.p.param(splitName[0]).setValue(value)
            if default:
                self.channelParameterTree.p.param(splitName[0]).setDefault(value)
        elif len(splitName)==2:
            self.channelParameterTree.p.param(splitName[0]).param(splitName[1]).setValue(value)
            if default:
                self.channelParameterTree.p.param(splitName[0]).param(splitName[1]).setDefault(value)
        else:
            raise RuntimeError(f'Not such parameter {parameterName}')

    def showHoloMinFluxImage(self,im, colormap="gray", name="HoloMinFluxImage", pixelsize=None, translation=None):
        ''' show displayed generated homolinflux image'''
    
        if translation is None:
            translation = [0]*len(im.shape)

        if pixelsize is None:
            pixelsize = [1]*len(im.shape)
        
        if self.layer is None or name not in self.viewer.layers:
            self.layer = self.viewer.add_image(im, rgb=False, colormap=colormap, 
                                               scale=pixelsize,translate=translation,
                                               name=name, blending='additive')
        self.layer.data = im



# Copyright (C) 2020-2021 ImSwitch developers
# This file is part of ImSwitch.
#
# ImSwitch is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ImSwitch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
