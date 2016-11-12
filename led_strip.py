#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import time

import paho.mqtt.client

from utils.log import logger_init
from utils.MyStrip import MyStrip

logger = logging.getLogger(__name__)
logger_init(logger, __name__)
logger.setLevel(logging.DEBUG)

TOPIC_STRIP = '/devices/room/rgb_strip/'
TOPIC_HUE = 'hue'
TOPIC_ANIMATION = 'animation'
TOPIC_BRIGHTNESS = 'brightness'
TOPIC_LED = 'led'


def on_message(client, userdata, msg):
    logger.info('{}: {}'.format(msg.topic, msg.payload))
    c_topic = str(msg.topic).replace(TOPIC_STRIP, '').strip('/')
    message = msg.payload.decode('utf-8')
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


def do_main():
    logger.debug('tmp')
    strip.begin()
    mqttc.connect('localhost')
    mqttc.loop_start()

    while True:
        time.sleep(10)

strip = MyStrip()


mqttc = paho.mqtt.client.Client(client_id='strip_hub')
mqttc.on_message = on_message
mqttc.on_connect = on_connect

if __name__ == '__main__':
    import argparse
    import sys
    from utils.daemon import Daemon

    parser = argparse.ArgumentParser(add_help=True,
                                     usage='pidfile'
                                     )
    parser.add_argument('mode', type=str, choices=['start', 'stop', 'restart', 'status', 'force-restart'])
    parser.add_argument('-p', '--pid_file', type=str, default='/var/run/led_strip.pid', help='pid file path')
    args = parser.parse_args()
    # print(args)
    # print('pid={}'.format(args.pid_file))
    # print(args.mode)

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