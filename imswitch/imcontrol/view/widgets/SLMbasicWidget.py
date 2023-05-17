import numpy as np
import pyqtgraph as pg
from pyqtgraph.parametertree import ParameterTree
from qtpy import QtCore, QtWidgets

from imswitch.imcontrol.view import guitools
from .basewidgets import NapariHybridWidget


class SLMbaseWidget(NapariHybridWidget):
    """ Widget containing basic slm interface. """

    sigSLMDisplayToggled = QtCore.Signal(bool)  # (enabled)
    sigSLMMonitorChanged = QtCore.Signal(int)  # (monitor)
    sigChangeButtonPressed = QtCore.Signal()  # (changeButton)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.layer = None
        
        # Button for showing SLM display and spinbox for monitor selection
        self.slmDisplayLayout = QtWidgets.QHBoxLayout()

        self.slmDisplayButton = guitools.BetterPushButton('SLM active')
        self.slmDisplayButton.setCheckable(True)
        self.slmDisplayButton.toggled.connect(self.sigSLMDisplayToggled)
        self.slmDisplayLayout.addWidget(self.slmDisplayButton, 1)

        self.slmMonitorLabel = QtWidgets.QLabel('Screen:')
        self.slmDisplayLayout.addWidget(self.slmMonitorLabel)

        self.slmMonitorBox = QtWidgets.QSpinBox()
        self.slmMonitorBox.valueChanged.connect(self.sigSLMMonitorChanged)
        self.slmDisplayLayout.addWidget(self.slmMonitorBox)

        # Button to apply changes
        self.applyChangesButton = guitools.BetterPushButton('Change Image')
        self.applyChangesButton.pressed.connect(self.sigChangeButtonPressed)
        
        self.grid = QtWidgets.QGridLayout()
        self.setLayout(self.grid)
        self.grid.addWidget(self.applyChangesButton, 0, 0, 1, 2)
        self.grid.addLayout(self.slmDisplayLayout, 2, 0, 1, 1)

    def setImage(self, im):
        pass

    def getSMLActiveChecked(self):
        return self.slmDisplayButton.isChecked()
    
    def setMonitorIdx(self,MIdx: int) -> None:
        self.slmMonitorBox.setValue(MIdx)


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
