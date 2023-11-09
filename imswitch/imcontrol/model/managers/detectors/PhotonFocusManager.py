import numpy as np

from imswitch.imcommon.model import initLogger
from .DetectorManager import DetectorManager,DetectorAction, DetectorNumberParameter, DetectorListParameter


class PhotonFocusManager(DetectorManager):
    """ DetectorManager that deals with PhotonFocus cameras and the
    parameters for frame extraction from them.

    Manager properties:

    - ``cameraListIndex`` -- the camera's index in the Allied Vision camera list (list
      indexing starts at 0); set this string to an invalid value, e.g. the
      string "mock" to load a mocker
    - ``av`` -- dictionary of Allied Vision camera properties
    """

    def __init__(self, detectorInfo, name, **_lowLevelManagers):
        self.__logger = initLogger(self, instanceName=name)

        cameraId = detectorInfo.managerProperties['cameraListIndex']
        self._camera = self._getGXObj(cameraId )
        self._binning = 1

        
        for propertyName, propertyValue in detectorInfo.managerProperties['pf'].items():
            self._camera.SetParameter(propertyName, propertyValue)

        fullShape = (self._camera.GetParameter("Width"), 
                     self._camera.GetParameter("Height"))

        model = self._camera.GetParameter("DeviceVendorName")

        # Prepare parameters
        parameters = {
            'exposure': DetectorNumberParameter(group='Misc', value=100, valueUnits='ms',
                                                editable=True),
            'PixelFormat': DetectorListParameter(group='Misc', value= "Mono8",
                                                 options = ['Mono8', 'Mono12'], editable=True),
            'image_width': DetectorNumberParameter(group='Misc', value=fullShape[0], valueUnits='px',
                        editable=False),
            'image_height': DetectorNumberParameter(group='Misc', value=fullShape[1], valueUnits='px',
                        editable=False)
            }            

        super().__init__(detectorInfo, name, fullShape=fullShape, supportedBinnings=[1],
                         model=model, parameters=parameters, croppable=False)
        

    def getLatestFrame(self):
        self.__logger.debug(f'Trying to acquire Image')
        ( _, image) = self._camera.getLastImage(waitForValidImage=True)
        self.__logger.debug(f'Acquired Image')

        return image

    def setParameter(self, name, value):
        """Sets a parameter value and returns the value.
        If the parameter doesn't exist, i.e. the parameters field doesn't
        contain a key with the specified parameter name, an error will be
        raised."""

        super().setParameter(name, value)

        if name not in self._DetectorManager__parameters:
            raise AttributeError(f'Non-existent parameter "{name}" specified')

        if name == 'exposure':
            value = self._camera.SetParameter('ExposureTime', int(value*1000))
        else:
            value = self._camera.SetParameter(name, value)
        return value

    def getParameter(self, name):
        """Gets a parameter value and returns the value.
        If the parameter doesn't exist, i.e. the parameters field doesn't
        contain a key with the specified parameter name, an error will be
        raised."""

        if name not in self._parameters:
            raise AttributeError(f'Non-existent parameter "{name}" specified')

        if name == 'exposure':
            value = self._camera.GetParameter("ExposureTime")/1000

        value = self._camera.GetParameter(name)
        return value

        
    def getChunk(self):
        pass

    def flushBuffers(self):
        pass

    def startAcquisition(self):
        self._camera.StartAcquisition()
        pass
    
    def stopAcquisition(self):
        self._camera.StopAcquisition()


    def stopAcquisitionForROIChange(self):
        pass
    
    def finalize(self) -> None:
        super().finalize()
        self.__logger.debug('Safely disconnecting the camera...')
        self._camera.DisconnectCamera()

    @property
    def pixelSizeUm(self):
        return [1, 1, 1]

    def crop(self, hpos, vpos, hsize, vsize):
        pass 

    def _getGXObj(self, cameraId, binning=1):
        try:
            from imswitch.imcontrol.model.interfaces.photonFocusCamera import Photonfocus
            self.__logger.debug(f'Trying to initialize Photonfocus camera {cameraId}')
            camera = Photonfocus()
            camera.PrepareCamera(cameraIdx= cameraId)
            #camera.StartAcquisition()
        except Exception as e:
            self.__logger.debug(e)
            self.__logger.warning(f'Failed to initialize Photonfocus {cameraId}, loading TIS mocker')
            from imswitch.imcontrol.model.interfaces.tiscamera_mock import MockCameraTIS
            camera = MockCameraTIS()


        self.__logger.info(f'Initialized camera, model: {camera.GetParameter("DeviceVendorName")}')
        return camera

    def closeEvent(self):
        self._camera.DisconnectCamera()

# Copyright (C) ImSwitch developers 2021
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
