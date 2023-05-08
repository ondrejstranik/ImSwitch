import importlib
from .LaserManager import LaserManager
from imswitch.imcommon.model import pythontools, initLogger
import time

class PyMicroscopeFilterWheelManager(LaserManager):
    """ Generic FilterWheelManager for FilterWheels handlers supported by Python Microscope.

    Manager properties:

    - ``pyMicroscopeDriver`` -- string describing the Python Microscope
        object to initialize; requires to specify the module
        and the class name, e.g. ``filterwheel.thorlabs``
    - ``digitalPorts`` -- string describing the COM port
        to connect to, e.g. ``["COM4"]``
    """
    def __init__(self, laserInfo, name, **_lowLevelManager) -> None:
        self.__logger = initLogger(self, instanceName=name)
        self.__port = laserInfo.managerProperties["digitalPorts"]
        self.__driver = str(laserInfo.managerProperties["pyMicroscopeDriver"])
        driver = self.__driver.split(".")
        package = importlib.import_module(
            pythontools.joinModulePath(
            pythontools.joinModulePath("microscope", driver[0]),
            driver[1])
        )
        self.__laser = getattr(package, driver[2])(self.__port)
        self.__logger.info(f"[{self.__port}] {self.__driver} initialized. ")
        super().__init__(laserInfo, name, isBinary=False, valueUnits='position', valueDecimals=0)
        
        # set the number of position on the wheel 
        self.__freqRangeMin = 0
        self.__freqRangeMax = self.__laser.n_positions -1
    
    def setEnabled(self, enabled: bool) -> None:
        (self.__laser.enable() if enabled else self.__laser.disable())
    
    def setValue(self, value) -> None:
        # laser power is handled as percentage
        # so we divide for the max power to obtain
        # the actual percentage to which we set
        # the output power
        self.__laser.power = float(value) 
        self.__laser.position = int(value)
        # wait till the new position is set
        time.sleep(1)

    def finalize(self) -> None:
        self.__logger.info(f"[{self.__port}] {self.__driver} closed.")
        self.__laser.shutdown()