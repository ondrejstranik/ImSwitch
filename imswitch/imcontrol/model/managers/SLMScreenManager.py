import numpy as np


from imswitch.imcommon.framework import Signal, SignalInterface
from imswitch.imcommon.model import initLogger
from imswitch.imcontrol.view import SLMDisplay



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
        self.__monitorIdx = self.__slmInfo.monitorIdx


        self.__logger.debug(f'slmInfo : \n {self.__slmInfo}')

        self.slmImg = np.zeros((self.__slmSize[1],self.__slmSize[0]), dtype=np.uint8)
        self.visible = False

        self.slmDisplay = SLMDisplay(self, self.__monitorIdx)
        self.update()
        self.slmDisplay.setVisible(self.visible)


    def update(self): 
        ''' update the SLM. 
        Originates from slmPy:
        https://github.com/wavefrontshaping/slmPy        
        '''
        self.__logger.debug(f'function update')

        arr = self.slmImg
        
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

        self.slmDisplay.updateImage(img)
        
        # emit the signal
        self.sigSLMMaskUpdated.emit(self.slmImg)
    


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
