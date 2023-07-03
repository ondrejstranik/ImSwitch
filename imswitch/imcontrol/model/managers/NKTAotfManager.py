from imswitch.imcommon.model import initLogger


# TODO: the decorator is not working
def NKTconnected(method):
    ''' decorator for checking if NKT is connected'''
    def inner(instance):
        if instance._laser is None:
            instance.__logger.debug(' connection to NKT not established')
        else:
            method(instance)
    return inner


class NKTAotfManager:
    """ Manager for controlling the NKT aotf (acusto optical tunable filter)

        Manager properties:
        - ``nChannel`` -- number of channels, which can be independentally setup [optional]
        "ManagerProperties":
            -"id" -- id of the device (optional)
    """

    def __init__(self, aotfInfo, **lowLevelManagers):
        self.__logger = initLogger(self)
        
        try:
            import imswitch.imcontrol.model.interfaces.NktLaser as NktLaser
        except ImportError:
            self.__logger.error(' NktLaser package not found')
            return
        
        self._aotf = self._rs232manager = (
                    lowLevelManagers['rs232sManager']['NKT']._NKT
        )
        
        myid = None
        if "id" in aotfInfo.managerProperties:
            myid = aotfInfo.managerProperties['id']
            self.__logger.debug(f" aotf iD = {myid}")
        
        res = self._aotf.initAotf(myid)
        
        if res is None:
            self.__logger.debug(f" NKT aotf initialised")
        else:
            self.__logger.error(res)

        self._nChannel = aotfInfo.nChannel

    #@NKTconnected
    def setChannel(self, channelNumber, wavelength, amplitude):
        """ Set the value of the aotf  """
        self._aotf.setLaserChannel(channel=channelNumber,
                                   wavelength=wavelength,
                                   amplitude =amplitude)
        
        #self.__logger.debug(f" channel: {channelNumber} \n" +
        #                    f" wavelength: {wavelength} \n" + 
        #                    f" amplitude: {amplitude}")

    def getNChannel(self):
        return self._nChannel

    #@NKTconnected
    def finalize(self) -> None:
        """ Close/cleanup laser. """
        res = self._aotf.closeAotf()

        if res is None:
            self.__logger.debug(f" aotf high power closed")
        else:
            self.__logger.error(res)



         



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
