#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@ Author      : Troy Kelly
@ Date        : 23 Sept 2018
@ Description : Philips Dynalite Library - Unofficial interface for Philips Dynalite over RS485

@ Notes:        Requires a RS485 to IP gateway (Do not use the Dynalite one - use something cheaper)
"""

import asyncio
import logging
import json


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
        if eventType not in self._monitoredEvents:
            self._monitoredEvents.append(eventType.upper())

    def unmonitorEvent(self, eventType=None):
        if eventType is None:
            raise BroadcasterError("Must supply an event type to un-monitor")
        if eventType in self._monitoredEvents:
            self._monitoredEvents.remove(eventType.upper())

    def update(self, event=None):
        if event is None:
            return
        if event.eventType not in self._monitoredEvents and '*' not in self._monitoredEvents:
            return
        if self._loop:
            self._loop.create_task(self._callUpdater(event=event))
        else:
            self._listenerFunction(event)

    @asyncio.coroutine
    def _callUpdater(self, event=None):
        self._listenerFunction(event)


class DynalitePreset(object):

    def __init__(self, name=None, value=None, fade=2, logger=None, broadcastFunction=None):
        if not value:
            raise PresetError("A preset must have a value")
        self._logger = logger
        self.active = False
        self.name = name if name else "Preset " + str(value)
        self.value = value
        self.fade = fade


class DynaliteArea(object):

    def __init__(self, name=None, value=None, fade=2, areaPresets=None, defaultPresets=None, logger=None, broadcastFunction=None):
        if not value:
            raise PresetError("An area must have a value")
        self._logger = logger
        self.name = name if name else "Area " + str(value)
        self.value = value
        self.fade = fade
        self.preset = {}
        if areaPresets:
            for presetValue in areaPresets:
                preset = areaPresets[presetValue]
                presetName = preset['name'] if 'name' in preset else None
                presetFade = preset['fade'] if 'fade' in preset else fade
                self._logger.debug("Area '%s' - Creating '%d/%s' (Fade %d)" %
                                   (self.name, int(presetValue), presetName, presetFade))
                self.preset[int(presetValue)] = DynalitePreset(
                    name=presetName, value=presetValue, fade=presetFade, logger=self._logger, broadcastFunction=broadcastFunction)
                if broadcastFunction:
                    broadcastData = {
                        'area': self.value,
                        'preset': presetValue,
                        'name': self.name + ' ' + presetName,
                        'state': 'OFF'
                    }
                    broadcastFunction(
                        Event(eventType='newpreset', data=broadcastData))
        if defaultPresets:
            for presetValue in defaultPresets:
                if int(presetValue) not in self.preset:
                    preset = defaultPresets[presetValue]
                    presetName = preset['name'] if preset['name'] else None
                    presetFade = preset['fade'] if preset['fade'] else fade
                    self._logger.debug("Area '%s' - Creating '%d/%s' (Fade %d)" %
                                       (self.name, int(presetValue), presetName, presetFade))
                    self.preset[int(presetValue)] = DynalitePreset(
                        name=presetName, value=presetValue, fade=presetFade, logger=self._logger, broadcastFunction=broadcastFunction)
                    if broadcastFunction:
                        broadcastData = {
                            'area': self.value,
                            'preset': presetValue,
                            'name': self.name + ' ' + presetName,
                            'state': 'OFF'
                        }
                        broadcastFunction(
                            Event(eventType='newpreset', data=broadcastData))


class Dynalite(object):

    def __init__(self, config=None, loop=None, logger=None):
        self.loop = loop if loop else asyncio.get_event_loop()
        self._logger = logger if logger else logging.getLogger(__name__)
        self._config = DynaliteConfig(config=config)
        logging.basicConfig(level=self._config.log_level,
                            format=self._config.log_formatter)

        self._listeners = []

        self._devices = {
            'area': {}
        }

    def start(self):
        self.loop.create_task(self._start())

    def broadcast(self, event):
        self.loop.create_task(self._broadcast(event))

    @asyncio.coroutine
    def _broadcast(self, event):
        for listenerFunction in self._listeners:
            listenerFunction.update(event)

    @asyncio.coroutine
    def _start(self):
        for areaValue in self._config.area:
            areaName = self._config.area[areaValue]['name'] if 'name' in self._config.area[areaValue] else None
            areaPresets = self._config.area[areaValue]['preset'] if 'preset' in self._config.area[areaValue] else {
            }
            areaFade = self._config.area[areaValue]['fade'] if 'fade' in self._config.area[areaValue] else None
            if areaFade is None:
                areaFade = self._config.default['fade'] if 'fade' in self._config.default else 2
            if 'nodefault' in self._config.area[areaValue] and self._config.area[areaValue]['nodefault'] == True:
                defaultPresets = None
            else:
                defaultPresets = self._config.preset

            self._logger.debug(
                "Generating Area '%d/%s' with a default fade of %d" % (int(areaValue), areaName, areaFade))
            self._devices['area'][int(areaValue)] = DynaliteArea(
                name=areaName, value=areaValue, fade=areaFade, areaPresets=areaPresets, defaultPresets=defaultPresets, logger=self._logger, broadcastFunction=self.broadcast)

    def addListener(self, listenerFunction=None):
        broadcaster = Broadcaster(
            listenerFunction=listenerFunction, loop=self.loop)
        self._listeners.append(broadcaster)
        return broadcaster
