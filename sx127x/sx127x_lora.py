#Copyright <YEAR> <COPYRIGHT HOLDER>

#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

#    The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
from sx127x import *

REG_LR_FIFOADDRPTR       = 0x0d
REG_LR_FIFOTXBASEADDR    = 0x0e
REG_LR_FIFORXBASEADDR    = 0x0f
REG_LR_FIFORXCURRENTADDR = 0x10
REG_LR_IRQFLAGS          = 0x12
REG_LR_RXNBBYTES         = 0x13
REG_LR_PKTSNRVALUE       = 0x19
REG_LR_PKTRSSIVALUE      = 0x1a
REG_LR_CURRSSIVALUE      = 0x1b
REG_MODEMCONF1           = 0x1d
REG_MODEMCONF2           = 0x1e
REG_LR_PAYLOADLENGTH     = 0x22
REG_MODEMCONF3           = 0x26
REG_LR_TEST33            = 0x33
REG_LR_SX1276_AUTO_DRIFT = 0x36
REG_LR_GAIN_DRIFT        = 0x3a
REG_LR_DRIFT_INVERT      = 0x3b

class ModemConf1Bits1272(ctypes.LittleEndianStructure):
    _fields_ = [
        ("LowDataRateOptimize",  ctypes.c_uint8, 1),
        ("RxPayloadCrcOn",       ctypes.c_uint8, 1),
        ("ImplicitHeaderModeOn", ctypes.c_uint8, 1),
        ("CodingRate",           ctypes.c_uint8, 3),
        ("Bw",                   ctypes.c_uint8, 2),
    ]

class ModemConf1Bits1276(ctypes.LittleEndianStructure):
    _fields_ = [
        ("ImplicitHeaderModeOn", ctypes.c_uint8, 1),
        ("CodingRate",           ctypes.c_uint8, 3),
        ("Bw",                   ctypes.c_uint8, 4),
    ]

class ModemConf1(ctypes.Union):
    _fields_ = [
        ("sx1272bits", ModemConf1Bits1272),
        ("sx1276bits", ModemConf1Bits1276),
        ("octet", ctypes.c_uint8)
    ]

class ModemConf2Bits(ctypes.LittleEndianStructure):
    _fields_ = [
        ("SymbTimeout",      ctypes.c_uint8, 2),
        ("RxPayloadCrcOn",   ctypes.c_uint8, 1),
        ("TxContinuousMode", ctypes.c_uint8, 1),
        ("SpreadingFactor",  ctypes.c_uint8, 4),
    ]

class ModemConf2(ctypes.Union):
    _fields_ = [ ("bits", ModemConf2Bits), ("octet", ctypes.c_uint8) ]

class ModemConf3Bits(ctypes.LittleEndianStructure):
    _fields_ = [
        ("reserved",            ctypes.c_uint8, 2),
        ("AgcAutoOn",           ctypes.c_uint8, 1),
        ("LowDataRateOptimize", ctypes.c_uint8, 1),
        ("unused",              ctypes.c_uint8, 4),
    ]

class ModemConf3(ctypes.Union):
    _fields_ = [ ("bits", ModemConf3Bits), ("octet", ctypes.c_uint8) ]

class IrqFlagsBits(ctypes.LittleEndianStructure):
    _fields_ = [
        ("CadDetected",       ctypes.c_uint8, 1),
        ("FhssChangeChannel", ctypes.c_uint8, 1),
        ("CadDone",           ctypes.c_uint8, 1),
        ("TxDone",            ctypes.c_uint8, 1),
        ("ValidHeader",       ctypes.c_uint8, 1),
        ("PayloadCrcError",   ctypes.c_uint8, 1),
        ("RxDone",            ctypes.c_uint8, 1),
        ("RxTimeout",         ctypes.c_uint8, 1),
    ]


class IrqFlags(ctypes.Union):
    _fields_ = [ ("bits", IrqFlagsBits), ("octet", ctypes.c_uint8) ]

class RegAutoDriftBits(ctypes.LittleEndianStructure):
    _fields_ = [
        ("freq_to_time_drift_auto",    ctypes.c_uint8, 1),
        ("sd_max_freq_deviation_auto", ctypes.c_uint8, 1),
        ("reserved",                   ctypes.c_uint8, 6),
    ]

class RegAutoDrift(ctypes.Union):
    _fields_ = [ ("bits", RegAutoDriftBits), ("octet", ctypes.c_uint8) ]

class RegGainDriftBits(ctypes.LittleEndianStructure):
    _fields_ = [
        ("freq_to_time_drift",   ctypes.c_uint8, 6),
        ("preamble_timing_gain", ctypes.c_uint8, 2),
    ]

class RegGainDrift(ctypes.Union):
    _fields_ = [ ("bits", RegGainDriftBits), ("octet", ctypes.c_uint8) ]

class RegTest33Bits(ctypes.LittleEndianStructure):
    _fields_ = [
        ("chirp_invert_tx",    ctypes.c_uint8, 1),
        ("chirp_invert_rx",    ctypes.c_uint8, 1),
        ("sync_detect_th",     ctypes.c_uint8, 1),
        ("invert_coef_phase ", ctypes.c_uint8, 1),
        ("invert_coef_amp",    ctypes.c_uint8, 1),
        ("quad_correction_en", ctypes.c_uint8, 1),
        ("invert_i_q",         ctypes.c_uint8, 1),
        ("start_rambist",      ctypes.c_uint8, 1),
    ]


class RegTest33(ctypes.Union):
    _fields_ = [ ("bits", RegTest33Bits), ("octet", ctypes.c_uint8) ]

class RegDriftInvertBits(ctypes.LittleEndianStructure):
    _fields_ = [
        ("coarse_sync",                    ctypes.c_uint8, 1),
        ("fine_sync",                      ctypes.c_uint8, 1),
        ("invert_timing_error_per_symbol", ctypes.c_uint8, 1),
        ("invert_freq_error",              ctypes.c_uint8, 1),
        ("invert_delta_sampling",          ctypes.c_uint8, 1),
        ("reserved",                       ctypes.c_uint8, 1),
        ("invert_fast_timing",             ctypes.c_uint8, 1),
        ("invert_carry_in",                ctypes.c_uint8, 1),
    ]

class RegDriftInvert(ctypes.Union):
    _fields_ = [ ("bits", RegDriftInvertBits), ("octet", ctypes.c_uint8) ]


class sx127x_lora(object):
    def __init__(self, radio):
        if not radio.LongRangeMode: # to LoRa mode
            radio.LongRangeMode = 1
        self.ModemConf1 = ModemConf1()
        self.ModemConf2 = ModemConf2()
        if radio.chipType == 1276:
            self.ModemConf3 = ModemConf3()
        self.regIrqFlags = IrqFlags()
        self.regAutoDrift = RegAutoDrift()
        self.regAutoDrift.octet = radio.readReg(REG_LR_SX1276_AUTO_DRIFT)
        self.regGainDrift = RegGainDrift()
        self.regGainDrift.octet = radio.readReg(REG_LR_GAIN_DRIFT)
        self.regTest33 = RegTest33()
        self.regTest33.octet = radio.readReg(REG_LR_TEST33)
        self.regDriftInvert = RegDriftInvert()
        self.regDriftInvert.octet = radio.readReg(REG_LR_DRIFT_INVERT);
        self.radio = radio
        if radio.Dio0Mapping != 3:
            radio.Dio0Mapping = 3   # both TxDone and RxDone

    @property
    def PayloadLength(self):
        return self.radio.readReg(REG_LR_PAYLOADLENGTH)

    @PayloadLength.setter
    def PayloadLength(self, length):
        self.radio.writeReg(REG_LR_PAYLOADLENGTH, length)

    @property
    def SpreadingFactor(self):
        self.ModemConf2.octet = self.radio.readReg(REG_MODEMCONF2)
        return self.ModemConf2.bits.SpreadingFactor

    @SpreadingFactor.setter
    def SpreadingFactor(self, sf):
        self.ModemConf2.bits.SpreadingFactor = sf
        self.radio.writeReg(REG_MODEMCONF2, self.ModemConf2.octet)
        if self.symbolPeriodMs > 16:
            self.LowDataRateOptimize = 1
        else:
            self.LowDataRateOptimize = 0

    @property
    def bandwidth(self):
        self.ModemConf1.octet = self.radio.readReg(REG_MODEMCONF1)
        if self.radio.chipType == 1276:
            return {
                0: 7.8,
                1: 10.4,
                2: 15.6,
                3: 20.8,
                4: 31.25,
                5: 41.7,
                6: 62.5,
                7: 125,
                8: 250,
                9: 500
            }[self.ModemConf1.sx1276bits.Bw]
        elif self.radio.chipType == 1272:
            return { 0:125, 1:250, 2:500 }[self.ModemConf1.sx1272bits.Bw]

    @bandwidth.setter
    def bandwidth(self, bw):
        if self.radio.chipType == 1276:
            self.ModemConf1.sx1276bits.Bw = {
                7.8: 0,
                10.4: 1,
                15.6: 2,
                20.8: 3,
                31.25: 4,
                41.7: 5,
                62.5: 6,
                125: 7,
                250: 8,
                500: 9
            }[bw]

        elif self.radio.chipType == 1272:
            self.ModemConf1.sx1272bits.Bw = { 125:0, 250:1, 500:2 }[bw]

        self.radio.writeReg(REG_MODEMCONF1, self.ModemConf1.octet)
        if self.symbolPeriodMs > 16:
            self.LowDataRateOptimize = 1
        else:
            self.LowDataRateOptimize = 0

    @property
    def symbolPeriodMs(self):
        return (2.0 ** self.SpreadingFactor) / self.bandwidth

    @property
    def LowDataRateOptimize(self):
        if self.radio.chipType == 1276:
            self.ModemConf3.octet = self.radio.readReg(REG_MODEMCONF3)
            return self.ModemConf3.bits.LowDataRateOptimize
        elif self.radio.chipType == 1272:
            self.ModemConf1.octet = self.radio.readReg(REG_MODEMCONF1)
            return self.ModemConf1.sx1272bits.LowDataRateOptimize

    @LowDataRateOptimize.setter
    def LowDataRateOptimize(self, o):
        if self.radio.chipType == 1276:
            self.ModemConf3.bits.LowDataRateOptimize = o
            self.radio.writeReg(REG_MODEMCONF3, self.ModemConf3.octet)
        elif self.radio.chipType == 1272:
            self.ModemConf1.sx1272bits.LowDataRateOptimize = o
            self.radio.writeReg(REG_MODEMCONF1, self.ModemConf1.octet)

    @property
    def irqFlags(self):
        return self.radio.readReg(REG_LR_IRQFLAGS)

    @irqFlags.setter
    def irqFlags(self, f):
        self.radio.writeReg(REG_LR_IRQFLAGS, f)

    def tx(self, payload):
        self.PayloadLength = len(payload)
        self.radio.writeReg(REG_LR_FIFOADDRPTR, self.radio.readReg(REG_LR_FIFOTXBASEADDR))
        self.radio.writeFifo(payload)
        self.radio.OpMode = RF_OPMODE_TRANSMIT

    def rxCont(self):
        if self.radio.chipType == 1276:
            if self.bandwidth == 500:
                self.freq_to_time_drift_auto = 0
                if self.radio.HF:
                    self.freq_to_time_drift = 0x24
                else:
                    self.freq_to_time_drift = 0x3f
            else:
                self.freq_to_time_drift_auto = 1

        self.radio.writeReg(REG_LR_FIFOADDRPTR, self.radio.readReg(REG_LR_FIFORXBASEADDR))
        self.radio.OpMode = RF_OPMODE_RX_CONT

    @property
    def freq_to_time_drift(self):
        self.regGainDrift.octet = self.radio.readReg(REG_LR_GAIN_DRIFT)
        return self.regGainDrift.bits.freq_to_time_drift

    @freq_to_time_drift.setter
    def freq_to_time_drift(self, d):
        self.regGainDrift.bits.freq_to_time_drift = d
        self.radio.writeReg(REG_LR_GAIN_DRIFT, self.regGainDrift.octet)

    @property
    def freq_to_time_drift_auto(self):
        self.regAutoDrift.bits.freq_to_time_drift_auto = d
        self.regAutoDrift.octet = self.radio.readReg(REG_LR_SX1276_AUTO_DRIFT)
        
    @freq_to_time_drift_auto.setter
    def freq_to_time_drift_auto(self, a):
        self.radio.writeReg(REG_LR_SX1276_AUTO_DRIFT, self.regAutoDrift.octet)
        return self.regAutoDrift.bits.freq_to_time_drift_auto


    def readFifo(self):
        RegRxNbBytes = self.radio.readReg(REG_LR_RXNBBYTES)
        myList = [REG_FIFO] * (RegRxNbBytes + 1)
        self.radio.writeReg(REG_LR_FIFOADDRPTR, self.radio.readReg(REG_LR_FIFORXCURRENTADDR));
        resp = self.radio.spi.xfer2(myList)
        return resp[1:]

    @property
    def PktSnr(self):
        snr = self.radio.readReg(REG_LR_PKTSNRVALUE)
        if snr > 0x7f: # two's complement, signed 8bit value
            snr -= 0x80
        return snr / 4.0    # return dB in quarter-dB resolution

    def rssiOffset(self, rssi, pkt):
        if self.radio.chipType == 1276:
            if self.radio.HF:
                rssi -= 157
            else:
                rssi -= 164
        elif self.radio.chipType == 1272:
            rssi -= 139

        if pkt and self.PktSnr < 0:
            rssi += (self.PktSnr * 0.25)

        return rssi

    @property
    def PktRssi(self):
        return self.rssiOffset(self.radio.readReg(REG_LR_PKTRSSIVALUE), True)

    @property
    def CurrentRssi(self):
        return self.rssiOffset(self.radio.readReg(REG_LR_CURRSSIVALUE), False)

    @property
    def invert_tx(self):
        self.regTest33.octet = self.radio.readReg(REG_LR_TEST33)
        return not self.regTest33.bits.chirp_invert_tx

    @invert_tx.setter
    def invert_tx(self, i):
        self.regTest33.bits.chirp_invert_tx = not i
        self.radio.writeReg(REG_LR_TEST33, self.regTest33.octet)

    @property
    def invert_rx(self):
        self.regTest33.octet = self.radio.readReg(REG_LR_TEST33)
        return self.regTest33.bits.invert_i_q

    @invert_rx.setter
    def invert_rx(self, i):
        self.regTest33.bits.invert_i_q = i
        self.radio.writeReg(REG_LR_TEST33, self.regTest33.octet)
        # crystal error tracking:
        self.regDriftInvert.bits.invert_timing_error_per_symbol = not self.regTest33.bits.invert_i_q
        self.radio.writeReg(REG_LR_DRIFT_INVERT, self.regDriftInvert.octet);

