#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import logging.config
import logging.handlers
import time
import paho.mqtt.client

import utils.MyStrip as mystrip
from decimal import Decimal as dec
from decimal import DecimalException

logging.config.fileConfig('log.conf')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.propagate = False

TOPIC_STRIP = '/devices/room/rgb_strip/'
TOPIC_HUE = 'hue'
TOPIC_ANIMATION = 'animation'
TOPIC_BRIGHTNESS = 'brightness'
TOPIC_LED = 'led'

TOPIC_HSV = 'hsv'
TOPIC_SET = 'set'
TOPIC_GET = TOPIC_HSV + '/get'
TOPIC_STATUS = 'status'
TOPIC_SATURATION = 'saturation'
TOPIC_IDENTIFY = 'identify'

TOPIC_FULL_STATUS = TOPIC_STRIP + TOPIC_HSV + '/' + TOPIC_STATUS
TOPIC_FULL_SET = TOPIC_STRIP + TOPIC_HSV + '/' + TOPIC_SET


class LedStrip(object):

    def __init__(self):
        super(LedStrip, self).__init__()

        self._strip = mystrip.MyStrip(brightness=0)
        self._strip.begin()

        self._mqttc = paho.mqtt.client.Client(client_id='strip_hub')
        self._mqttc.on_message = lambda client, userdata, msg: self.on_message(client, userdata, msg)
        self._mqttc.on_connect = lambda client, userdata, rc: self.on_connect(client, userdata, rc)

    def on_message(self, client, userdata, msg):
        logger.info('{}: {}'.format(msg.topic, msg.payload))
        c_topic = str(msg.topic).replace(TOPIC_STRIP, '').strip('/').lower()
        message = msg.payload.decode('utf-8')
        if c_topic.startswith(TOPIC_HSV):
            if c_topic == TOPIC_GET:
                self.publish_status(message.lower())
                return

            try:
                val = dec(message)
                logger.debug('hsb val = {}'.format(val))
            except DecimalException as ex:
                logger.warning(ex)
                return
            # /hsb
            c_topic = c_topic.replace(TOPIC_HSV, '', 1).strip('/')
            if c_topic.startswith(TOPIC_SET):
                # /set
                c_topic = c_topic.replace(TOPIC_SET, '').strip('/')
                if '' == c_topic:
                    # setOn
                    if 1 == val:
                        if not self._strip.is_on:
                            self._strip.restore_brightness()
                            self._strip.show()
                    else:
                        if self._strip.is_on:
                            self._strip.setBrightness(0)
                            self._strip.show()
                elif c_topic.startswith(TOPIC_HUE):
                    # /hue
                    logger.debug('set_strip_hls_hue({}, {})'.format(val, self._strip.saturation))
                    self._strip.set_strip_hls_hue(hue_360=val, saturation_percent=self._strip.saturation)
                    self._strip.show()
                elif c_topic.startswith(TOPIC_BRIGHTNESS):
                    # /brightness
                    self._strip.setBrightnessSmooth(int(int(val) * 2.55))
                elif c_topic.startswith(TOPIC_SATURATION):
                    # /saturation
                    self._strip.saturation = val
                elif c_topic.startswith(TOPIC_IDENTIFY):
                    led_first = 0
                    led_mid = int(self._strip.numPixels() / 2)
                    led_last = self._strip.numPixels() - 1
                    led_first_color = self._strip.getPixelColor(led_first)
                    led_mid_color = self._strip.getPixelColor(led_mid)
                    led_last_color = self._strip.getPixelColor(led_last)
                    led_brightness = self._strip.brightness
                    if led_brightness == 0:
                        self._strip.setBrightness(255)

                    self._strip.setPixelColorRGB(led_first, red=255)
                    self._strip.setPixelColorRGB(led_mid, red=255)
                    self._strip.setPixelColorRGB(led_last, red=255)
                    self._strip.show()
                    time.sleep(0.5)
                    self._strip.setPixelColorRGB(led_first, green=255)
                    self._strip.setPixelColorRGB(led_mid, green=255)
                    self._strip.setPixelColorRGB(led_last, green=255)
                    self._strip.show()
                    time.sleep(0.5)
                    self._strip.setPixelColorRGB(led_first, blue=255)
                    self._strip.setPixelColorRGB(led_mid, blue=255)
                    self._strip.setPixelColorRGB(led_last, blue=255)
                    self._strip.show()
                    time.sleep(0.5)
                    self._strip.setPixelColor(led_first, led_first_color)
                    self._strip.setPixelColor(led_mid, led_mid_color)
                    self._strip.setPixelColor(led_last, led_last_color)
                    if led_brightness == 0:
                        self._strip.setBrightness(led_brightness)
                    self._strip.show()

            elif c_topic.startswith(TOPIC_STATUS):
                # /status
                c_topic = c_topic.replace(TOPIC_STATUS, '').strip('/')
                if '' == c_topic:
                    # setOn
                    pass
                elif c_topic.startswith(TOPIC_HUE):
                    # /hue
                    pass
                elif c_topic.startswith(TOPIC_BRIGHTNESS):
                    # /brightness
                    pass
                elif c_topic.startswith(TOPIC_SATURATION):
                    # /saturation
                    pass

        else:
            if TOPIC_LED in c_topic:
                c_topic = c_topic.replace(TOPIC_LED, '').strip('/')
                logger.debug(c_topic)
                led_str, command = c_topic.split('/', 2)
                led = int(led_str)
                logger.debug('led: {}, command: {}'.format(led, command))
                if command is None:
                    pass
                elif TOPIC_HUE in command:
                    red, green, blue = [int(x) for x in str(message).split(maxsplit=4)]
                    self._strip.setPixelColorRGB(led, red=red, green=green, blue=blue)
                    self._strip.show()

            elif TOPIC_HUE in c_topic:
                red, green, blue = [int(x) for x in str(message).split(maxsplit=3)]
                self._strip.set_strip_color_rgb(red, green, blue)
                self._strip.show()
            elif TOPIC_BRIGHTNESS in c_topic:
                brightness = int(message)
                colors = self._strip.getPixels()
                self._strip.setBrightness(brightness=brightness)
                for pixel in range(self._strip.numPixels()):
                    self._strip.setPixelColor(pixel, colors[pixel])
                logger.debug('New bright')
                self._strip.show()
            elif TOPIC_ANIMATION in c_topic:
                self._strip.animation = message
                self._strip.start_animation()

    def on_connect(self, client, userdata, rc):
        logger.info('mqtt connected with status code ' + str(rc))
        self._mqttc.subscribe(topic=TOPIC_STRIP + '#')

    def publish_status(self, status=None):
        status_on = '1' if self._strip.is_on else '0'
        status_brightness = str(int(self._strip.brightness / 2.55))
        status_hue = str(self._strip.hue_360)
        status_saturation = str(self._strip.saturation)
        if status is None or status == TOPIC_STATUS:
            self._mqttc.publish(topic=TOPIC_FULL_STATUS,
                                payload=status_on)
        if status is None or status == TOPIC_BRIGHTNESS:
            self._mqttc.publish(topic=TOPIC_FULL_STATUS + '/' + TOPIC_BRIGHTNESS,
                                payload=status_brightness)
        if status is None or status == TOPIC_HUE:
            self._mqttc.publish(topic=TOPIC_FULL_STATUS + '/' + TOPIC_HUE,
                                payload=status_hue)
        if status is None or status == TOPIC_SATURATION:
            self._mqttc.publish(topic=TOPIC_FULL_STATUS + '/' + TOPIC_SATURATION,
                                payload=status_saturation)

    def run(self):
        self._mqttc.connect('localhost')
        self._mqttc.loop_start()
        while True:
            self.publish_status()
            time.sleep(5)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(add_help=True,
                                     usage='led_strip.py {-v|--verbose [debug|info|warning|none]}'
                                     )
    parser.add_argument('-v', '--verbose', type=str, choices=['debug', 'info', 'warning', 'none'], default='warning')
    args = parser.parse_args()

    if 'none' in args.verbose:
        logger.setLevel(logging.NOTSET)
    elif 'warning' in args.verbose:
        logger.setLevel(logging.WARNING)
    elif 'info' in args.verbose:
        logger.setLevel(logging.INFO)
    elif 'debug' in args.verbose:
        logger.setLevel(logging.DEBUG)

    magic = LedStrip()
    magic.run()
