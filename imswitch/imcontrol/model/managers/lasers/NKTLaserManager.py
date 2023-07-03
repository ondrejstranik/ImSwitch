from imswitch.imcommon.model import initLogger
from .LaserManager import LaserManager
import os


# TODO: the decorator is not working
def NKTconnected(method):
    ''' decorator for checking if NKT is connected'''
    def inner(instance):
        if instance._laser is None:
            instance.__logger.debug(' connection to NKT not established')
        else:
            method(instance)
    return inner


class NKTLaserManager(LaserManager):
    """ LaserManager for controlling the NKT white light laser

    Manager properties:
    "ManagerProperties":
    - ``id`` -- id of the device (optional)
    """

    def __init__(self, laserInfo, name, **lowLevelManagers):
        self.__logger = initLogger(self, instanceName=name)
        
        try:
            import imswitch.imcontrol.model.interfaces.NktLaser as NktLaser
        except ImportError:
            self.__logger.error(' NktLaser package not found')
            return

        self._laser = self._rs232manager = (
                    lowLevelManagers['rs232sManager']['NKT']._NKT
        )

        myid = None
        if "id" in laserInfo.managerProperties:
            myid = laserInfo.managerProperties['id']
            self.__logger.debug(f" laser iD = {myid}")

        res = self._laser.initLaser(myid)
        if res is None:
            self.__logger.debug("NKT laser initialised")
        else:
            self.__logger.error(res)
    
        self._power = 0
        self._enabled = False
        super().__init__(laserInfo, name, isBinary=False, valueUnits='mW', valueDecimals=0, isModulated=False)

    #@NKTconnected
    def setEnabled(self, enabled):
        """Turn on or off laser emission"""
        if enabled:
           self._enabled = True
           self._laser.setPowerLevel(self._power)
           self.__logger.debug(f"Laser power set to {self._power}")

        else:
            self._enabled = False
            self._laser.setPowerLevel(0)
            self.__logger.debug(f"Laser power set to 0")

    #@NKTconnected
    def setValue(self, power):
        """ Set the value of laser """
        self._power = power

        if self._enabled:
            self._laser.setPowerLevel(self._power)


    #@NKTconnected
    def finalize(self) -> None:
        """ Close/cleanup laser. """
        res = self._laser.closeLaser()

        if res is None:
            self.__logger.debug(f" laser power closed")
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
