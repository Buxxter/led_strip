#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
from neopixel import *
import time


logger = logging.getLogger()

ANI_NONE = 'none'
ANI_COLOR_WIPE = 'color_wipe'
ANI_RAINBOW_CYCLE = 'rainbow_cycle'


def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)


class MyStrip(Adafruit_NeoPixel):

    @property
    def animation(self):
        return self._animation

    @animation.setter
    def animation(self, value):
        self._animation = value

    @property
    def last_brigthness(self):
        return self._last_brightness

    def __init__(self, num=109, pin=18, freq_hz=800000, dma=5, invert=False,
                 brightness=255, channel=0, strip_type=ws.WS2811_STRIP_RGB):
        super(MyStrip, self).__init__(num, pin, freq_hz, dma, invert,
                                      brightness, channel, strip_type)
        self._last_brightness = 0
        self._brightness = brightness
        self._animation = ANI_NONE

    def setBrightness(self, brightness):
        self._last_brightness = self._brightness
        self._brightness = brightness
        super(MyStrip, self).setBrightness(brightness=self._brightness)

    def setPixelColorRGB(self, n, red, green, blue, white=0):
        super(MyStrip, self).setPixelColorRGB(n=n, green=red, red=green, blue=blue, white=white)
    
    def set_strip_color(self, color):
        for pixel in range(self.numPixels()):
            self.setPixelColor(pixel, color)

    def set_strip_color_rgb(self, red, green, blue):
        for pixel in range(self.numPixels()):
            self.setPixelColorRGB(pixel, red, green, blue)

    def start_animation(self):
        pass

    def rainbow(self, wait_ms=20, iterations=1):
        """Draw rainbow that fades across all pixels at once."""
        for j in range(256 * iterations):
            for i in range(self.numPixels()):
                strip.setPixelColor(i, wheel((i + j) & 255))
            strip.show()
            time.sleep(wait_ms / 1000.0)

    def rainbow_cycle(self, wait_ms=20, iterations=5):
        """Draw rainbow that uniformly distributes itself across all pixels."""
        for j in range(256 * iterations):
            for i in range(self.numPixels()):
                self.setPixelColor(i, wheel(((i * 256 // self.numPixels()) + j) & 255))
            self.show()
            time.sleep(wait_ms / 1000.0)

    def theater_chase_rainbow(self, wait_ms=50):
        """Rainbow movie theater light style chaser animation."""
        for j in range(256):
            for q in range(3):
                for i in range(0, self.numPixels(), 3):
                    self.setPixelColor(i + q, wheel((i + j) % 255))
                self.show()
                time.sleep(wait_ms / 1000.0)
                for i in range(0, self.numPixels(), 3):
                    self.setPixelColor(i + q, 0)
