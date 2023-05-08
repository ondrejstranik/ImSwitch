import unittest
''' test of camera for imswitch'''

#%% 
from imswitch.imcontrol.model.interfaces.tiscamera_mock import MockCameraTIS
import numpy as np

from imswitch.imcontrol.model import configfiletools

from imswitch.imcontrol.model.managers.detectors.AVManager import AVManager
import logging

from imswitch.imcontrol.view import ViewSetupInfo

# %%
logger = logging.getLogger('test AVcamera')
logging.basicConfig(level=logging.INFO)



class Test_test1(unittest.TestCase):
    def setUp(self) -> None:
        # %%
        options, optionsDidNotExist = configfiletools.loadOptions()
        # %%
        setupInfo = configfiletools.loadSetupInfo(options, ViewSetupInfo)
        # %%
        p_info = setupInfo.detectors['SLM_WidefieldCamera']


        # %%
        self.camera = AVManager(p_info, name="AV camera")
        # %%

    def tearDown(self) -> None:
        self.camera.finalize()


    def test_camera_connected(self):
        print(type(self.camera))
        self.assertNotEqual(self.camera.model, "mock")

    def test_camera_shape(self):
        self.camera.setBinning(2)
        self.assertEqual()



        

if __name__ == '__main__':
    unittest.main()