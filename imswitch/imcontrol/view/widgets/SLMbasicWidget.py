import numpy as np
import pyqtgraph as pg
from pyqtgraph.parametertree import ParameterTree
from qtpy import QtCore, QtWidgets
from pyqtgraph.dockarea import DockArea
from pyqtgraph.dockarea import Dock

from imswitch.imcommon.model import initLogger

from imswitch.imcontrol.view import guitools
from .basewidgets import NapariHybridWidget


class SLMBasicWidget(NapariHybridWidget):
    """ Widget containing basic slm interface. """

    sigSLMDisplayToggled = QtCore.Signal(bool)  # (enabled)
    sigUpdateParameters = QtCore.Signal()

    def __post_init__(self, *args, **kwargs):
        #super().__init__(*args, **kwargs)

        self.__logger = initLogger(self)

        self.__logger.debug('SLMBasicWidet initialised')

        # layer in the napari widget for display of slm Image
        self.layer = None


        # 1. Panel - Selection Parameter

        self.parameterPanel = QtWidgets.QFrame()
        self.parameterPanel.gridLayout = QtWidgets.QGridLayout()
        self.parameterPanel.setLayout(self.parameterPanel.gridLayout)

        # create parameters three as a docking area
        self.channelParameterTree = ParameterTree()
        
        generalparams = [
                    {
                        "name": "width",
                        "type": "float",
                        "value": 100,
                        "step": 1,
                        "suffix": "px",
                    },
                    {
                        "name": "height",
                        "type": "float",
                        "value": 100,
                        "step": 1,
                        "suffix": "px",
                    },
                    {
                        "name": "monitor ID",
                        "type": "int",
                        "value": 1,
                    },
                    {
                        "name": "image source",
                        "type": "list",
                        "value": "pattern",
                        "values": ["pattern", "file"]
                    },
                    {
                        "name": "file",
                        "type": "str",
                        "value": ""
                    },
                    {
                        "name": "pattern",
                        "type": "list",
                        "value": "random",
                        "values": ["mirror", "hgrating", "vgrating", "random", "cross"]
                    },
                    {
                        "name": "periodicity",
                        "type": "float",
                        "value": 2,
                    },
                    {
                        "name": "contrast",
                        "type": "int",
                        "value": 100,
                    },
                    {
                        "name": "offset",
                        "type": "int",
                        "value": 1,
                    },



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
        self.slmDisplayButton = guitools.BetterPushButton('SLM active')
        self.slmDisplayButton.setCheckable(True)

        # create button to update parameters
        self.buttonUP = QtWidgets.QPushButton("Update Parameters")

        # place the items on the grid
        self.parameterPanel.gridLayout.addWidget(
            self.parameterPanel.paramtreeDockArea, 0, 0, 1, 0
        )
        self.parameterPanel.gridLayout.addWidget(
            self.buttonUP, 1, 0, 1, 1
        )
        self.parameterPanel.gridLayout.addWidget(
            self.slmDisplayButton, 2, 0, 1, 1
        )

        # Panels  -place them on the widget
        self.gridLayout = QtWidgets.QGridLayout()
        self.setLayout(self.gridLayout)
        self.gridLayout.addWidget(self.parameterPanel)


        # Connect signals
        self.slmDisplayButton.toggled.connect(self.sigSLMDisplayToggled)
        self.buttonUP.pressed.connect(self.sigUpdateParameters)


    def getParameterValue(self,parameterName:str):
        ''' return the channel parameter '''
        return self.channelParameterTree.p.param(parameterName).value()
    
    def setParameterValue(self,parameterName:str, value,default=True):
        ''' set the value of the paramter'''
        self.channelParameterTree.p.param(parameterName).setValue(value)
        if default:
            self.channelParameterTree.p.param(parameterName).setDefault(value)

    def showSlmImage(self,im, colormap="gray", name="SlmImage", pixelsize=None, translation=None):
        ''' show displayed slm image'''
    
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
