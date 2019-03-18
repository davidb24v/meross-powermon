# -*- coding: utf-8 -*-

from threading import RLock, Condition
from hashlib import md5
import ssl
import random
import sys
import time
import string
import json

import paho.mqtt.client as mqtt
from paho.mqtt import MQTTException

from meross_iot.supported_devices.power_plugs import (Device, ClientStatus)
from meross_iot.utilities.synchronization import AtomicCounter


class ModifiedDevice(Device):

    def __init__(self,
                 token,
                 key,
                 user_id,
                 **kwords):

        self._status_lock = RLock()

        self._waiting_message_ack_queue = Condition()
        self._waiting_subscribers_queue = Condition()
        self._subscription_count = AtomicCounter(0)

        self._set_status(ClientStatus.INITIALIZED)

        self._token = token,
        self._key = key
        self._user_id = user_id
        self._uuid = kwords['uuid']
        if "domain" in kwords:
            self._domain = kwords['domain']
        else:
            self._domain = "eu-iot.meross.com"

        # Lookup port and certificate MQTT server
        self._port = kwords.get('port', 2001)
        self._ca_cert = kwords.get('ca_cert', None)

        if "channels" in kwords:
            self._channels = kwords['channels']

        # Informations about device
        if "devName" in kwords:
            self._name = kwords['devName']
        if "deviceType" in kwords:
            self._type = kwords['deviceType']
        if "fmwareVersion" in kwords:
            self._fwversion = kwords['fmwareVersion']
        if "hdwareVersion" in kwords:
            self._hwversion = kwords['hdwareVersion']

        self._generate_client_and_app_id()

        # Password is calculated as the MD5 of USERID concatenated with KEY
        md5_hash = md5()
        clearpwd = "%s%s" % (self._user_id, self._key)
        md5_hash.update(clearpwd.encode("utf8"))
        hashed_password = md5_hash.hexdigest()

        # Start the mqtt client
        # ex. app-id -> app:08d4c9f99da40203ebc798a76512ec14
        self._mqtt_client = mqtt.Client(client_id=self._client_id,
                                        protocol=mqtt.MQTTv311)
        self._mqtt_client.on_connect = self._on_connect
        self._mqtt_client.on_message = self._on_message
        self._mqtt_client.on_disconnect = self._on_disconnect
        self._mqtt_client.on_subscribe = self._on_subscribe
        self._mqtt_client.on_log = self._on_log
        # Set user_id to None to avoid login
        if self._user_id is not None:
            self._mqtt_client.username_pw_set(username=self._user_id,
                                              password=hashed_password)
        self._mqtt_client.tls_set(ca_certs=self._ca_cert, certfile=None,
                                  keyfile=None, cert_reqs=ssl.CERT_REQUIRED,
                                  tls_version=ssl.PROTOCOL_TLS,
                                  ciphers=None)

        self._mqtt_client.connect(self._domain, self._port, keepalive=30)
        self._set_status(ClientStatus.CONNECTING)

        # Starts a new thread that handles mqtt protocol and calls us back
        # via callbacks
        self._mqtt_client.loop_start()

        with self._waiting_subscribers_queue:
            self._waiting_subscribers_queue.wait()
            if self._client_status != ClientStatus.SUBSCRIBED:
                # An error has occurred
                raise Exception(self._error)


class Mss310(ModifiedDevice):
    def get_power_consumptionX(self):
        return self._execute_cmd("GET", "Appliance.Control.ConsumptionX", {})

    def get_electricity(self):
        return self._execute_cmd("GET", "Appliance.Control.Electricity", {})

    def turn_on(self):
        if self._hwversion.split(".")[0] == "2":
            payload = {'togglex': {"onoff": 1}}
            return self._execute_cmd("SET", "Appliance.Control.ToggleX",
                                     payload)
        else:
            payload = {"channel": 0, "toggle": {"onoff": 1}}
            return self._execute_cmd("SET", "Appliance.Control.Toggle",
                                     payload)

    def turn_off(self):
        if self._hwversion.split(".")[0] == "2":
            payload = {'togglex': {"onoff": 0}}
            return self._execute_cmd("SET", "Appliance.Control.ToggleX",
                                     payload)
        else:
            payload = {"channel": 0, "toggle": {"onoff": 0}}
            return self._execute_cmd("SET", "Appliance.Control.Toggle",
                                     payload)
