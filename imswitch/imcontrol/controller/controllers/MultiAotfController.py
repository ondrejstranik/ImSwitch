from ..basecontrollers import ImConWidgetController
from imswitch.imcommon.model import initLogger

class MultiAOTFController(ImConWidgetController):
    """ Linked to MultiAotfWidget."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__logger = initLogger(self)

        self.aotf = self._master.aotfManager

        self.nChannel = self.aotf.getNChannel()

        self.channelInfo = [ {"channelN":ii, "wavelength":500,"intensity":0} 
                            for ii in range(self.nChannel)]

       
        # set number of channels
        self._widget.setNumberOfChannels(self.nChannel)

        # Connect Widget signals
        self._widget.sigUpdateParameters.connect(self.updateParametersFromWidget)


    def setAllChannelAotf(self):
        ''' set the Aotf'''
        for ii in range(self.nChannel):

            self.aotf.setChannel(self.channelInfo[ii]["channelN"],
                                 self.channelInfo[ii]["wavelength"],
                                 self.channelInfo[ii]["intensity"])
            #self.__logger.debug(f'channelinfo : \n {self.channelInfo[ii]}')

    def updateParametersFromWidget(self):
        """update parameters from the widget"""

        self.channelInfo = []

        for ii in range(self.nChannel):
            cInfo = self._widget.getChannelInfo(ii+1)
            self.channelInfo.append({
                "channelN": ii,
                "wavelength": cInfo["wavelength"],
                "intensity": cInfo["intensity"]*int(cInfo["active"])
                })

        #self.__logger.debug(f'channelinfo : \n {self.channelInfo}')

        self.setAllChannelAotf()


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
