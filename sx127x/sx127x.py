#Copyright <YEAR> <COPYRIGHT HOLDER>

#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

#    The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import spidev
import ctypes
import time
 
class OpModeBits(ctypes.LittleEndianStructure):
    _fields_ = [
        ("Mode",              ctypes.c_uint8, 3),
        ("ModulationShaping", ctypes.c_uint8, 2),
        ("ModulationType",    ctypes.c_uint8, 2),
        ("LongRangeMode",     ctypes.c_uint8, 1),
    ]

class sx1276LoRaBits(ctypes.LittleEndianStructure):
    _fields_ = [
        ("Mode",               ctypes.c_uint8, 3),
        ("LowFrequencyModeOn", ctypes.c_uint8, 1),
        ("none",               ctypes.c_uint8, 1),
        ("ModulationType",     ctypes.c_uint8, 2),
        ("LongRangeMode",      ctypes.c_uint8, 1),
    ]


class RegOpMode(ctypes.Union):
    _fields_ = [
        ("bits", OpModeBits),
        ("sx1276LORAbits", sx1276LoRaBits),
        ("octet", ctypes.c_uint8)
    ]

class DioMapping1Bits(ctypes.LittleEndianStructure):
    _fields_ = [
        ("Dio3Mapping", ctypes.c_uint8, 2),
        ("Dio2Mapping", ctypes.c_uint8, 2),
        ("Dio1Mapping", ctypes.c_uint8, 2),
        ("Dio0Mapping", ctypes.c_uint8, 2),
    ]

class DioMapping1(ctypes.Union):
    _fields_ = [ ("bits", DioMapping1Bits), ("octet", ctypes.c_uint8) ]

class PaConfigBits(ctypes.LittleEndianStructure):
    _fields_ = [
        ("OutputPower", ctypes.c_uint8, 4),
        ("MaxPower",    ctypes.c_uint8, 3),
        ("PaSelect",    ctypes.c_uint8, 1),
    ]

class PaConfig(ctypes.Union):
    _fields_ = [ ("bits", PaConfigBits), ("octet", ctypes.c_uint8) ]

class PdsTrimBits(ctypes.LittleEndianStructure):
    _fields_ = [
        ("prog_txdac",      ctypes.c_uint8, 3), # bandgap reference current for PA DAC
        ("pds_analog_test", ctypes.c_uint8, 1),
        ("pds_pa_test",     ctypes.c_uint8, 2), # PDS PA test mode
        ("pds_ptat",        ctypes.c_uint8, 2), # trimming of PTAT master bias current
    ]

class PdsTrim(ctypes.Union):
    _fields_ = [ ("bits", PdsTrimBits), ("octet", ctypes.c_uint8) ]


XTAL_FREQ    = 32000000

FREQ_STEP_MHZ  =   61.03515625e-6    # 32 / (2^19)
FREQ_STEP_KHZ  =   61.03515625e-3    # 32e3 / (2^19)
FREQ_STEP_HZ   =   61.03515625       # 32e6 / (2^19)

REG_FIFO             = 0x00
REG_OPMODE           = 0x01
REG_FRF              = 0x06
REG_PACONFIG         = 0x09
REG_DIOMAPPING1      = 0x40
REG_PDSTRIM1_SX1276  = 0x4d
REG_PDSTRIM1_SX1272  = 0x5a

RF_OPMODE_SLEEP     = 0
RF_OPMODE_STANDBY   = 1
RF_OPMODE_TRANSMIT  = 3
RF_OPMODE_RX_CONT   = 5
RF_OPMODE_RX_SINGLE = 6

class sx127x(object):

    def __init__(self, antcb):
        self.spi = spidev.SpiDev()
        self.spi.open(0,0)
        self.ant_callback = antcb
        self.regOpMode = RegOpMode()
        self.DioMapping1 = DioMapping1()
        self.PaConfig = PaConfig()
        self.PaConfig.octet = self.readReg(REG_PACONFIG)
        # for detecting chip type (sx1276 vs sx1272), put it into LoRa mode
        # sx1272 doesnt have LowFrequencyModeOn bit in LoRa mode
        if not self.LongRangeMode:
            if self.regOpMode.bits.Mode != RF_OPMODE_SLEEP:
                self.OpMode = RF_OPMODE_SLEEP
                time.sleep(0.01)
            self.LongRangeMode = 1

        if self.regOpMode.sx1276LORAbits.LowFrequencyModeOn:
            self.chipType = 1276
        else:
            self.LowFrequencyModeOn = 1
            if self.LowFrequencyModeOn:
                self.chipType = 1276
            else:
                self.chipType = 1272

        print ("chip type:%u" % self.chipType)
        self.pds_trim = PdsTrim()
        if self.chipType == 1276:
            self.pds_trim.octet = self.readReg(REG_PDSTRIM1_SX1276);
        elif self.chipType == 1272:
            self.pds_trim.octet = self.readReg(REG_PDSTRIM1_SX1276);


    @property
    def OpMode(self):
        self.regOpMode.octet = self.readReg(REG_OPMODE)
        return self.regOpMode.bits.Mode

    @OpMode.setter
    def OpMode(self, value):
        self.regOpMode.bits.Mode = value;
        self.ant_callback(value)
        self.writeReg(REG_OPMODE, self.regOpMode.octet)

    @property
    def ModulationType(self):
        self.regOpMode.octet = self.readReg(REG_OPMODE)
        return self.regOpMode.bits.ModulationType

    @ModulationType.setter
    def ModulationType(self, t):
        self.regOpMode.bits.ModulationType = t
        self.writeReg(REG_OPMODE, self.regOpMode.octet)

    @property
    def LongRangeMode(self):
        self.regOpMode.octet = self.readReg(REG_OPMODE)
        return self.regOpMode.bits.LongRangeMode

    @LongRangeMode.setter
    def LongRangeMode(self, lrm):
        if self.OpMode != RF_OPMODE_SLEEP:
            self.OpMode = RF_OPMODE_SLEEP 
            time.sleep(0.005)
        self.regOpMode.bits.LongRangeMode = lrm
        self.writeReg(REG_OPMODE, self.regOpMode.octet)

    @property
    def Dio0Mapping(self):
        self.DioMapping1.octet = self.readReg(REG_DIOMAPPING1)
        return self.DioMapping1.bits.Dio0Mapping

    @Dio0Mapping.setter
    def Dio0Mapping(self, m):
        self.DioMapping1.bits.Dio0Mapping = m
        self.writeReg(REG_DIOMAPPING1, self.DioMapping1.octet)

    @property
    def PaSelect(self):
        self.PaConfig.octet = self.readReg(REG_PACONFIG)
        return self.PaConfig.bits.PaSelect

    @PaSelect.setter
    def PaSelect(self, b):
        self.PaConfig.bits.PaSelect = b
        self.writeReg(REG_PACONFIG, self.PaConfig.octet)

    @property
    def MHz(self):
        resp = self.spi.xfer2([REG_FRF, 0, 0, 0])
        frf = (resp[1] << 16) + (resp[2] << 8) + resp[3]
        ret = frf * FREQ_STEP_MHZ
        if ret < 525:
            self.HF = False
        else:
            self.HF = True
        return ret

    @MHz.setter
    def MHz(self, Mhz):
        frf = int(Mhz / FREQ_STEP_MHZ)
        msb = frf >> 16
        mid = frf >> 8
        resp = self.spi.xfer2([REG_FRF | 0x80, msb, mid, frf])
        if Mhz < 525:
            self.HF = False
        else:
            self.HF = True

    def readReg(self, addr):
        resp = self.spi.xfer2([addr, 0x00])
        return resp[1]

    def writeReg(self, addr, value):
        resp = self.spi.xfer2([addr | 0x80, value])

    def writeFifo(self, payload):
        myList = [REG_FIFO | 0x80] + payload
        resp = self.spi.xfer2(myList)
        #print ("myList len %u" % len(myList))

    @property
    def tx_dBm(self):
        if self.chipType == 1276:
            self.pds_trim.octet = self.readReg(REG_PDSTRIM1_SX1276);
        elif self.chipType == 1272:
            self.pds_trim.octet = self.readReg(REG_PDSTRIM1_SX1276);
        self.PaConfig.octet = self.readReg(REG_PACONFIG)
        if self.PaConfig.bits.PaSelect == 1:
            if self.pds_trim.bits.prog_txdac == 7:
                return self.PaConfig.bits.OutputPower + 5
            else:
                return self.PaConfig.bits.OutputPower + 2
        else:
            pmax = (0.6 * self.PaConfig.bits.MaxPower) + 10.8
            return pmax - (15 - self.PaConfig.bits.OutputPower)

    @tx_dBm.setter
    def tx_dBm(self, dBm):
        self.PaConfig.octet = self.readReg(REG_PACONFIG)
        if self.PaConfig.bits.PaSelect == 1: # PA_BOOST:
            if dBm > 17:
                if dBm > 20:
                    dBm = 20
                self.PaConfig.bits.OutputPower = dBm - 5
                self.pds_trim.bits.prog_txdac = 7   # PA DAC bandgap reference at max
            else:
                if dBm < 2:
                    dBm = 2
                self.PaConfig.bits.OutputPower = dBm - 2
                self.pds_trim.bits.prog_txdac = 4   # PA DAC bandgap reference at default

            if self.chipType == 1276:
                self.writeReg(REG_PDSTRIM1_SX1276, self.pds_trim.octet)
            elif self.chipType == 1272:
                self.writeReg(REG_PDSTRIM1_SX1276, self.pds_trim.octet)
        else: # RFO:
            if dBm > 14:
                dBm = 14
            elif dBm < -1:
                dBm = -1
            self.PaConfig.bits.OutputPower = dBm + 1

        self.writeReg(REG_PACONFIG, self.PaConfig.octet)

