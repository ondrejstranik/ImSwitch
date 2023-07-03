import numpy as np
from pathlib import Path

import time


from imswitch.imcommon.framework import Signal, Thread, Worker, Mutex
from imswitch.imcontrol.view import guitools
from ..basecontrollers import ImConWidgetController, LiveUpdatedController

from imswitch.imcommon.model import initLogger

class PtychoController(ImConWidgetController):
#class PtychoController(LiveUpdatedController):
    """ Linked to PtychoWidget."""

    sigMoveStage = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__logger = initLogger(self)

        try:
            from ptypyLab.Model.GridGenerator import GridGenerator
            from ptypyLab.Controller.Storage.h5 import DataStorage
            from ptypyLab import dataContainer
        except ImportError:
            self._logger.error('ptypyLab package not installed')
            return 

        
        # set the parameters from json/default
        self._widget.setParameterValue("number of points",
            self._setupInfo.ptychoInfo.nMax)
        self._widget.setParameterValue("size of probe",
            self._setupInfo.ptychoInfo.probe_size_mm)

        # set the detector from json/default
        allDetectorNames = self._master.detectorsManager.getAllDeviceNames()
        if self._setupInfo.ptychoInfo.cameraName in allDetectorNames:
            DetectorName= self._setupInfo.ptychoInfo.cameraName
        else:
            DetectorName = allDetectorNames[0]
        self._widget.setParameterValue("camera name", DetectorName)
        self.detector = self._master.detectorsManager[DetectorName]

        # set other parameters of the detector from json/default
        self.detector.setBinning(self._setupInfo.ptychoInfo.binning)
        self.detector.setParameter("exposure",self._setupInfo.ptychoInfo.exposure_ms)

        # flag for taking an image
        self.looping = False

        # file numbering
        self.filenumber = 1

        # define gridgenerator
        self.grid_generator = GridGenerator()

        # parameters for the recording
        self.storage = None
        self.fullfilename = None
  
        # prepare gui
        self.updateParametersFromWidget()

        # stage worker
        self.stageWorker = None
        self.stageThread = None
        
        # Connect PtychoWidget signals
        self._widget.sigStartMeasurement.connect(self.startMeasurement)
        self._widget.sigStopMeasurement.connect(self.interuptMeausurement)
        self._widget.sigUpdateParameters.connect(self.updateParametersFromWidget)

        # Connect CommunicationChannel signals
        #self._commChannel.sigUpdateImage.connect(self.update)
        #self.detector.sigImageUpdated.connect(self.update)
        #self._commChannel.sigUpdateImage.connect(self.update)


    def updateParametersFromWidget(self):
        """update parameters from the widget"""

        # fixed parameters
        self.grid_generator.type = "square"
        self.grid_generator.extent_mm = "auto"  # either range in mm or 'auto' 0.4
        self.grid_generator.probe_size_mm = (
            self._widget.getParameterValue("size of probe")
        )
        self.grid_generator.n_points_max = (
            self._widget.getParameterValue("number of points")
        )
        self.grid_generator.overlap = (
            self._widget.getParameterValue("overlap")
        )
        self.fullfilename = Path(
            self._widget.getParameterValue("Saving folder"),
            self._widget.getParameterValue("Saving filename")
        )
        self.grid_generator.prepare()
        self._widget._plotPath(self.grid_generator.coordinates)

        self.detector = self._master.detectorsManager[
            self._widget.getParameterValue("camera name")
        ]
        
        
        
        self.__logger.debug('Parameters updated')

    def increaseIdxOfFilename(self):
        ''' change the name of the file for recording'''
        self.filenumber +=1
        currentFilename =  self._widget.getParameterValue("Saving filename")
        newFilename = currentFilename.split('_m')[0] + '_m' + str(self.filenumber)
        self._widget.setParameterValue("Saving filename",newFilename)
        self.fullfilename = Path(
            self._widget.getParameterValue("Saving folder"),
            newFilename)


    def startMeasurement(self):
        ''' prepare all the variable for recording and gui'''
        # start the camera running
        # handle_Acq = self._master.detectorsManager.startAcquisition(liveView=True)

        #self.detector.startAcquisition(liveView=True)
        self.detector.startAcquisition()



        # create the data storage
        self.storage = DataStorage(self.fullfilename, append_tag=True)

        extra_info = dict(
            target_coordinate = self.grid_generator.coordinates,
            exposure_time=self.detector.parameters['exposure'].value,
            binning=self.detector.binning,
            offset= list(self.detector.frameStart)
        )
        self.storage.add_metadata(extra_info)

        self._logger.debug(self.detector.parameters)

        # alocate space for the data in the storage
        myim = self.detector.getLatestFrame()
        cameraName = self.detector.model
        picture_dictionary = {cameraName: dataContainer(data=myim, image=True, show_FT=False, show=True)}
        info = {}
        info.update(picture_dictionary)
        self.storage.prepare_measurement(info,len(self.grid_generator.coordinates))
        self._logger.debug('allocating the space in the hdf5 file')

        # set gui
        self._widget._guiStartMeasurement()

        # prepare stage worker
        # TODO: temp       
        '''
        self.stageWorker = self.StageWorker(
            self._master.PositionsManager,
            self.grid_generator.coordinates
            )
        '''
        self.stageWorker = self.StageWorker(
            None,self.detector,
            self.grid_generator.coordinates
            )


        self.stageWorker.sigStageMoved.connect(self.measurementStep)
        self.stageThread = Thread()
        self.stageWorker.moveToThread(self.stageThread)
        self.sigMoveStage.connect(self.stageWorker.moveStageToNextPosition)
        self.stageThread.start()

        # start moving the stage
        self.sigMoveStage.emit()

    def finishMeasurement(self):
        ''' close all the variable and gui '''
        
        self.detector.stopAcquisition()

        self.storage.finish()
        self._widget._guiStopMeasurement()

        # update widget
        self._widget._plotStagePosition(
        self.stageWorker.stagePosX,
        self.stageWorker.stagePosY,
        self.stageWorker.stagePosIdx,
        self.stageWorker.nPos)

        self.increaseIdxOfFilename()



        # close the thread
        self.stageThread.quit()
        self.stageThread.wait()

    def interuptMeausurement(self):
        ''' interupt the measurment sequence before regular end'''
        self.stageWorker.skipMovementToEnd()

    def measurementStep(self, newPosition, recordedImage):
        ''' record single image'''
        #self.detector.startAcquisition()
        #self.looping = True
        self.__logger.debug('New measurement step')

#    def update(self, detectorName, im, init, scale, isCurrentDetector):
    #def update(self):

        ''' single step in the measurements sequence'''
        
        #self.__logger.debug('New Image')

        self.looping = True
        if self.looping:
        
            #self.detector.stopAcquisition()

            if not self.stageWorker.pathFinished:
            
                '''
                # record the image
                self.detector.startAcquisition()

                im = self.detector.getLatestFrame()

                while im.size == 0:
                    time.sleep(self.detector.parameters['exposure'].value/1e3/10)
                    im = self.detector.getLatestFrame()
                    self.__logger.debug(f' size {im.size}')

                self.detector.stopAcquisition()

                # get now recording image
                #myim = self.detector.getLatestFrame()
                myim = im
                '''
                myim = recordedImage

                self.__logger.debug(f"image size {myim.shape}") 

                self._widget.showPtychogram(myim)

                # save the image
                cameraName = self.detector.model
                picture_dictionary = {cameraName: dataContainer(data=myim, image=True, show_FT=False, show=True)}
                # info ... whole dataset
                info = {}
                info.update(picture_dictionary)
                self.storage.add_measurement(info)

                # update widget plot
                self._widget._plotStagePosition(
                    self.stageWorker.stagePosX,
                    self.stageWorker.stagePosY,
                    self.stageWorker.stagePosIdx,
                    self.stageWorker.nPos)
                
                # start moving the stage to new position
                self.sigMoveStage.emit()

            else:
                self.finishMeasurement()

            self.looping = False

    class StageWorker(Worker):
        '''' class to carry out the stage movement along certain path'''
        sigStageMoved = Signal(list, np.ndarray)
        stageOriginX = 0
        stageOriginY = 0

        def __init__(self,PositionerManager,Detector,coordinates:np.array):
            super().__init__()
            self.coordinates = coordinates
            self.nPos = len(self.coordinates)
            self.stagePosIdx = -1
            self.stagePosIdxMutex = Mutex()
            self.stagePosX = self.stageOriginX
            self.stagePosY = self.stageOriginY
            self.pathFinished = False
            self.PositionerManager = PositionerManager
            self.Detector = Detector

        def moveStageToNextPosition(self):
            self.stagePosIdxMutex.lock()
            self.stagePosIdx += 1
            self.stagePosIdxMutex.unlock()

            if self.stagePosIdx == self.nPos:
                self.pathFinished = True
                self.stagePosIdx = -1
                pos = [self.stageOriginX,self.stageOriginY]
            else:
                pos = self.coordinates[self.stagePosIdx]

            # move stage

            # TODO: termporarly not moving .. check the funtionality
            #myTempx = self.PositionerManager.move(0,'x')
            #myTempy = self.PositionerManager.move(0,'y')

            time.sleep(0.3)

            self.stagePosX = pos[0]
            self.stagePosY = pos[1]

            # take image
            self.Detector.startAcquisition()
            im = self.Detector.getLatestFrame()
            while im.size == 0:
                sleeptime = min(10e-3,self.Detector.parameters['exposure'].value/1e3/10)
                time.sleep(sleeptime)
                im = self.Detector.getLatestFrame()
            self.Detector.stopAcquisition()


            self.sigStageMoved.emit([pos[0],pos[1]],im)

        def skipMovementToEnd(self):
            self.stagePosIdxMutex.lock()
            self.stagePosIdx = self.nPos-1 
            self.stagePosIdxMutex.unlock()
            








        














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
