import numpy as np
from pathlib import Path

from ptypyLab.Model.GridGenerator import GridGenerator
from ptypyLab.Controller.Storage.h5 import DataStorage
from ptypyLab import dataContainer


from imswitch.imcommon.framework import Signal, Thread, Worker, Mutex
from imswitch.imcontrol.view import guitools
from ..basecontrollers import WidgetController

from imswitch.imcommon.model import initLogger

class PtychoController(WidgetController):
    """ Linked to PtychoWidget."""

    sigMoveStage = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__logger = initLogger(self)

        
        # define gridgenerator
        self.grid_generator = GridGenerator()
        # fixed parameters
        self.grid_generator.type = "square"
        self.grid_generator.extent_mm = "auto"  # either range in mm or 'auto' 0.4

        # extra parameters ... (temp)
        self.camera_exposure_time  = 0,
        self.camera_binning = 1,
        self.offset = [0,0]

        # parameters for the recording
        self.storage = None
        self.fullfilename = None

        # prepare gui
        self.updateParameters()

        # stage worker
        self.stageWorker = None
        self.stageThread = None
        
        # Connect PtychoWidget signals
        self._widget.sigStartMeasurement.connect(self.startMeasurement)
        self._widget.sigStopMeasurement.connect(self.interuptMeausurement)
        self._widget.sigUpdateParamters.connect(self.updateParameters)


    def updateParameters(self):
        """update parameters from the widget"""

        self.grid_generator.probe_size_mm = (
            self._widget.ptychoParameterTree.p.param("general").param("size of probe").value()
        )
        self.grid_generator.n_points_max = (
            self._widget.ptychoParameterTree.p.param("general")
            .param("number of points")
            .value()
        )
        self.grid_generator.overlap = (
            self._widget.ptychoParameterTree.p.param("general").param("overlap").value()
        )

        self.fullfilename = Path(
            self._widget.ptychoParameterTree.p.param("general").param("Saving folder").value(),
            self._widget.ptychoParameterTree.p.param("general").param("Saving filename").value()
        )
        self.grid_generator.prepare()
        self._widget._plotPath(self.grid_generator.coordinates)
        self._widget._plotStagePosition(self.stageX,self.stageY,
                                        self.stagePosIdx,
                                        len(self.grid_generator.coordinates))

        self.__logger.debug('Parameters updated')

    def startMeasurement(self):
        ''' prepare all the variable for recording and gui'''
        # create the data storage
        self.storage = DataStorage(self.fullfilename, append_tag=True)

        extra_info = dict(
            target_coordinate = self.grid_generator.coordinates,
            exposure_time=self.camera_exposure_time,
            binning=self.camera_binning,
            offset=self.offset,
        )
        self.storage.add_metadata(extra_info)

        # alocate date for the storage
        myimage = self._master.DetectorsManager.execOnCurrent(getLatestFrame)
        cameraName = 'testcam'
        picture_dictionary = {cameraName: dataContainer(data=myimage, image=True, show_FT=False, show=True)}
        info = {}
        info.update(picture_dictionary)
        self.storage.prepare_measurement(info,len(self.grid_generator.coordinates))
        print('allocating the space in the hdf5 file')

        # set gui
        self._widget._guiStartmeasurement()

        # prepare stage worker       
        self.stageWorker = self.StageWorker(
            self._master.PositionsManager,
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
        self.storage.finish()
        self._widget._guiStopMeasurement()

        # update widget plot
        self._widget._plotStagePosition(
        self.stageWorker.stagePosX,
        self.stageWorker.stagePosY,
        self.stageWorker.stagePosIdx,
        self.stageWorker.nPos)

        # close the thread
        self.stageThread.quit()
        self.stageThread.wait()

    def interuptMeausurement(self):
        ''' interupt the measurment sequence before regular end'''
        self.stageWorker.skipMovementToEnd()

    def measurementStep(self):
        ''' single step in the measurements sequence'''

        if not self.stageWorker.pathFinished:
        
            # record the image
            myimage = self._master.DetectorsManager.execOnCurrent(getLatestFrame)

            # save the image
            cameraName = 'testcam'
            picture_dictionary = {cameraName: dataContainer(data=myimage, image=True, show_FT=False, show=True)}
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


        
    class StageWorker(Worker):
        '''' class to carry out the stage movement along certain path'''
        sigStageMoved = Signal(list)
        stageOriginX = 0
        stageOriginY = 0

        def __init__(self,PositionerManager,coordinates:np.array):
            super().__init__()
            self.coordinates = coordinates
            self.nPos = len(self.coordinates)
            self.stagePosIdx = -1
            self.stagePosIdxMutex = Mutex()
            self.stagePosX = self.stageOriginX
            self.stagePosY = self.stageOriginY
            self.pathFinished = False
            self.PositionerManager = PositionerManager

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

            # TODO: termporarly not moving .. check the funtionality
            myTempx = self.PositionerManager.move(0,'x')
            myTempy = self.PositionerManager.move(0,'y')

            self.stagePosX = pos[0]
            self.stagePosY = pos[1]

            self.sigStageMoved.emit()

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
