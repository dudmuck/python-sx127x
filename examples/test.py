#!/usr/bin/python
import sx127x
import time
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
lora = sx127x.sx127x_lora(radio)

print ("gpiover:%s, opmode:%x" % (GPIO.VERSION, radio.OpMode))
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
        lora.rxCont()
    elif lora.regIrqFlags.bits.RxDone:
        print ("rssi:%.2fdBm snr:%.2fdB " % (lora.PktRssi, lora.PktSnr)),
        rxPayload = lora.readFifo()
        print rxPayload
    else:
        print "unhandled irq %02x" % lora.regIrqFlags.octet
    lora.irqFlags = 0xff   # clear all interrupt flags


GPIO.add_event_detect(PIN_DIO0, GPIO.RISING, callback=dio0_callback, bouncetime=1)

radio.MHz = 902.9
print ("%.3fMHz" % radio.MHz)

#radio.PaSelect = 0    # check schematic of your board, is RFO or PABOOST connected?
radio.PaSelect = 1    # check schematic of your board, is RFO or PABOOST connected?
print ("PaSelect:%u" % radio.PaSelect)
lora.SpreadingFactor = 8
print ("SpreadingFactor:%u" % lora.SpreadingFactor)
print ("tx_dBm:%d" % radio.tx_dBm)


lora.tx([1, 2, 3, 4, 55, 66, 77, 0xaa])

def print_status():
    lora.regIrqFlags.octet = lora.irqFlags
    print ("irqFlags:%02x" % lora.regIrqFlags.octet)
    print ("dio0: %u" % GPIO.input(PIN_DIO0))
    print ("PaSelect:%u " % radio.PaSelect),
    print ("%.3fMHz " % radio.MHz),
    print ("tx_dBm:%d " % radio.tx_dBm),
    print ("opmode:%u" % radio.OpMode)
    if radio.OpMode == sx127x.RF_OPMODE_RX_CONT or radio.OpMode == sx127x.RF_OPMODE_RX_SINGLE:
        print ("rssi:%.2fdBm " % lora.CurrentRssi)
    print ("sf%u  bw%u symbolPeriod:%.3fms LowDataRateOptimize:%u" % (lora.SpreadingFactor, lora.bandwidth, lora.symbolPeriodMs, lora.LowDataRateOptimize))

while True:
    # or GPIO.wait_for_edge(PIN_DIO0, GPIO.RISING)
    buf = raw_input("> ")
    print buf[0:1]
    if buf == ".":
        print_status()
    elif buf[0:1] == "?":
        print ".    print status"
        print "sf<7-12>    set spreading factor"
        print "bw<KHz>    set bandwidth"
        print "tx <payload>    transmit string"
        print "stby    standby mode"
        print "rx    start rx mode"
        print "irx    toggle invert rx"
        print "itx    toggle invert tx"
    elif buf[0:2] == "sf":
        if len(buf) > 2:
            lora.SpreadingFactor = int(buf[2:])
        print ("lora.SpreadingFactor %u" % lora.SpreadingFactor)
    elif buf[0:2] == "bw":
        if len(buf) > 2:
            lora.bandwidth = int(buf[2:])
        print ("lora.bandwidth %u" % lora.bandwidth)
    elif buf[0:3] == "tx ":
        ascii = [ord(ch) for ch in buf[buf.index(' ')+1:]]
        lora.tx(ascii)
    elif buf == "stby":
        radio.OpMode = sx127x.RF_OPMODE_STANDBY
        print ("opmode:%u" % radio.OpMode)
    elif buf[0:2] == "op":
        if len(buf) > 2:
            radio.tx_dBm = int(buf[2:])
        print ("tx_dBm:%d" % radio.tx_dBm)
    elif buf == "rx":
        lora.rxCont()
        print ("opmode:%u" % radio.OpMode)
    elif buf == "irx":
        lora.invert_rx = not lora.invert_rx
        print ("lora.invert_rx %u" % lora.invert_rx)
    elif buf == "itx":
        lora.invert_tx = not lora.invert_tx
        print ("lora.invert_tx %u" % lora.invert_tx)

