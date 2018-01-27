#Copyright <YEAR> <COPYRIGHT HOLDER>

#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

#    The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
from sx127x import *
import math

REG_FSK_BITRATEMSB    = 0x02
REG_FSK_PACKETCONFIG2 = 0x31
REG_FSK_FDEV          = 0x04
REG_FSK_RXBW          = 0x12
REG_FSK_AFCBW         = 0x13

class RegBwBits(ctypes.LittleEndianStructure):
    _fields_ = [
        ("Exponent", ctypes.c_uint8, 3),
        ("Mantissa", ctypes.c_uint8, 2),
        ("dccForce", ctypes.c_uint8, 1),
        ("dccFastInit", ctypes.c_uint8, 1),
        ("reserved", ctypes.c_uint8, 1),
    ]


class RegBw(ctypes.Union):
    _fields_ = [ ("bits", RegBwBits), ("octet", ctypes.c_uint8) ]

class RegPktConfig2Bits(ctypes.LittleEndianStructure):
    _fields_ = [
        ("PayloadLength",    ctypes.c_uint16, 11),
        ("BeaconOn",         ctypes.c_uint16, 1),
        ("IoHomePowerFrame", ctypes.c_uint16, 1),
        ("IoHomeOn",         ctypes.c_uint16, 1),
        ("DataModePacket",   ctypes.c_uint16, 1),
        ("reserved",         ctypes.c_uint16, 1),
    ]

class RegPktConfig2(ctypes.Union):
    _fields_ = [ ("bits", RegPktConfig2Bits), ("word", ctypes.c_uint16) ]


RegBw
class sx127x_fsk(object):

    def __init__(self, radio):
        if not radio.LongRangeMode: # to FSK mode
            radio.LongRangeMode = 0
        self.regPktConfig2 = RegPktConfig2()
        self.radio = radio

    @property
    def txFDevHz(self):
        resp = self.radio.spi.xfer2([REG_FSK_FDEV, 0, 0])
        ret = (resp[1] << 8) + resp[2]
        return ret * FREQ_STEP_HZ

    @txFDevHz.setter
    def txFDevHz(self, hz):
        tmp = int(hz / FREQ_STEP_HZ)
        lst = [REG_FSK_FDEV | 0x80]
        lst.append(tmp >> 8)
        lst.append(tmp & 0xff)
        resp = self.radio.spi.xfer2(lst)

    @property
    def datarate_bps(self):
        resp = self.radio.spi.xfer2([REG_FSK_BITRATEMSB, 0, 0])
        br = (resp[1] << 8) + resp[2]
        if br == 0:
            return 0
        else:
            return XTAL_FREQ / br

    @datarate_bps.setter
    def datarate_bps(self, bps):
        tmp = XTAL_FREQ / bps
        lst = [REG_FSK_BITRATEMSB | 0x80]
        lst.append(tmp >> 8)
        lst.append(tmp & 0xff)
        self.radio.spi.xfer2(lst)

    def rxBw(self, octet):
        reg_bw = RegBw()
        reg_bw.octet = octet
        mantissa = {
            0: 16,
            1: 20,
            2: 24
            }[reg_bw.bits.Mantissa]
        if self.radio.ModulationType == 0:
            return XTAL_FREQ / (mantissa * (1 << (reg_bw.bits.Exponent+2)))
        else:
            return XTAL_FREQ / (mantissa * (1 << (reg_bw.bits.Exponent+3)))

    def setbw(self, hz, addr):
        m = 0
        reg_bw = RegBw()
        rxBwMin = 10e6
        if self.radio.ModulationType == 0:
            expOfs = 2
        else:
            expOfs = 3
        for tmpExp in range(0, 8):
            for tmpMant in range(16, 25, 4):
                tmpRxBw = XTAL_FREQ / (tmpMant * (1 << (tmpExp + expOfs)))
                this = math.fabs(tmpRxBw - hz)
                if this < rxBwMin:
                    rxBwMin = this
                    m = tmpMant
                    reg_bw.bits.Exponent = tmpExp
        reg_bw.bits.Mantissa = {
            16: 0,
            20: 1,
            24: 2 
            }[m]
        self.radio.writeReg(addr, reg_bw.octet)
        

    @property
    def rxBwHz(self):
        reg = self.radio.readReg(REG_FSK_RXBW)
        #return self.rxBw(self.radio.readReg(REG_FSK_RXBW))
        return self.rxBw(reg)

    @rxBwHz.setter
    def rxBwHz(self, hz):
        self.setbw(hz, REG_FSK_RXBW)

    @property
    def afcBwHz(self):
        return self.rxBw(self.radio.readReg(REG_FSK_AFCBW))

    @afcBwHz.setter
    def afcBwHz(self, hz):
        self.setbw(hz, REG_FSK_AFCBW)

    @property
    def DataModePacket(self):
        resp = self.radio.spi.xfer2([REG_FSK_PACKETCONFIG2, 0, 0])
        self.regPktConfig2.word = (resp[1] << 8) + resp[2]
        return self.regPktConfig2.bits.DataModePacket

