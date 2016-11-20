#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging as log
from neopixel import *
import time
import colorsys
from decimal import Decimal as dec

ANI_NONE = 'none'
ANI_COLOR_WIPE = 'color_wipe'
ANI_RAINBOW_CYCLE = 'rainbow_cycle'


def _wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)


def _hsv2rgb(h, s, v):
    val = tuple(int(x) for x in colorsys.hsv_to_rgb(float(h), float(s), float(v)))
    log.debug('hsv: ({},{},{}), rgb: {}'.format(
        h, s, v, val
    ))
    return val


def _rgb2hsv(r, g, b):
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return h * 360, s * 100, v * 100


class MyColor:

    @property
    def red(self):
        return self._red

    @property
    def green(self):
        return self._green

    @property
    def blue(self):
        return self._blue

    @property
    def rgb(self):
        return self.red, self.green, self.blue

    @property
    def hue_360(self):
        return self._hue_360

    @property
    def saturation_percent(self):
        return self._saturation_percent

    @property
    def brightness(self):
        return self._brightness

    def __init__(self, red=None, green=None, blue=None,
                 color24=None,
                 hue_360=None, saturation_percent=None, brightness_percent=100):
        if red is None and green is None and blue is None and color24 is None:
            log.debug('hue_360={}'.format(hue_360))
            self._red, self._green, self._blue = _hsv2rgb(hue_360 / 360,
                                                          saturation_percent * dec(0.01),
                                                          int(brightness_percent * dec(2.55)))
            self._hue_360 = hue_360
            self._saturation_percent = saturation_percent
            self._brightness_percent = brightness_percent
            self._color24 = Color(self._red, self._green, self._blue)
        elif color24 is not None:
            # (white << 24) | (red << 16) | (green << 8) | blue
            self._color24 = color24
            self._red = ((255 << 16) & color24) >> 16
            self._green = ((255 << 8) & color24) >> 8
            self._blue = (255 & color24)
            self._hue_360, self._saturation_percent, self._brightness_percent = _rgb2hsv(self._red, self._green, self._blue)
        else:
            self._red = red
            self._green = green
            self._blue = blue
            self._hue_360, self._saturation_percent, self._brightness_percent = _rgb2hsv(red, green, blue)
            self._color24 = Color(red=red, green=green, blue=blue)

        self._brightness = int(brightness_percent * dec(2.55))


class MyStrip(Adafruit_NeoPixel):

    @property
    def animation(self):
        return self._animation

    @animation.setter
    def animation(self, value):
        self._animation = value

    @property
    def is_on(self):
        return self._brightness > 0

    @property
    def last_brigthness(self):
        return self._last_brightness

    @property
    def brightness(self):
        return self._brightness

    @property
    def strip_color(self):
        return self._current_color

    @property
    def hue_360(self):
        return self._hue_360

    @property
    def saturation(self):
        return self._saturation

    @saturation.setter
    def saturation(self, value):
        self._saturation = value

    def __init__(self, num=109, pin=18, freq_hz=800000, dma=5, invert=False,
                 brightness=255, channel=0, strip_type=ws.WS2811_STRIP_RGB):
        super(MyStrip, self).__init__(num, pin, freq_hz, dma, invert,
                                      brightness, channel, strip_type)
        self._last_brightness = 125
        self._brightness = brightness
        self._animation = ANI_NONE
        self._saturation = 0.0
        self._hue_360 = 0
        self._current_color = MyColor(color24=0)

    def setBrightness(self, brightness):
        if self._brightness > 0:
            self._last_brightness = self._brightness
        self._brightness = brightness
        super(MyStrip, self).setBrightness(brightness=self._brightness)

    def setBrightnessSmooth(self, target_brightness, pause_sec=0.01):
        counter = 0   # to prevent permanent loop
        last_brightness = self._last_brightness if self._brightness == 0 else self._last_brightness
        tmp_brightness = self._brightness

        while tmp_brightness != target_brightness and counter <= 100:
            if tmp_brightness > target_brightness:
                tmp_brightness -= 1
            else:
                tmp_brightness += 1
            super(MyStrip, self).setBrightness(brightness=tmp_brightness)
            self.show()
            time.sleep(pause_sec)
            counter += 1

        self._brightness = tmp_brightness
        self._last_brightness = last_brightness

    def restore_brightness(self):
        self.setBrightness(self.last_brigthness)

    def setPixelColorRGB(self, n, red=0, green=0, blue=0, white=0):
        super(MyStrip, self).setPixelColorRGB(n=n, green=red, red=green, blue=blue, white=white)

    def set_strip_mycolor(self, my_color):
        for pixel in range(self.numPixels()):
            self.setPixelColorRGB(pixel, my_color.red, my_color.green, my_color.blue)
        self._update_self_color()

    def set_strip_color_rgb(self, red, green, blue):
        for pixel in range(self.numPixels()):
            self.setPixelColorRGB(pixel, red, green, blue)
        self._update_self_color()

    def set_strip_hls_hue(self, hue_360, saturation_percent=None, value_percent=None):
        if saturation_percent is not None:
            self.saturation = saturation_percent

        if value_percent is not None:
            self.setBrightness(int(value_percent * dec(2.55)))
        else:
            value_percent = 100

        self._hue_360 = hue_360
        new_color = MyColor(hue_360=self.hue_360,
                            saturation_percent=self.saturation,
                            brightness_percent=value_percent)
        log.debug('new_color: {} {} {}'.format(new_color.red, new_color.green, new_color.blue))
        self.set_strip_mycolor(new_color)

    def _update_self_color(self):
        self._current_color = MyColor(color24=self.getPixelColor(1))

    def start_animation(self):
        pass

    def rainbow(self, wait_ms=20, iterations=1):
        """Draw rainbow that fades across all pixels at once."""
        for j in range(256 * iterations):
            for i in range(self.numPixels()):
                self.setPixelColor(i, _wheel((i + j) & 255))
            self.show()
            time.sleep(wait_ms / 1000.0)

    def rainbow_cycle(self, wait_ms=20, iterations=5):
        """Draw rainbow that uniformly distributes itself across all pixels."""
        for j in range(256 * iterations):
            for i in range(self.numPixels()):
                self.setPixelColor(i, _wheel(((i * 256 // self.numPixels()) + j) & 255))
            self.show()
            time.sleep(wait_ms / 1000.0)

    def theater_chase_rainbow(self, wait_ms=50):
        """Rainbow movie theater light style chaser animation."""
        for j in range(256):
            for q in range(3):
                for i in range(0, self.numPixels(), 3):
                    self.setPixelColor(i + q, _wheel((i + j) % 255))
                self.show()
                time.sleep(wait_ms / 1000.0)
                for i in range(0, self.numPixels(), 3):
                    self.setPixelColor(i + q, 0)
