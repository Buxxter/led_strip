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


def on_message(client, userdata, msg):
    logger.info('{}: {}'.format(msg.topic, msg.payload))
    c_topic = str(msg.topic).replace(TOPIC_STRIP, '').strip('/').lower()
    message = msg.payload.decode('utf-8')
    if c_topic.startswith(TOPIC_HSV):
        if c_topic == TOPIC_GET:
            publish_status(message.lower())
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
                    if not strip.is_on:
                        strip.restore_brightness()
                        strip.show()
                else:
                    if strip.is_on:
                        strip.setBrightness(0)
                        strip.show()
            elif c_topic.startswith(TOPIC_HUE):
                # /hue
                logger.debug('set_strip_hls_hue({}, {})'.format(val, strip.saturation))
                strip.set_strip_hls_hue(hue_360=val, saturation_percent=strip.saturation)
                strip.show()
            elif c_topic.startswith(TOPIC_BRIGHTNESS):
                # /brightness
                strip.setBrightness(int(int(val) * 2.55))
                strip.show()
            elif c_topic.startswith(TOPIC_SATURATION):
                # /saturation
                strip.saturation = val
            elif c_topic.startswith(TOPIC_IDENTIFY):
                led_first = 0
                led_mid = int(strip.numPixels() / 2)
                led_last = strip.numPixels() - 1
                led_first_color = strip.getPixelColor(led_first)
                led_mid_color = strip.getPixelColor(led_mid)
                led_last_color = strip.getPixelColor(led_last)
                led_brightness = strip.brightness
                if led_brightness == 0:
                    strip.setBrightness(255)

                strip.setPixelColorRGB(led_first, red=255)
                strip.setPixelColorRGB(led_mid, red=255)
                strip.setPixelColorRGB(led_last, red=255)
                strip.show()
                time.sleep(0.5)
                strip.setPixelColorRGB(led_first, green=255)
                strip.setPixelColorRGB(led_mid, green=255)
                strip.setPixelColorRGB(led_last, green=255)
                strip.show()
                time.sleep(0.5)
                strip.setPixelColorRGB(led_first, blue=255)
                strip.setPixelColorRGB(led_mid, blue=255)
                strip.setPixelColorRGB(led_last, blue=255)
                strip.show()
                time.sleep(0.5)
                strip.setPixelColor(led_first, led_first_color)
                strip.setPixelColor(led_mid, led_mid_color)
                strip.setPixelColor(led_last, led_last_color)
                if led_brightness == 0:
                    strip.setBrightness(led_brightness)
                strip.show()

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
                strip.setPixelColorRGB(led, red=red, green=green, blue=blue)
                strip.show()

        elif TOPIC_HUE in c_topic:
            red, green, blue = [int(x) for x in str(message).split(maxsplit=3)]
            strip.set_strip_color_rgb(red, green, blue)
            strip.show()
        elif TOPIC_BRIGHTNESS in c_topic:
            brightness = int(message)
            colors = strip.getPixels()
            print(colors)
            strip.setBrightness(brightness=brightness)
            for pixel in range(strip.numPixels()):
                strip.setPixelColor(pixel, colors[pixel])
            logger.debug('New bright')
            strip.show()
        elif TOPIC_ANIMATION in c_topic:
            strip.animation = message
            strip.start_animation()


def on_connect(client, userdata, rc):
    logger.info('mqtt connected with status code ' + str(rc))
    mqttc.subscribe(topic=TOPIC_STRIP + '#')


def publish_status(status=None):
    status_on = '1' if strip.is_on else '0'
    status_brightness = str(int(strip.brightness / 2.55))
    status_hue = str(strip.hue_360)
    status_saturation = str(strip.saturation)
    if status is None or status == TOPIC_STATUS:
        mqttc.publish(topic=TOPIC_FULL_STATUS,
                      payload=status_on)
    if status is None or status == TOPIC_BRIGHTNESS:
        mqttc.publish(topic=TOPIC_FULL_STATUS + '/' + TOPIC_BRIGHTNESS,
                      payload=status_brightness)
    if status is None or status == TOPIC_HUE:
        mqttc.publish(topic=TOPIC_FULL_STATUS + '/' + TOPIC_HUE,
                      payload=status_hue)
    if status is None or status == TOPIC_SATURATION:
        mqttc.publish(topic=TOPIC_FULL_STATUS + '/' + TOPIC_SATURATION,
                      payload=status_saturation)


def do_main():
    mqttc.connect('localhost')
    mqttc.loop_start()
    while True:
        publish_status()
        time.sleep(5)

strip = mystrip.MyStrip(brightness=0)
strip.begin()


mqttc = paho.mqtt.client.Client(client_id='strip_hub')
mqttc.on_message = on_message
mqttc.on_connect = on_connect


if __name__ == '__main__':
    import argparse
    # import sys
    # from utils.daemon import Daemon

    parser = argparse.ArgumentParser(add_help=True,
                                     usage='pidfile'
                                     )
    parser.add_argument('mode', type=str, choices=['start', 'stop', 'restart', 'status', 'force-restart'], default='start')
    parser.add_argument('-p', '--pid_file', type=str, default='/var/run/led_strip.pid', help='pid file path')
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

    do_main()

    # daemon = Daemon(pidfile=args.pid_file, action=do_main)
    # if 'start' == args.mode:
    #     daemon.start()
    # elif 'stop' == args.mode:
    #     daemon.stop()
    # elif 'restart' == args.mode:
    #     daemon.restart()
    # elif 'state' == args.mode:
    #     print('Unknown')
    # else:
    #     print('Unknown command')
    #     sys.exit(2)
    # sys.exit(0)
