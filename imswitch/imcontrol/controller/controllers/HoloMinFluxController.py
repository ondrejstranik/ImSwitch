import json
import os

import numpy as np

from imswitch.imcommon.model import dirtools, initLogger
from ..basecontrollers import ImConWidgetController


class HoloMInFluxController(ImConWidgetController):
    """Linked to HoloMinFluxWidget."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__logger = initLogger(self)

        if self._setupInfo.slm is None:
            self._widget.replaceWithError('SLMManager is not configured in your setup file.')
            return

        self.slm = self._master.slmManager

        # get the paramteres from setupInfo
        self.monitorIdx = self._setupInfo.slm.monitorIdx
        self.width = self._setupInfo.slm.width
        self.heigth = self._setupInfo.slm.height
        # set the defalut parematers
        self.fromfile = False # source of the image
        self.pattern = "random"
        self.periodicity = 2
        self.contrast = 100
        self.offset = 1
        self.filename = r"C:\testimage.png"
        self.patternImage = None
        self.blackImage = np.zeros((self.heigth,self.width), dtype=np.uint8)
        self.active = False
        # set widget values
        self.updateWidgetParameters()
        self.updatePatternImage()

        # Connect CommunicationChannel signals
        self._commChannel.sigSLMUpdated.connect(lambda image: self.updateDisplayImage(image))

        # Connect Widget signals
        self._widget.sigSLMDisplayToggled.connect(self.toggleSLMDisplay)
        self._widget.sigUpdateParameters.connect(self.updateParameters)

        # Set SLM display
        self.slm.setNewImage(self.blackImage)
        self.slm.update()


    def updateWidgetParameters(self):
        ''' update widget paramters'''
        self._widget.setParameterValue("width",self.width)
        self._widget.setParameterValue("height",self.heigth)
        self._widget.setParameterValue("monitor ID",self.monitorIdx)
        if self.fromfile:
            self._widget.setParameterValue("image source","file")
        else:
            self._widget.setParameterValue("image source","pattern")
        self._widget.setParameterValue("file",self.filename)
        self._widget.setParameterValue("pattern",self.pattern)
        self._widget.setParameterValue("periodicity",self.periodicity)
        self._widget.setParameterValue("contrast",self.contrast)
        self._widget.setParameterValue("offset",self.offset)


    def updateParametersFromWidget(self):
        ''' update parameters from widget'''
        self.filename = self._widget.getParameterValue("file")
        self.pattern = self._widget.getParameterValue("pattern")
        self.periodicity = self._widget.getParameterValue("periodicity")
        self.contrast = self._widget.getParameterValue("contrast")
        self.offset = self._widget.getParameterValue("offset")
        if self._widget.getParameterValue("image source")== "file":
            self.fromfile = True
        else:
            self.fromfile = False

    def updateParameters(self):
        ''' update the pattern parameter Image after clicking the update button'''
        self.updateParametersFromWidget()
        self.updatePatternImage()

    def updatePatternImage(self):
        ''' update pattern image'''

        if self.pattern == "random":
            self.patternImage = (np.random.rand(self.heigth,self.width)*self.contrast + self.offset).astype(np.uint8)
        elif self.pattern == "mirror":
            self.patternImage = np.ones((self.heigth,self.width),dtype=np.uint8)*self.offset
        elif self.pattern == "hgrating":
            self.patternImage = np.ones((self.heigth,self.width),dtype=np.uint8)*self.offset
            patternIdx = np.arange(int(self.heigth/self.periodicity))*self.periodicity
            self.patternImage[patternIdx.astype(int),:] = self.contrast + self.offset
        elif self.pattern == "vgrating":
            self.patternImage = np.ones((self.heigth,self.width),dtype=np.uint8)*self.offset
            patternIdx = np.arange(int(self.width/self.periodicity))*self.periodicity
            self.patternImage[:,patternIdx.astype(int)] = self.contrast + self.offset
        elif self.pattern == "cross":
            self.patternImage = np.ones((self.heigth,self.width),dtype=np.uint8)*self.offset
            self.patternImage[[0, -1],:] = self.contrast + self.offset
            self.patternImage[:,[0,-1]] = self.contrast + self.offset
            self.patternImage[self.heigth//2,:] = self.contrast + self.offset
            self.patternImage[:,self.width//2] = self.contrast + self.offset



        # display pattern image on slm if button checked
        if self._widget.slmDisplayButton.isChecked():
            self.slm.setNewImage(self.patternImage)
            self.slm.update()

    def toggleSLMDisplay(self, enabled):
        ''' switch between pattern image and black image'''
        
        if self._widget.slmDisplayButton.isChecked():
            self.slm.setNewImage(self.patternImage)
        else:
            self.slm.setNewImage(self.blackImage)

        self.slm.update()

    def updateDisplayImage(self,image):
        ''' update image in the napari'''
        #image = np.fliplr(image.transpose())
        self._widget.showSlmImage(image)


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
