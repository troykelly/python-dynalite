"""
@ Author      : Troy Kelly
@ Date        : 23 Sept 2018
@ Description : Philips Dynalite Library - Unofficial interface for Philips Dynalite over RS485

@ Notes:        Requires a RS485 to IP gateway (Do not use the Dynalite one - use something cheaper)
"""

import asyncio
import logging
import json
from .dynet import Dynet, DynetControl

class BroadcasterError(Exception):
    def __init__(self, message):
        self.message = message


class PresetError(Exception):
    def __init__(self, message):
        self.message = message


class AreaError(Exception):
    def __init__(self, message):
        self.message = message


class Event(object):

    def __init__(self, eventType=None, message=None, data={}):
        self.eventType = eventType.upper() if eventType else None
        self.msg = message
        self.data = data

    def toJson(self):
        return json.dumps(self.__dict__)


class DynaliteConfig(object):

    def __init__(self, config=None):
        self.log_level = config['log_level'].upper(
        ) if 'log_level' in config else logging.INFO
        self.log_formatter = config[
            'log_formatter'] if 'log_formatter' in config else "[%(asctime)s] %(name)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s"
        self.host = config['host'] if 'host' in config else 'localhost'
        self.port = config['port'] if 'port' in config else 12345
        self.default = config['default'] if 'default' in config else {}
        self.area = {}
        self.preset = {}
        self.area = config['area'] if 'area' in config else {}
        self.preset = config['preset'] if 'preset' in config else {}


class Broadcaster(object):

    def __init__(self, listenerFunction=None, loop=None):
        if listenerFunction is None:
            raise BroadcasterError(
                "A broadcaster bust have a listener Function")
        self._listenerFunction = listenerFunction
        self._monitoredEvents = []
        self._loop = loop

    def monitorEvent(self, eventType=None):
        if eventType is None:
            raise BroadcasterError("Must supply an event type to monitor")
        eventType = eventType.upper()
        if eventType not in self._monitoredEvents:
            self._monitoredEvents.append(eventType.upper())

    def unmonitorEvent(self, eventType=None):
        if eventType is None:
            raise BroadcasterError("Must supply an event type to un-monitor")
        eventType = eventType.upper()
        if eventType in self._monitoredEvents:
            self._monitoredEvents.remove(eventType.upper())

    def update(self, event=None, dynalite=None):
        if event is None:
            return
        if event.eventType not in self._monitoredEvents and '*' not in self._monitoredEvents:
            return
        if self._loop:
            self._loop.create_task(self._callUpdater(
                event=event, dynalite=dynalite))
        else:
            self._listenerFunction(event=event, dynalite=dynalite)

    @asyncio.coroutine
    def _callUpdater(self, event=None, dynalite=None):
        self._listenerFunction(event=event, dynalite=dynalite)


class DynalitePreset(object):

    def __init__(self, name=None, value=None, fade=2, logger=None, broadcastFunction=None, area=None, dynetControl=None):
        if not value:
            raise PresetError("A preset must have a value")
        self._logger = logger
        self.active = False
        self.name = name if name else "Preset " + str(value)
        self.value = int(value)
        self.fade = float(fade)
        self.area = area
        self.broadcastFunction = broadcastFunction
        self._control = dynetControl
        if self.broadcastFunction:
            broadcastData = {
                'area': self.area.value,
                'preset': self.value,
                'name': self.area.name + ' ' + self.name,
                'state': 'OFF'
            }
            self.broadcastFunction(
                Event(eventType='newpreset', data=broadcastData))

    def turnOn(self, sendDynet=True, sendMQTT=True):
        self.active = True
        if self.area:
            self.area.activePreset = self.value
        if sendMQTT and self.broadcastFunction:
            broadcastData = {
                'area': self.area.value,
                'preset': self.value,
                'name': self.area.name + ' ' + self.name,
                'state': 'ON'
            }
            self.broadcastFunction(
                Event(eventType='preset', data=broadcastData))
        if sendDynet and self._control:
            self._control.areaPreset(
                area=self.area.value, preset=self.value, fade=self.fade)
        for preset in self.area.preset:
            if self.value != preset:
                if self.area.preset[preset].active:
                    self.area.preset[preset].turnOff(sendDynet=False, sendMQTT=True)

    def turnOff(self, sendDynet=True, sendMQTT=True):
        self.active = False
        if sendMQTT and self.broadcastFunction:
            broadcastData = {
                'area': self.area.value,
                'preset': self.value,
                'name': self.area.name + ' ' + self.name,
                'state': 'OFF'
            }
            self.broadcastFunction(
                Event(eventType='preset', data=broadcastData))
        if sendDynet and self._control:
            self._control.areaOff(area=self.area.value, fade=self.fade)


class DynaliteArea(object):

    def __init__(self, name=None, value=None, fade=2, areaPresets=None, defaultPresets=None, logger=None, broadcastFunction=None, dynetControl=None):
        if not value:
            raise PresetError("An area must have a value")
        self._logger = logger
        self.name = name if name else "Area " + str(value)
        self.value = int(value)
        self.fade = fade
        self.preset = {}
        self.activePreset = None
        self.broadcastFunction = broadcastFunction
        self._dynetControl = dynetControl
        if areaPresets:
            for presetValue in areaPresets:
                preset = areaPresets[presetValue]
                presetName = preset['name'] if 'name' in preset else None
                presetFade = preset['fade'] if 'fade' in preset else fade
                self.preset[int(presetValue)] = DynalitePreset(
                    name=presetName, value=presetValue, fade=presetFade, logger=self._logger, broadcastFunction=self.broadcastFunction, area=self, dynetControl=self._dynetControl)
        if defaultPresets:
            for presetValue in defaultPresets:
                if int(presetValue) not in self.preset:
                    preset = defaultPresets[presetValue]
                    presetName = preset['name'] if preset['name'] else None
                    presetFade = preset['fade'] if preset['fade'] else fade
                    self.preset[int(presetValue)] = DynalitePreset(
                        name=presetName, value=presetValue, fade=presetFade, logger=self._logger, broadcastFunction=self.broadcastFunction, area=self, dynetControl=self._dynetControl)

    def presetOn(self, preset, sendDynet=True, sendMQTT=True):
        if preset not in self.preset:
            self.preset[preset] = DynalitePreset(
                value=preset, fade=self.fade, logger=self._logger, broadcastFunction=self.broadcastFunction, area=self, dynetControl=self._dynetControl)
        self.preset[preset].turnOn(sendDynet=sendDynet, sendMQTT=sendMQTT)

    def presetOff(self, preset, sendDynet=True, sendMQTT=True):
        if preset not in self.preset:
            self.preset[preset] = DynalitePreset(
                value=preset, fade=self.fade, logger=self._logger, broadcastFunction=self.broadcastFunction, area=self, dynetControl=self._dynetControl)
        self.preset[preset].turnOff(sendDynet=sendDynet, sendMQTT=sendMQTT)

class Dynalite(object):

    def __init__(self, config=None, loop=None, logger=None):
        self.loop = loop if loop else asyncio.get_event_loop()
        self._logger = logger if logger else logging.getLogger(__name__)
        self._config = DynaliteConfig(config=config)
        logging.basicConfig(level=self._config.log_level,
                            format=self._config.log_formatter)

        self._configured = False

        self._listeners = []

        self.devices = {
            'area': {}
        }

        self._dynet = None
        self.control = None

    def start(self):
        self.loop.create_task(self._start())

    def connect(self):
        self.loop.create_task(self._connect())

    def processTraffic(self, event):
        self.loop.create_task(self._processTraffic(event))

    @asyncio.coroutine
    def _processTraffic(self, event):
        self.broadcast(event)
        if event.eventType == 'PRESET':
            self.devices['area'][event.data['area']].presetOn(event.data['preset'],sendDynet=False, sendMQTT=False)

    @asyncio.coroutine
    def _connect(self):
        self._dynet = Dynet(host=self._config.host, port=self._config.port,
                            loop=self.loop, broadcaster=self.processTraffic, onConnect=self._connected, onDisconnect=self._disconnection)
        self._dynet.connect()

    @asyncio.coroutine
    def _connected(self, dynet=None, transport=None):
        self.control = DynetControl(
            dynet, self.loop, areaDefinition=self.devices['area'])
        if not self._configured:
            self.loop.create_task(self._configure())
        self.broadcast(Event(eventType='connected', data={}))

    @asyncio.coroutine
    def _disconnection(self, dynet=None):
        self.control = None
        self.broadcast(Event(eventType='disconnected', data={}))

    def broadcast(self, event):
        self.loop.create_task(self._broadcast(event))

    @asyncio.coroutine
    def _broadcast(self, event):
        for listenerFunction in self._listeners:
            listenerFunction.update(event=event, dynalite=self)

    @asyncio.coroutine
    def _start(self):
        self.connect()

    @asyncio.coroutine
    def _configure(self):
        for areaValue in self._config.area:
            areaName = self._config.area[areaValue]['name'] if 'name' in self._config.area[areaValue] else None
            areaPresets = self._config.area[areaValue]['preset'] if 'preset' in self._config.area[areaValue] else {
            }
            areaFade = self._config.area[areaValue]['fade'] if 'fade' in self._config.area[areaValue] else None
            if areaFade is None:
                areaFade = self._config.default['fade'] if 'fade' in self._config.default else 2
            areaFade = float(areaFade)
            if 'nodefault' in self._config.area[areaValue] and self._config.area[areaValue]['nodefault'] == True:
                defaultPresets = None
            else:
                defaultPresets = self._config.preset

            self._logger.debug(
                "Generating Area '%d/%s' with a default fade of %f" % (int(areaValue), areaName, areaFade))
            self.devices['area'][int(areaValue)] = DynaliteArea(
                name=areaName, value=areaValue, fade=areaFade, areaPresets=areaPresets, defaultPresets=defaultPresets, logger=self._logger, broadcastFunction=self.broadcast, dynetControl=self.control)
        self._configured = True

    def state(self):
        self.loop.create_task(self._state())

    @asyncio.coroutine
    def _state(self):
        for areaValue in self.devices['area']:
            area = self.devices['area'][areaValue]
            for presetValue in area.preset:
                preset = area.preset[presetValue]
                presetState = 'ON' if preset.active else 'OFF'
                broadcastData = {
                    'area': area.value,
                    'preset': preset.value,
                    'name': area.name + ' ' + preset.name,
                    'state': presetState
                }
                self.broadcast(
                    Event(eventType='newpreset', data=broadcastData))
                if preset.active:
                    self.broadcastFunction(
                        Event(eventType='preset', data=broadcastData))
            self.control.areaReqPreset(area.value)


    def addListener(self, listenerFunction=None):
        broadcaster = Broadcaster(
            listenerFunction=listenerFunction, loop=self.loop)
        self._listeners.append(broadcaster)
        return broadcaster
