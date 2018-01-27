#!/usr/bin/python
from PyCRC.CRCCCITT import CRCCCITT
from PyCRC.CRC16 import CRC16
from PyCRC.CRC16DNP import CRC16DNP
from PyCRC.CRC16Kermit import CRC16Kermit
from PyCRC.CRC16SICK import CRC16SICK
import time
import sys
import array
import sx127x
import RPi.GPIO as GPIO


PIN_ANT_SW = 22
PIN_DIO0   = 18

GPIO.setmode(GPIO.BOARD)
GPIO.setup(PIN_DIO0, GPIO.IN) # dio0 input
GPIO.setup(PIN_ANT_SW, GPIO.OUT) # antenna switch output

def ant_switch(OpMode):
    if OpMode == sx127x.RF_OPMODE_TRANSMIT:
        GPIO.output(PIN_ANT_SW, GPIO.HIGH)
    else:
        GPIO.output(PIN_ANT_SW, GPIO.LOW)

radio = sx127x.sx127x(ant_switch)
lora = sx127x.sx127x_lora(radio)

if not radio.LongRangeMode:
    radio.LongRangeMode = 1

if GPIO.input(PIN_DIO0):
    print ("dio0 high 0x%x" % lora.irqFlags)
    lora.irqFlags = 0xff   # clear all interrupt flags
    if GPIO.input(PIN_DIO0):
        print ("dio0 still high 0x%x" % lora.irqFlags)
        sys.exit()

def dio0_callback(channel):
    lora.regIrqFlags.octet = lora.irqFlags
    if lora.regIrqFlags.bits.TxDone:
        print "start rx...",
        lora.rxCont()
        sys.stdout.flush()
    elif lora.regIrqFlags.bits.RxDone:
        print ("RxDone rssi:%.2fdBm snr:%.2fdB " % (lora.PktRssi, lora.PktSnr)),
        rxPayload = lora.readFifo()
        print rxPayload # payload with crc
        rxString = array.array('B', rxPayload[:-2]).tostring()
        c = CRCCCITT().calculate(rxString) # CRC-CCITT (Xmodem)
        print "calcCrc:%04x" % c
        rxCrc = int(rxPayload[-2]) << 8
        rxCrc += int(rxPayload[-1])
        print "rxcrc:%04x" % rxCrc
        if rxCrc == c:
            print "crc ok"
        else:
            print "crc-bad"
        print rxPayload[:-2] # payload without crc
    else:
        print "unhandled irq %02x" % lora.regIrqFlags.octet
    lora.irqFlags = 0xff   # clear all interrupt flags

GPIO.add_event_detect(PIN_DIO0, GPIO.RISING, callback=dio0_callback, bouncetime=1)

radio.MHz = 902.9
print ("%.3fMHz" % radio.MHz)

radio.PaSelect = 0  # check schematic of your board, is RFO or PABOOST connected?
print ("PaSelect:%u" % radio.PaSelect)
lora.SpreadingFactor = 8
print ("SpreadingFactor:%u" % lora.SpreadingFactor)

input = '123456789'
#print(CRCCCITT().calculate(input))
c = CRCCCITT().calculate(input) # CRC-CCITT (Xmodem)
print "CCITT :%x " % c
c = CRC16().calculate(input)    # CRC-16
print "CRC16 :%x " % c
c = CRC16DNP().calculate(input)    # CRC-DNP
print "CRC16DNP :%x " % c
c = CRC16Kermit().calculate(input)    # CRC-CCITT (Kermit)
print "CRC16Kermit:%x " % c
c = CRC16SICK().calculate(input)    # CRC-16 (Sick)
print "CRC16SICK:%x " % c


buf = [ord(ch) for ch in input]
print "tx buf:",
print buf
stringForCRC = array.array('B', buf).tostring()
print "tx stringForCRC :",
print stringForCRC 
c = CRCCCITT().calculate(stringForCRC) # CRC-CCITT (Xmodem)
print "tx CCITT :%x (buf)" % c
print "c-type:",
print type(c)
buf.append(c >> 8)
buf.append(c & 0xff)
print "tx buf with crc:",
print buf

lora.regIrqFlags.octet = lora.irqFlags
print "tx start... ",
lora.tx(buf)
while not lora.regIrqFlags.bits.TxDone:
    time.sleep(0.05)
print "tx done"

# rx started in dio0_callback at TxDone
while not lora.regIrqFlags.bits.RxDone:
    time.sleep(0.05)

print "rx done"
time.sleep(0.2)
