import numpy as np


from imswitch.imcommon.framework import Signal, SignalInterface
from imswitch.imcommon.model import initLogger


class SLMbaseManager(SignalInterface):
    sigSLMMaskUpdated = Signal(object)  # (maskCombined)

    def __init__(self, slmInfo, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__logger = initLogger(self)

        if slmInfo is None:
            return

        self.__slmInfo = slmInfo
        self.__pixelsize = self.__slmInfo.pixelSize
        self.__slmSize = (self.__slmInfo.width, self.__slmInfo.height)

        self.__logger.debug(f'slmInfo : \n {self.__slmInfo}')

        self.slmImg = np.zeros((self.__slmSize[1],self.__slmSize[0]), dtype=np.uint8)
        self.newSlmImg = None

        self.setNewImage(self.slmImg)
        self.update()

    def update(self) -> np.array: 
        ''' update the SLM with the new image'''
        self.slmImg = self.newSlmImg
        self.__logger.debug(f'function update: singnal emitted')
        self.sigSLMMaskUpdated.emit(self.slmImg)
        return self.slmImg
    
    def setNewImage(self,image:np.array) -> None:
        ''' set in the buffer new image for slm'''
        self.newSlmImg = image
        self.__logger.debug(f'function setNewImage: new image')



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
