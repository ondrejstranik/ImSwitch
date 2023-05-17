import json
import os

import numpy as np

from imswitch.imcommon.model import dirtools, initLogger
from ..basecontrollers import ImConWidgetController


class SLMbasicController(ImConWidgetController):
    """Linked to SLMbasicWidget."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__logger = initLogger(self)

        if self._setupInfo.slm in None:
            self._widget.replaceWithError('SLMManager is not configured in your setup file.')
            return

        self._widget.setMonitorIdx(self._setupInfo.slm.monitorIdx)

        # Connect CommunicationChannel signals
        #self._commChannel.sigSLMMaskUpdated.connect(lambda mask: self.displayMask(mask))

        #self._widget.applyChangesButton.clicked.connect(self.applyParams)
        self._widget.sigSLMDisplayToggled.connect(self.toggleSLMDisplay)
        self._widget.sigSLMMonitorChanged.connect(self.monitorChanged)
        self._widget.ChangeButtonPressed.connect(self.gnerateNewImage)

        # Initial SLM display
        self.displayMask(self._master.slmManager.slmImg)

    def generateNewImage(self):
        # generate new Image for the slm
        pass


    def toggleSLMDisplay(self, enabled):
        # set new arbitrary image
        self.__logger.debug(f'function tpggleSLMDisplay: new image')
        
        if not self._widget.slmDisplayButton.isChecked():
            mynewim = np.zeros((600,800))
        else:
            mynewim = np.random.rand(600,800)

        self._master.slmManager.setNewImage(mynewim)

        self._master.slmManager.update()

        self._widget.setSLMDisplayVisible(enabled)

    def monitorChanged(self, monitor):
        self._widget.setSLMDisplayMonitor(monitor)

    def displayMask(self, maskCombined):
        """ Display the mask in the SLM display. Originates from slmPy:
        https://github.com/wavefrontshaping/slmPy """

        arr = maskCombined
        

        self.updateDisplayImage(arr)

        
        # Padding: Like they do in the software
        pad = np.zeros((600, 8), dtype=np.uint8)
        arr = np.append(arr, pad, 1)

        # Create final image array
        h, w = arr.shape[0], arr.shape[1]

        if len(arr.shape) == 2:
            # Array is grayscale
            arrGray = arr.copy()
            arrGray.shape = h, w, 1
            img = np.concatenate((arrGray, arrGray, arrGray), axis=2)
        else:
            img = arr

        self._widget.updateSLMDisplay(img)



    # Button pressed functions

    def updateDisplayImage(self, image):
        image = np.fliplr(image.transpose())
        self._widget.img.setImage(image, autoLevels=True, autoDownsample=False)


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
