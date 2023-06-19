import pyqtgraph as pg
from qtpy import QtCore, QtWidgets
from pyqtgraph.parametertree import ParameterTree
from pyqtgraph.dockarea import DockArea
from pyqtgraph.dockarea import Dock

from imswitch.imcommon.view.guitools import pyqtgraphtools
from imswitch.imcontrol.view import guitools
from .basewidgets import Widget

from imswitch.imcommon.model import initLogger

import numpy as np

class PtychoWidget(Widget):
    """ Run the ptychography data acquisition """

    sigStartMeasurement = QtCore.Signal()
    sigStopMeasurement = QtCore.Signal()
    sigUpdateParameters = QtCore.Signal()


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__logger = initLogger(self)

        # 1. Panel - Selection Parameter

        self.parameterPanel = QtWidgets.QFrame()
        self.parameterPanel.gridLayout = QtWidgets.QGridLayout()
        self.parameterPanel.setLayout(self.parameterPanel.gridLayout)

        # create ptycho recording parameters three as a docking area
        self.ptychoParameterTree = ParameterTree()
        generalparams = [
            {
                "name": "general",
                "type": "group",
                "children": [
                    {
                        "name": "wavelength",
                        "type": "float",
                        "value": 550,
                        "limits": (400, 900),
                        "step": 1,
                        "suffix": "nm",
                    },
                    {
                        "name": "number of points",
                        "type": "int",
                        "value": 200,
                        "limits": (1, 599),
                        "step": 1,
                        "suffix": "",
                    },
                    {
                        "name": "overlap",
                        "type": "float",
                        "value": 0.85,
                        "limits": (0, 1),
                        "step": 0.01,
                        "suffix": "",
                    },
                    {
                        "name": "size of probe",
                        "type": "float",
                        "value": 60,
                        "limits": (0, 1000),
                        "step": 10,
                        "suffix": "mm",
                    },
                    {
                        "name": "Magnification",
                        "type": "int",
                        "value": 50,
                        "limits": (1, 100),
                        "step": 10,
                        "suffix": "rad",
                    },
                    {   "name": "Saving folder",
                        "type": "str",
                        "value": r"G:\office\work\projects - funded\23-02-24 holominflux\23-06-09 imwitch_test\DATA_TEST"},
                    {
                        "name": "Saving filename",
                        "type": "str",
                        "value": r"ptychodata",
                    },
                ],
            }
        ]

        self.ptychoParameterTree.p = pg.parametertree.Parameter.create(
            name="params", type="group", children=generalparams
        )
        self.ptychoParameterTree.setParameters(
            self.ptychoParameterTree.p, showTop=False
        )
        self.ptychoParameterTree._writable = True

        self.parameterPanel.paramtreeDockArea = DockArea()
        pmtreeDock = Dock("Ptychography acquisition parameters", size=(1, 1))
        pmtreeDock.addWidget(self.ptychoParameterTree)
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

        # 2. Panel -  data acquisition 
        self.acquisitionPanel = QtWidgets.QFrame()
        self.acquisitionPanel.gridLayout = QtWidgets.QHBoxLayout()
        self.acquisitionPanel.setLayout(self.acquisitionPanel.gridLayout)

        # create two buttons for starting and stopping the acquisition
        self.acquisitionPanel.buttonSM = QtWidgets.QPushButton("Start Measurement")
        self.acquisitionPanel.buttonStM = QtWidgets.QPushButton("Stop Measurement")
        self.acquisitionPanel.buttonStM.setEnabled(False)

        # place the items on the grid
        self.acquisitionPanel.gridLayout.addWidget(self.acquisitionPanel.buttonSM)
        self.acquisitionPanel.gridLayout.addWidget(self.acquisitionPanel.buttonStM)

        # 3. Panel  - image view
        self.pathImagePanel = pg.plot()

        # Panels  -place them on the widget
        self.gridLayout = QtWidgets.QGridLayout()
        self.setLayout(self.gridLayout)
        self.gridLayout.addWidget(self.parameterPanel, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.acquisitionPanel, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.pathImagePanel, 0, 1, 0, 1)


        # Connect signals
        self.parameterPanel.buttonUP.pressed.connect(self.sigUpdateParameters)


    def _plotPath(self, coordinates:np.array):
        """plot the acquisition path in the widget"""

        # just rename
        p1 = self.pathImagePanel

        p1.clear()

        # define the scatterer plot and add it
        scatter = pg.ScatterPlotItem(pxMode = False)
        spots = []
        for ii in range(len(coordinates)):
            spot_dic = {
            'pos': (coordinates[ii,0]*1e-3,
            coordinates[ii,1]*1e-3), 
            'size': 3e-3,
            'pen': None,
            'brush': pg.hsvColor(hue= 1, sat= ii/len(coordinates))}
            
            spots.append(spot_dic)
        scatter.addPoints(spots)
        p1.addItem(scatter)

        # define line plot and add it
        lineplot = pg.PlotCurveItem()
        lineplot.setData(coordinates[:,0]*1e-3, coordinates[:,1]*1e-3)
        p1.addItem(lineplot)

        # define stage position and add it
        p1.stagePosition = pg.ScatterPlotItem(pxMode = False, symbol='o', size=1e-2)
        #p1.stagePosition.setData([{'pos':[0,0]}])
        p1.addItem(p1.stagePosition)

        # define the parameters of the plot
        p1.setAspectLocked(True)
        p1.setTitle(f'{len(self.grid_generator.coordinates)} positions')
        styles = {'color':'r', 'font-size':'20px'}
        p1.setLabel('left', ' Y', units='m')
        p1.setLabel('bottom', 'X', units= 'm')
        
        self.__logger.debug('Parameters updated')

    def _plotStagePosition(self,stageX,stageY,stagePosIdx,stagePosIdxMax):
        ''' update position of the stage'''

        self.pathImagePanel.stagePosition.setData([{'pos':[stageX*1e-3,stageY*1e-3]}])
        if stagePosIdx == -1:
            self.pathImagePanel.setTitle(f'{len(stagePosIdxMax)} positions')
        else:
            self.pathImagePanel.setTitle(f'{stagePosIdx} of {stagePosIdxMax} positions')


        self.__logger.debug('Updating stage position')            


    def _guiStartMeasurement(self):
        ''' update the gui for the measurement'''

        self.parameterPanel.buttonUP.setEnabled(False)
        self.acquisitionPanel.buttonSM.setEnabled(False)
        self.acquisitionPanel.buttonStM.setEnabled(True)

    def _guiStopMeasurement(self):
        ''' update gui after the measurement'''

        # set gui
        self.parameterPanel.buttonUP.setEnabled(True)
        self.acquisitionPanel.buttonSM.setEnabled(True)
        self.acquisitionPanel.buttonStM.setEnabled(False)















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
