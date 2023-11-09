import numpy as np
from pathlib import Path

import time


from imswitch.imcommon.framework import Signal, Thread, Worker, Mutex
from imswitch.imcontrol.view import guitools
from ..basecontrollers import ImConWidgetController, LiveUpdatedController

from imswitch.imcommon.model import initLogger

try:
    from ptypyLab.Model.GridGenerator import GridGenerator
    from ptypyLab.Controller.Storage.h5 import DataStorage
    from ptypyLab import dataContainer
except ImportError:
    print('ptypyLab package not installed. Do not use PtychoWidget/Controller')

class HSImagingController(ImConWidgetController):
    """ Linked to HSImagingWidget."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__logger = initLogger(self)

        # set the parameters from json/default
        self._widget.setParameterValue("number of images",
            self._setupInfo.ptychoInfo.nImages)
        self._widget.setParameterValue("size of spot",
            self._setupInfo.ptychoInfo.spot_size)

        # set the detector from json/default
        allDetectorNames = self._master.detectorsManager.getAllDeviceNames()
        if self._setupInfo.ptychoInfo.cameraName in allDetectorNames:
            DetectorName= self._setupInfo.ptychoInfo.cameraName
        else:
            DetectorName = allDetectorNames[0]
        self._widget.setParameterValue("camera name", DetectorName)
        self.detector = self._master.detectorsManager[DetectorName]

        # wavelength
        self.wavelength = None

        # number of average Images
        self.nAverage = None

        # prepare gui
        self.updateParametersFromWidget()

        # stage worker
        self.cameraWorker = None
        self.cameraThread = None
        
        # Connect PtychoWidget signals
        self._widget.sigLiveMeasurement.connect(self.liveMeasurement)
        self._widget.sigUpdateParameters.connect(self.updateParametersFromWidget)

        # Connect CommunicationChannel signals


    def updateParametersFromWidget(self):
        """update parameters from the widget"""

        self.detector = self._master.detectorsManager[
            self._widget.getParameterValue("camera name")
        ]
        
        self.nAverage = self._widget.getParameterValue("number of images")

        self.__logger.debug('Parameters updated')


    def liveMeasurement(self,toggled:bool):
        ''' make action if the 'live measurement' button is toggled'''

        if toggled == True:
            self._startMeasurement()
        else:
            self._stopMeasurement()


    def _startMeasurement(self):
        ''' prepare all the variable for recording and gui'''
        # get one image in order to allocate the size of the image
        self.detector.startAcquisition()

        # set gui
        self._widget._guiStartMeasurement()

        self.cameraWorker = self.CameraWorker(
            self.detector,
            self.nAverage
            )
        self.cameraWorker.sigHSImageDone.connect(self.measurementStep)

        self.cameraThread = Thread()
        self.cameraWorker.moveToThread(self.cameraThread)
        self.cameraThread.start()

        # start recording the images
        self.cameraWorker.startRecording()

    def finishMeasurement(self):
        ''' close all the variable and gui '''
        
        self.detector.stopAcquisition()

        self._widget._guiStopMeasurement()

        # close the thread
        self.cameraThread.quit()
        self.cameraThread.wait()

    def measurementStep(self, recordedImage):
        ''' display / analyse the hyper spectral image'''
        self.__logger.debug('Hyper spectral image received ')

        # show the recorded image
        self._widget.showHSImage(recorededImage)
       
        #TODO: show the spectra in the widget
        # show the spectra
        pass


    class CameraWorker(Worker):
        '''' class to record average image and transform the raw image into hyperspectral cube image'''
        sigHSImageDone = Signal(np.ndarray)

        def __init__(self,Detector,nAverage):
            super().__init__()
            self.imageRecording = True
            self.nAverage = nAverage
            self.nIdx = 0
            self.Detector = Detector

        def startRecording(self):

            while self.imageRecording:
                # make avarage
                for ii in range(self.nAverage):
                    # take image
                    im = self.Detector.getLatestFrame()
                    if ii== 0:
                        imAve = im.astype('uint64')
                    else:
                        imAve += im
                imFinal = (imAve/self.nAverage).astype(uint16)

                self.sigHSImageDone.emit(imFinal)

            








        














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
