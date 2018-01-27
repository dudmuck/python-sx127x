
    
# LoRa physical layer python example
This is for hobbyists or students who wish to create simple point-to-point link using LoRa physical layer.  
This is not LoRaWAN.
LoRaWAN is a MAC layer (and network infrastructure) which runs on top of LoRa physical layer.

This driver operates SX1272 or SX1276.  The chip type is detected on startup, meaning this driver works with both devices.
This driver requires [py-spidev](https://github.com/doceme/py-spidev), because LoRa radio chip operates over SPI.
GPIO pin access is required for `DIO0` pin and antenna switch pin (if RF switch isn't already controlled by radio chip).  `DIO0` pin from radio chip indicates when TX is complete or RX packet received.  GPIO pin's are operated completly from user application, to allow python driver to operate on any platform which py-spidev works.  In the case of raspberry pi, examples are provided using [RPi.GPIO](https://sourceforge.net/p/raspberry-gpio-python/wiki/BasicUsage/).
## Installation, RPi example:
[Enable SPI on RPi](https://www.raspberrypi-spy.co.uk/2014/08/enabling-the-spi-interface-on-the-raspberry-pi/)
### py-spidev installation
`sudo apt-get update`
`sudo apt-get install python-dev`

`git clone https://github.com/doceme/py-spidev`
`cd py-spidev`
`sudo python setup.py install`
## RPi pin connections to LoRa radio
|     | Pin#   | Pin#  | |
|----:|:------:|:-----:|:---- |
| +3.3v | 1 | 2 | +5v do not use|
|  | 3 | 4 | +5v do not use  |
|  | 5 | 6 | gnd
|  | 7 | 8 |
| gnd |9|10|
| |11|12|
| |13|14| gnd
| |15|16|
| +3.3v |17|18| (`dio0` in example)
| `MOSI` |19|20| gnd
| `MISO` |21|22| (`ant SW` in example)
| `SCLK` |23|24| `NSS-0` |
| |25|26| `NSS-1` |
| |27|28| |
| |29|30| gnd |
| |31|32| |
| |33|34| gnd|
| |35|36| |
| |37|38| |
| gnd |39|40| |

[Dragino board](http://wiki.dragino.com/index.php?title=Lora/GPS_HAT) connects SPI-NSS to pin 22, requiring software controlof SPI chip select (example not provided). If you want spidev control of NSS, connect pin 24 to LORA-NSS. Dragino uses pin 7 for `DIO0`.  Hope RF doesnt require antenna switch control from CPU, this is done on Hope RF board.

This code was tested with [SX1276 Shield](https://os.mbed.com/components/SX1276MB1xAS/).
.
Fixed RPi pins: MOSI, MISO SCLK, NSS.
Variable pins: `DIO0`, antenna switch
LORA-RESET pin should be left floating for normal operation.
On some boards, antenna switch could be driven by radio chip.  On others it could be driven by CPU pin.  Other boards might have antenna switch requiring more than one pin to control.

Pay close attention to schematic of your LoRa RF board for selection of RFO or PABOOST pin for transmit operation. `PaSelect` must be configured to match RF connection on your board (`PaSelect = 1` for PABOOST).  PABOOST can offer up to 100mW of transmit power, or RFO can provide 20mW at lower current consumption.
If antenna switch is not correctly controlled, approximately 25dB signal loss will result.  If `PaSelect` is not configured correctly, RF output can be practically non-existant.
## Example Programs
Configuration is done by accessing properties. `tx_dBm` is for accessing transmit power.  If your board is using PA_BOOST for TX, you can set to 20dBm. Receive mode is started by calling `rxCont()`, transmit is started by calling `tx(<python list>)`
### test.py
Program demonstrating LoRa physical layer transmission and reception.  Simple text command interface is provided for testing: '?' to see list of commands.
### crc.py
Using [PyCRC](https://pypi.python.org/pypi/PyCRC) for LoRa message integrity check.
## regulatory compliance
Sub-GHz rules vary of country to country for unlicensed bands.  In USA, FCC rules permit operating on 902 to 928MHz band.  LoRa complies with DSSS rules when when operating at 500KHz bandwidth configuration, with up to +20dBm TX power from within 902 to 928MHz, while staying on the same radio channel.  Alternately using a lower bandwidth LoRa signal (125Khz/250KHz/etc) requires limiting TX duration to 400ms while randomly selecting a different frequency after that 400ms (FHSS rule).
In other countries, the unlicensed RF channels can be different, in some cases requiring listen-before-transmit, or duty cycling limiting.

(edited using https://dillinger.io/)
