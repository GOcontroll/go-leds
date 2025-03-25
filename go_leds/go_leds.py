#!/usr/bin/env python3
from abc import ABC,abstractmethod
import os
import smbus2

I2CADDR = 0x14
RED=1
GREEN=2
BLUE=3

class CaseLed(ABC):
    """
    Represents one case led
    """

    @abstractmethod
    def set_led_red(self, brightness):
        pass

    @abstractmethod
    def set_led_green(self, brightness):
        pass

    @abstractmethod
    def set_led_blue(self, brightness):
        pass

    @abstractmethod
    def set_led_brightness(self, brightness):
        pass

class CaseLedI2c(CaseLed):

    lednum = 0
    bus=0
    red = 0
    green = 0
    blue = 0
    brightness = 0

    def __init__(self, lednum:int):
        self.lednum = lednum -1
        self.bus = smbus2.SMBus(2)
        if not self.bus.read_byte_data(I2CADDR,0) is 0x40:
            self.bus.write_byte_data(I2CADDR, 0x17, 0xff)
            self.bus.write_byte_data(I2CADDR, 0x0, 0x40)
        else:
            self.red = self.bus.read_byte(I2CADDR,0x0a+lednum*3+RED)
            self.green = self.bus.read_byte(I2CADDR,0x0a+lednum*3+GREEN)
            self.blue = self.bus.read_byte(I2CADDR,0x0a+lednum*3+BLUE)
            self.brightness=255

    def set_led_red(self, brightness:int):
        self.red = brightness
        brightness = int((self.brightness/255) * brightness)
        self.bus.write_i2c_block_data(I2CADDR,0x0a+self.lednum*3+RED,[brightness])

    def set_led_green(self, brightness:int):
        self.green = brightness
        brightness = int((self.brightness/255) * brightness)
        self.bus.write_i2c_block_data(I2CADDR,0x0a+self.lednum*3+GREEN,[brightness])

    def set_led_blue(self, brightness:int):
        self.blue = brightness
        brightness = int((self.brightness/255) * brightness)
        self.bus.write_i2c_block_data(I2CADDR,0x0a+self.lednum*3+BLUE,[brightness])

    def set_led_brightness(self, brightness):
        self.brightness = brightness
        brightness = int((self.brightness/255) * self.red)
        self.bus.write_i2c_block_data(I2CADDR,0x0a+self.lednum*3+RED,[brightness])
        brightness = int((self.brightness/255) * self.green)
        self.bus.write_i2c_block_data(I2CADDR,0x0a+self.lednum*3+GREEN,[brightness])
        brightness = int((self.brightness/255) * self.blue)
        self.bus.write_i2c_block_data(I2CADDR,0x0a+self.lednum*3+BLUE,[brightness])

class CaseLedSysfs(CaseLed):

    lednum=0
    red = 0
    green = 0
    blue = 0
    brightness = 0

    def __init__(self, lednum:int):
        self.lednum = lednum
        with open(f"/sys/class/leds/case-led{self.lednum}/brightness", "r") as brtfile:
            self.brightness = int(brtfile.read())
        with open(f"/sys/class/leds/case-led{self.lednum}/multi_intensity", "r") as multifile:
            multilist = multifile.read().split(" ")
            self.red = int(multilist[0])
            self.green = int(multilist[1])
            self.blue = int(multilist[2])

    def set_led_colour(self):
        with open(f"/sys/class/leds/case-led{self.lednum}/multi_intensity", "w") as multifile:
            multifile.write(f"{self.red} {self.green} {self.blue}")

    def set_led_red(self, brightness:int):
        self.red = brightness
        self.set_led_colour()

    def set_led_green(self, brightness:int):
        self.green = brightness
        self.set_led_colour()

    def set_led_blue(self, brightness:int):
        self.blue = brightness
        self.set_led_colour()

    def set_led_brightness(self, brightness:int):
        self.brightness = brightness
        with open(f"/sys/class/leds/case-led{self.lednum}/brightness", "w") as brtfile:
            brtfile.write(f"{brightness}")

def get_led(lednum):
    if os.path.isfile(f"/sys/class/leds/case-led{lednum}/brightness"):
        return CaseLedSysfs(lednum)
    else:
        return CaseLedI2c(lednum)

def reset_i2c_leds():
    bus = smbus2.SMBus(2)
    bus.write_i2c_block_data(I2CADDR, 0x17, [0xff])
    bus.write_i2c_block_data(I2CADDR, 0x0, [0x40])

def set_led():
    from argparse import ArgumentParser

    parser = ArgumentParser(
        prog="go-leds",
        description=f"""go-leds\n
        Control the case leds from the command line""",
        add_help=True,
    )
    parser.add_argument(
        "lednum",
#        required=True,
        type=int,
        help="The number (1-4) of the led to controll",)
    parser.add_argument(
        "function",
#        required=True,
        type=str,
        help="The function to control, <brightness/red/green/blue>",
    )
    parser.add_argument(
        "value",
#        required=True,
        type=int,
        help="The value to right to led/function",
    )

    args = parser.parse_args()

    if args.lednum < 1 or args.lednum > 4:
        print("Invalid led number")
        exit(-1)
    if args.function not in ["brightness", "red", "green", "blue"]:
        print("Invalid function")
        exit(-1)
    if args.value < 0 or args.value > 255:
        print("Invalid value")
        exit(-1)

    led = get_led(args.lednum)

    if args.function == "brightness":
        led.set_led_brightness(args.value)
    elif args.function == "red":
        led.set_led_red(args.value)
    elif args.function == "green":
        led.set_led_green(args.value)
    elif args.function == "blue":
        led.set_led_blue(args.value)
    else:
        print("Invalid function")
        exit(-1)
    exit(0)

def test_leds():
    import time
    led1 = get_led(1)
    led2 = get_led(2)
    led3 = get_led(3)
    led4 = get_led(4)

    led1.set_led_brightness(127)
    led2.set_led_brightness(127)
    led3.set_led_brightness(127)
    led4.set_led_brightness(127)

    led1.set_led_red(255)
    led2.set_led_red(255)
    led3.set_led_red(255)
    led4.set_led_red(255)

    time.sleep(2)

    led1.set_led_red(0)
    led2.set_led_red(0)
    led3.set_led_red(0)
    led4.set_led_red(0)

    led1.set_led_green(255)
    led2.set_led_green(255)
    led3.set_led_green(255)
    led4.set_led_green(255)

    time.sleep(2)

    led1.set_led_green(0)
    led2.set_led_green(0)
    led3.set_led_green(0)
    led4.set_led_green(0)

    led1.set_led_blue(255)
    led2.set_led_blue(255)
    led3.set_led_blue(255)
    led4.set_led_blue(255)

    time.sleep(2)

    led1.set_led_blue(0)
    led2.set_led_blue(0)
    led3.set_led_blue(0)
    led4.set_led_blue(0)

    led1.set_led_brightness(0)
    led2.set_led_brightness(0)
    led3.set_led_brightness(0)
    led4.set_led_brightness(0)
