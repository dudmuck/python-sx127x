#!/usr/bin/python
import sx127x
import RPi.GPIO as GPIO

PIN_ANT_SW = 22
PIN_DIO0   = 18

def ant_switch(OpMode):
    if OpMode == sx127x.RF_OPMODE_TRANSMIT:
        GPIO.output(PIN_ANT_SW, GPIO.HIGH)
    else:
        GPIO.output(PIN_ANT_SW, GPIO.LOW)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(PIN_DIO0, GPIO.IN) # dio0 input
GPIO.setup(PIN_ANT_SW, GPIO.OUT) # antenna switch output

radio = sx127x.sx127x(ant_switch)
fsk = sx127x.sx127x_fsk(radio)

radio.MHz = 902.9
print ("%.3fMHz" % radio.MHz)

radio.PaSelect = 0    # check schematic of your board, is RFO or PABOOST connected?
print ("PaSelect:%u" % radio.PaSelect)

if radio.LongRangeMode: # to FSK
    radio.LongRangeMode = 0

print ("LongRangeMode %u" % radio.LongRangeMode)
print ("tx fdev:%uHz " % fsk.txFDevHz)
fsk.txFDevHz = 50000    # TX frequency deviation to 50KHz
print ("tx fdev:%uHz " % fsk.txFDevHz)
print ("rx bw:%uHz " % fsk.rxBwHz)
fsk.rxBwHz = 62500
print ("LongRangeMode %u" % radio.LongRangeMode)
print ("rx bw:%uHz " % fsk.rxBwHz)
print ("datarate_bps %u" % fsk.datarate_bps)
fsk.datarate_bps = 25000
print ("datarate_bps %u" % fsk.datarate_bps)
print ("DataModePacket %u" % fsk.DataModePacket)


