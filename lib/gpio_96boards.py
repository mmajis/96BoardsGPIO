import os
import ctypes


class GPIO(object):
    DIRECTIONS = ('in', 'out')
    HIGH = 1
    LOW = 0

    try:
        _lib = ctypes.CDLL('lib96BoardsGPIO.so')
    except OSError:
        # Library isn't in LD_LIBRARY_PATH, try based on relative location
        here = os.path.join(os.path.dirname(__file__))
        _lib = ctypes.CDLL(os.path.join(here, '../../lib96BoardsGPIO.so'))

    def __init__(self, pins):
        for pin in pins:
            if type(pin[0]) != int:
                raise ValueError('Pin number must be an integer')
            if pin[1] not in GPIO.DIRECTIONS:
                raise ValueError('Invalid direction for pin(%d): %s' % pin)
        self.pins = pins
        self.in_ctx = False

    def __enter__(self):
        for pin, direction in self.pins:
            if GPIO._lib.gpio_open(pin, direction):
                raise RuntimeError(
                    'Unable to set direction for pin(%d) to: %s' % (
                        pin, direction))
            self.in_ctx = True
        return self

    def __exit__(self, type, value, traceback):
        self.in_ctx = False

    @staticmethod
    def gpio_id(pin_name):
        #print "Trying to get pin %s" % pin_name
        converted_gpio = GPIO._lib.gpio_id(pin_name)
        #print "Got gpio %s" % translated_gpio
        if converted_gpio == -1:
            raise RuntimeError('Unknown pin %s' % pin_name)
        return converted_gpio

    def digital_read(self, pin):
        assert type(pin) == int
        if not self.in_ctx:
            raise RuntimeError('Method must be called inside context manager')
        return GPIO._lib.digitalRead(pin)

    def digital_write(self, pin, val):
        assert type(pin) == int and type(val) == int
        if not self.in_ctx:
            raise RuntimeError('Method must be called inside context manager')
        return GPIO._lib.digitalWrite(pin, val)
