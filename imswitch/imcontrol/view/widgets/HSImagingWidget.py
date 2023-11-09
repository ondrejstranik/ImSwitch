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

class HSImagingWidget(NapariHybridWidget):
    """ Run the hyperspectral Imaging widget """

    sigLiveMeasurement = QtCore.Signal(bool)
    sigUpdateParameters = QtCore.Signal()


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
                        "name": "number of images",
                        "type": "int",
                        "value": 10,
                        "limits": (1, 599),
                        "step": 1,
                        "suffix": "",
                    },
                    {
                        "name": "size of spot",
                        "type": "int",
                        "value": 10,
                        "limits": (1, 50),
                        "step": 10,
                        "suffix": "px",
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
        pmtreeDock = Dock("HSI parameters", size=(1, 1))
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

        # create button for starting and stopping the acquisition

        self.acquisitionPanel.buttonLM = guitools.BetterPushButton('Live Measurement')
        self.acquisitionPanel.buttonLM.setCheckable(True)
  
        # place the items on the grid
        self.acquisitionPanel.gridLayout.addWidget(self.acquisitionPanel.buttonLM)

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
        self.acquisitionPanel.buttonLM.toggled.connect(
            self.sigLiveMeasurement(self.acquisitionPanel.buttonLM.isChecked()))


    def _plotSpectra(self, x:np.array, spectra:np.array):
        """plot the spectra in the widget
        spectra ... one spectrum per column (axis = 0)
        """
        # just rename
        p1 = self.pathImagePanel

        p1.clear()

        # define line plot and add it
        for ii in range(len(spectra)):
            lineplot = pg.PlotCurveItem()
            lineplot.setData(x, spectra[:,ii])
        p1.addItem(lineplot)

        # define the parameters of the plot
        p1.setAspectLocked(True)
        p1.setTitle(f'{len(spectra)} Spectra')
        styles = {'color':'r', 'font-size':'20px'}
        p1.setLabel('left', ' Y', units='m')
        p1.setLabel('bottom', 'X', units= 'm')
        
        self.__logger.debug('Spectra updated')


    def showHSImage(self,im, colormap="gray", name="HSImage", pixelsize=None, translation=None):
        ''' show the recorded HS Image as Napari layer in image widget'''
    
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
        pass

    def _guiStopMeasurement(self):
        ''' update gui after the measurement'''
        pass

    def getParameterValue(self,name:str, key="general"):
        ''' return the value of parameter in the parameters three'''
        return  self.ptychoParameterTree.p.param(key).param(name).value()
    
    def setParameterValue(self,name:str, value, key="general",default=True):
        ''' set the value of the parameter in the parameters three'''
        self.ptychoParameterTree.p.param(key).param(name).setValue(value)
        if default:
            self.ptychoParameterTree.p.param(key).param(name).setDefault(value)

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
