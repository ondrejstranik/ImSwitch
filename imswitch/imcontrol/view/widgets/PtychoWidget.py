import pyqtgraph as pg
from qtpy import QtCore, QtWidgets
from pyqtgraph.parametertree import ParameterTree
from pyqtgraph.dockarea import DockArea
from pyqtgraph.dockarea import Dock

from imswitch.imcommon.view.guitools import pyqtgraphtools
from imswitch.imcontrol.view import guitools
from .basewidgets import NapariHybridWidget

from imswitch.imcommon.model import initLogger

import numpy as np

class PtychoWidget(NapariHybridWidget):
    """ Run the ptychography data acquisition """

    sigStartMeasurement = QtCore.Signal()
    sigStopMeasurement = QtCore.Signal()
    sigUpdateParameters = QtCore.Signal()
    sigDarkMeasurement = QtCore.Signal()


    def __post_init__(self, *args, **kwargs):
        #super().__init__(*args, **kwargs)
        self.__logger = initLogger(self)

        # layer in the napari widget for display of the recorded images
        self.layer = None

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
                        "type": "str",
                        "value": "550",
                        "suffix": "nm",
                    },
                    {
                        "name": "number of points",
                        "type": "int",
                        "value": 10,
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
                    },
                    {   "name": "Saving folder",
                        "type": "str",
                        "value": r"C:",
                    },
                    {
                        "name": "Saving filename",
                        "type": "str",
                        "value": r"ptychodata",
                    },
                    {
                        "name": "Saving dark filename",
                        "type": "str",
                        "value": r"ptychodark",
                    },
                    {   "name": "camera name",
                        "type": "str",
                        "value": "cam1",
                    },
                    {   "name": "positioner name",
                        "type": "str",
                        "value": "pos1",
                    }
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
        self.acquisitionPanel.buttonDM = QtWidgets.QPushButton("Dark Measurement")
        self.acquisitionPanel.buttonStM = QtWidgets.QPushButton("Stop Measurement")

        self.acquisitionPanel.buttonStM.setEnabled(False)

        # place the items on the grid
        self.acquisitionPanel.gridLayout.addWidget(self.acquisitionPanel.buttonSM)
        self.acquisitionPanel.gridLayout.addWidget(self.acquisitionPanel.buttonDM)
        self.acquisitionPanel.gridLayout.addWidget(self.acquisitionPanel.buttonStM)

        # 3. Panel  - image view
        self.pathImagePanel = pg.plot()

        # Panels  -place them on the widget
        self.gridLayout = QtWidgets.QGridLayout()
        self.setLayout(self.gridLayout)
        self.gridLayout.addWidget(self.pathImagePanel, 0, 0, 4, 0)
        self.gridLayout.addWidget(self.parameterPanel, 4, 0, 2, 0)
        self.gridLayout.addWidget(self.acquisitionPanel, 6, 0, 1, 0)


        # Connect signals
        self.parameterPanel.buttonUP.pressed.connect(self.sigUpdateParameters)
        self.acquisitionPanel.buttonSM.pressed.connect(self.sigStartMeasurement)
        self.acquisitionPanel.buttonDM.pressed.connect(self.sigDarkMeasurement)
        self.acquisitionPanel.buttonStM.pressed.connect(self.sigStopMeasurement)


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
        p1.setTitle(f'{len(coordinates)} positions')
        styles = {'color':'r', 'font-size':'20px'}
        p1.setLabel('left', ' Y', units='m')
        p1.setLabel('bottom', 'X', units= 'm')
        
        self.__logger.debug('Parameters updated')

    def _plotStagePosition(self,stageX,stageY,stagePosIdx,stagePosIdxMax):
        ''' update position of the stage'''

        self.pathImagePanel.stagePosition.setData([{'pos':[stageX*1e-3,stageY*1e-3]}])
        if stagePosIdx == -1:
            self.pathImagePanel.setTitle(f'{stagePosIdxMax} positions')
        else:
            self.pathImagePanel.setTitle(f'{stagePosIdx} of {stagePosIdxMax} positions')


        self.__logger.debug('Updating stage position')            

    def showPtychogram(self,im, colormap="gray", name="Ptychogram", pixelsize=None, translation=None):
        ''' show the recorded ptychogram in as Napari layer in image widget'''
    
        if translation is None:
            translation = [0]*len(im.shape)

        if pixelsize is None:
            pixelsize = [1]*len(im.shape)
        
        if self.layer is None or name not in self.viewer.layers:
            self.layer = self.viewer.add_image(im, rgb=False, colormap=colormap, 
                                               scale=pixelsize,translate=translation,
                                               name=name, blending='additive')
        self.layer.data = im




    def _guiStartMeasurement(self):
        ''' update the gui for the measurement'''

        self.parameterPanel.buttonUP.setEnabled(False)
        self.acquisitionPanel.buttonSM.setEnabled(False)
        self.acquisitionPanel.buttonDM.setEnabled(False)
        self.acquisitionPanel.buttonStM.setEnabled(True)

    def _guiStopMeasurement(self):
        ''' update gui after the measurement'''

        # set gui
        self.parameterPanel.buttonUP.setEnabled(True)
        self.acquisitionPanel.buttonSM.setEnabled(True)
        self.acquisitionPanel.buttonDM.setEnabled(True)
        self.acquisitionPanel.buttonStM.setEnabled(False)

    def getParameterValue(self,name:str, key="general"):
        ''' return the value of parameter in the parameters three'''
        return  self.ptychoParameterTree.p.param(key).param(name).value()
    
    def setParameterValue(self,name:str, value, key="general",default=True):
        ''' set the value of the parameter in the parameters three'''
        self.ptychoParameterTree.p.param(key).param(name).setValue(value)
        if default:
            self.ptychoParameterTree.p.param(key).param(name).setDefault(value)

    # TODO: this function is not working
    def setParametersValue(self,name:str, values:list, value, key="general"):
        ''' set the values list and value of the parameter in the parameters three'''
       
        if True:
            pass
        else:
            self.ptychoParameterTree.p.param(key).param(name).setOpts(**{"values":values})
                    
            if value in values:
                self.setParameterValue(name,value)
            else:
                self.setParameterValue(name,values[0])
















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
