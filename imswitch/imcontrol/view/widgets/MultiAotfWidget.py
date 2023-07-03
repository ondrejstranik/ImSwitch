from qtpy import QtCore, QtWidgets
from pyqtgraph.parametertree import ParameterTree
from pyqtgraph.dockarea import DockArea
from pyqtgraph.dockarea import Dock
import pyqtgraph as pg

from imswitch.imcommon.model import initLogger


from .basewidgets import Widget


class MultiAOTFWidget(Widget):

    sigUpdateParameters = QtCore.Signal()


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.__logger = initLogger(self)

        # 1. Panel - Selection Parameter

        self.parameterPanel = QtWidgets.QFrame()
        self.parameterPanel.gridLayout = QtWidgets.QGridLayout()
        self.parameterPanel.setLayout(self.parameterPanel.gridLayout)

        # create ptycho recording parameters three as a docking area
        self.channelParameterTree = ParameterTree()
        
        self.singleChannel = [
                    {
                        "name": "wavelength",
                        "type": "float",
                        "value": 550,
                        "limits": (400, 900),
                        "step": 1,
                        "suffix": "nm",
                    },
                    {
                        "name": "intensity",
                        "type": "float",
                        "value": 0,
                        "limits": (0, 100),
                        "step": 1,
                        "suffix": "",
                    },
                    {
                        "name": "active",
                        "type": "bool",
                        "value": False,
                    }
                ]

       
        generalparams = [
            {
                "name": "Channel_1",
                "type": "group",
                "children": self.singleChannel
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
        pmtreeDock = Dock("AOTF channels", size=(1, 1))
        pmtreeDock.addWidget(self.channelParameterTree)
        self.parameterPanel.paramtreeDockArea.addDock(pmtreeDock)

        # create a button for changing the values of the parameters
        self.parameterPanel.buttonUP = QtWidgets.QPushButton("Update Parameters")

        # place the items on the grid
        self.parameterPanel.gridLayout.addWidget(
            self.parameterPanel.paramtreeDockArea, 0, 0, 1, 0
        )
        self.parameterPanel.gridLayout.addWidget(
            self.parameterPanel.buttonUP, 1, 0, 1, 1
        )

        # Panels  -place them on the widget
        self.setLayout(self.parameterPanel.gridLayout)

        # Connect signals
        self.parameterPanel.buttonUP.pressed.connect(self.sigUpdateParameters)

    def setNumberOfChannels(self,nChannels):
        ''' set number of AOTF channels in the parameterPanel'''

        generalparams = []

        for ii in range(nChannels):
            generalparams.append(
            {
                "name": f"Channel_{ii+1}",
                "type": "group",
                "children": self.singleChannel
            }
            )
        self.channelParameterTree.p = pg.parametertree.Parameter.create(
            name="params", type="group", children=generalparams
        )
        self.channelParameterTree.setParameters(
            self.channelParameterTree.p, showTop=False
        )

    def getChannelInfo(self,Channel):
        ''' return a dictionary of the channel parameters '''
        cInfo = {
        "wavelength": (
        self.channelParameterTree.p.param(f"Channel_{Channel}").param("wavelength").value()
        ),
        "intensity": (
        self.channelParameterTree.p.param(f"Channel_{Channel}").param("intensity").value()
        ),
        "active": (
        self.channelParameterTree.p.param(f"Channel_{Channel}").param("active").value()
        )
        }

        self.__logger.debug(f'cInfo: \n {cInfo}')
        return cInfo



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
