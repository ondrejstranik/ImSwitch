from imswitch.imcommon.model import initLogger
import os

class NKTManager:
    """ A wrapper manager to controll NKT devices

    Manager properties:

    - ``pathToSDK`` -- path to the DLL controlling the laser
    """

    def __init__(self, rs232Info, name, **lowLevelManagers):
        self.__logger = initLogger(self, instanceName=name)
        self._settings = rs232Info.managerProperties
        self._name = name

        try:
            os.environ['NKTP_SDK_PATH'] = rs232Info.managerProperties['pathToSDK']
            import imswitch.imcontrol.model.interfaces.NktLaser as NktLaser
        except ImportError:
            self.__logger.error(' NktLaser package not found')
        
        self._NKT = NktLaser.NktLaserControl()
        res = self._NKT.comConnect(rs232Info.managerProperties['COM'])
        self.__logger.debug(res)

    def finalize(self) -> None:
        """ Close/cleanup NKT communication """
        self.__logger.debug(self._NKT.finalise())


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
