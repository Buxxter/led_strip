#!/usr/bin/python3
# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt


class MyMqttClient:

    @property
    def host(self):
        return self._host

    def __init__(self, host='localhost', client_id='python_hub'):
        self._client = mqtt.Client(client_id=client_id)
        self._host = host
        self._listen = False

    def connect(self):
        self._client.connect(host=self.host)
        self._client.on_connect = self.on_connect
        self._client.on_message = self.on_message

    def on_connect(self):
        pass

    def on_message(self):
        pass
