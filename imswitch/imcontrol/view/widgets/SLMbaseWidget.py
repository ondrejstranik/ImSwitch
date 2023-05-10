import numpy as np
import pyqtgraph as pg
from pyqtgraph.parametertree import ParameterTree
from qtpy import QtCore, QtWidgets

from imswitch.imcontrol.view import guitools
from .basewidgets import Widget


class SLMbaseWidget(Widget):
    """ Widget containing slm interface. """

    sigSLMDisplayToggled = QtCore.Signal(bool)  # (enabled)
    sigSLMMonitorChanged = QtCore.Signal(int)  # (monitor)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.slmDisplay = None

        self.slmFrame = pg.GraphicsLayoutWidget()
        self.vb = self.slmFrame.addViewBox(row=1, col=1)
        self.img = pg.ImageItem()
        self.img.setImage(np.zeros((792, 600)), autoLevels=True, autoDownsample=True,
                          autoRange=True)
        self.vb.addItem(self.img)
        self.vb.setAspectLocked(True)


        # Button for showing SLM display and spinbox for monitor selection
        self.slmDisplayLayout = QtWidgets.QHBoxLayout()

        self.slmDisplayButton = guitools.BetterPushButton('Show SLM display (fullscreen)')
        self.slmDisplayButton.setCheckable(True)
        self.slmDisplayButton.toggled.connect(self.sigSLMDisplayToggled)
        self.slmDisplayLayout.addWidget(self.slmDisplayButton, 1)

        self.slmMonitorLabel = QtWidgets.QLabel('Screen:')
        self.slmDisplayLayout.addWidget(self.slmMonitorLabel)

        self.slmMonitorBox = QtWidgets.QSpinBox()
        self.slmMonitorBox.valueChanged.connect(self.sigSLMMonitorChanged)
        self.slmDisplayLayout.addWidget(self.slmMonitorBox)

        # Button to apply changes
        self.applyChangesButton = guitools.BetterPushButton('Apply changes')
        # self.paramtreeDockArea.addWidget(self.applyChangesButton, 'bottom', abertreeDock)

        self.grid = QtWidgets.QGridLayout()
        self.setLayout(self.grid)

        self.grid.addWidget(self.slmFrame, 0, 0, 1, 2)
        #self.grid.addWidget(self.paramtreeDockArea, 1, 0, 2, 1)
        #self.grid.addWidget(self.applyChangesButton, 2, 0, 1, 1)
        self.grid.addLayout(self.slmDisplayLayout, 2, 0, 1, 1)
        #self.grid.addWidget(self.controlPanel, 1, 1, 2, 1)

    def initSLMDisplay(self, monitor):
        from imswitch.imcontrol.view import SLMDisplay
        self.slmDisplay = SLMDisplay(self, monitor)
        self.slmDisplay.sigClosed.connect(lambda: self.sigSLMDisplayToggled.emit(False))
        self.slmMonitorBox.setValue(monitor)

    def updateSLMDisplay(self, imgArr):
        self.slmDisplay.updateImage(imgArr)

    def setSLMDisplayVisible(self, visible):
        self.slmDisplay.setVisible(visible)
        self.slmDisplayButton.setChecked(visible)

    def setSLMDisplayMonitor(self, monitor):
        self.slmDisplay.setMonitor(monitor, updateImage=True)


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
