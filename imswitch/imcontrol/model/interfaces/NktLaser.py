try:
    from imswitch.imcontrol.model.interfaces.NKTP_DLL import *
except ImportError:
    print(" You do not have the NKT SDK installed. The NKT laser wont work.")

import numpy as np
import os
import logging


class NktLaserControl:
    name = "NktLaser"

    def __init__(self):
        self.com_str = None
        self.logger = logging.getLogger(self.name)
        self.laserId = 15
        self.aotfId = 17
        self.aotfId = 100


    def comConnect(self, comNumber):
        self.com_str = "COM" + str(comNumber)
        openResult = openPorts(self.com_str, 0, 0)
        return ('Opening the comport:', PortResultTypes(openResult))

    def comClose(self):
        closeResult = closePorts(self.com_str)
        return ('Closing the comport:', PortResultTypes(closeResult))



    def initLaser(self, id=None):
        if id is not None:
            self.laserId = id

        result = registerWriteU8(self.com_str, self.laserId, 0x30, 0x03, -1)
        mymessage = None
        if result != 0:
            mymessage = "can not start the laser"
        return mymessage
            
    def closeLaser(self):
        mymessage = None
        result = registerWriteU8(self.com_str, self.laserId, 0x30, 0x00, -1)
        if result != 0:
            mymessage = "can not close the laser power"
        return mymessage

    def setPowerLevel(self, power):
        registerWriteU16(self.com_str, self.laserId, 0x37, int(power * 10), -1)

    
    def initAotf(self,id = None):
        if id is not None:
            self.aotfId = id

        mymessage = None
        result = registerWriteU8(self.com_str,self.aotfId, 0x30, 1, -1)
        if result != 0:
            mymessage = "can not start the aotf high power"
        return mymessage


    def closeAotf(self):
        mymessage = None
        result = registerWriteU8(self.com_str,self.aotfId, 0x30, 0, -1)
        if result != 0:
            mymessage = "can not close the aotf high power"
        return mymessage

    def setLaserChannel(self, channel, wavelength, amplitude):
        ''' set the wavelength in nm'''
        # set wavelength 
        registerWriteU32(self.com_str, self.aotfId, int(0x90 + channel), int(wavelength * 1000), -1)
        # set power
        registerWriteU16(self.com_str, self.aotfId, int(0xB0 + channel), int(amplitude * 10), -1)

    def getLaserChannelWavelength(self,channel):
        ''' return wavelength in nm'''
        return registerReadU32(self.com_str, self.aotfId, int(0x90 + channel),-1)[1]/1000


    def allChannelZeroAmplitude(self):
        for ii in range(8):
            registerWriteU16(self.com_str, self.aotfId, int(0xB0 + ii), 0, -1)

    def finalise(self):
        # Close com port
        return self.comClose()