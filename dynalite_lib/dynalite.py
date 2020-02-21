"""
@ Author      : Troy Kelly
@ Date        : 3 Dec 2018
@ Description : Philips Dynalite Library - Unofficial interface for Philips Dynalite over RS485

@ Notes:        Requires a RS485 to IP gateway (Do not use the Dynalite one - use something cheaper)
"""

import asyncio
import logging
from .dynet import Dynet, DynetControl
from .event import DynetEvent

from .const import (
    CONF_HOST,
    CONF_LOGLEVEL,
    CONF_LOGFORMATTER,
    CONF_PORT,
    CONF_DEFAULT,
    CONF_AREA,
    CONF_NAME,
    CONF_FADE,
    CONF_STATE,
    CONF_STATE_ON,
    CONF_STATE_OFF,
    CONF_LEVEL,
    CONF_PRESET,
    CONF_AUTO_DISCOVER,
    CONF_POLLTIMER,
    CONF_CHANNEL,
    CONF_NODEFAULT,
    CONF_ACTION,
    CONF_ACTION_REPORT,
    CONF_ACTION_CMD,
    CONF_TRGT_LEVEL,
    CONF_ACT_LEVEL,
    CONF_ALL,
    EVENT_CONNECTED,
    EVENT_DISCONNECTED,
    EVENT_CONFIGURED,
    EVENT_NEWPRESET,
    EVENT_NEWCHANNEL,
    EVENT_PRESET,
    EVENT_CHANNEL,
    STARTUP_RETRY_DELAY,
    INITIAL_RETRY_DELAY,
    MAXIMUM_RETRY_DELAY,
    NO_RETRY_DELAY_VALUE,
    CONF_ACTIVE,
    CONF_ACTIVE_ON,
    CONF_ACTIVE_INIT,
)


class BroadcasterError(Exception):
    """Class to handle errors with Broadcaster object."""

    def __init__(self, message):
        """Initialize the error."""
        self.message = message


class PresetError(Exception):
    """Class to handle errors with a Dynalite preset."""

    def __init__(self, message):
        """Initialize the error."""
        self.message = message


class ChannelError(Exception):
    """Class to handle errors with a Dynalite channel."""

    def __init__(self, message):
        """Initialize the error."""
        self.message = message


class AreaError(Exception):
    """Class to handle errors with a Dynalite area."""

    def __init__(self, message):
        """Initialize the error."""
        self.message = message


class DynaliteConfig(object):
    """Class for the configuration of the Dynalite network."""

    def __init__(self, config=None):
        """Initialize the configuration from Dict."""
        self.log_level = (
            config[CONF_LOGLEVEL].upper() if CONF_LOGLEVEL in config else logging.INFO
        )
        self.log_formatter = (
            config[CONF_LOGFORMATTER]
            if CONF_LOGFORMATTER in config
            else "[%(asctime)s] %(name)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s"
        )
        self.host = config[CONF_HOST] if CONF_HOST in config else "localhost"
        self.port = config[CONF_PORT] if CONF_PORT in config else 12345
        self.default = config[CONF_DEFAULT] if CONF_DEFAULT in config else {}
        self.area = config[CONF_AREA] if CONF_AREA in config else {}
        self.preset = config[CONF_PRESET] if CONF_PRESET in config else {}
        self.autodiscover = (
            config[CONF_AUTO_DISCOVER] if CONF_AUTO_DISCOVER in config else False
        )  # autodiscover by default
        self.polltimer = (
            config[CONF_POLLTIMER] if CONF_POLLTIMER in config else 1
        )  # default poll 1 sec
        self.active = config[CONF_ACTIVE] if CONF_ACTIVE in config else False


class Broadcaster(object):
    """Class to broadcast event to listeners."""

    def __init__(self, listenerFunction=None, loop=None, logger=None):
        """Initialize the broadcaster."""
        if listenerFunction is None:
            raise BroadcasterError("A broadcaster bust have a listener Function")
        self._listenerFunction = listenerFunction
        self._monitoredEvents = []
        self._loop = loop
        self.logger = logger

    def monitorEvent(self, eventType=None):
        """Set broadcaster to monitor an event or all."""
        if eventType is None:
            raise BroadcasterError("Must supply an event type to monitor")
        eventType = eventType.upper()
        if eventType not in self._monitoredEvents:
            self._monitoredEvents.append(eventType.upper())

    def unmonitorEvent(self, eventType=None):
        """Stop monitoring an event."""
        if eventType is None:
            raise BroadcasterError("Must supply an event type to un-monitor")
        eventType = eventType.upper()
        if eventType in self._monitoredEvents:
            self._monitoredEvents.remove(eventType.upper())

    def update(self, event=None, dynalite=None):
        """Update listener with an event if relevant."""
        if event is None:
            return
        if (
            event.eventType not in self._monitoredEvents
            and "*" not in self._monitoredEvents
        ):
            return
        if self._loop:
            self._loop.create_task(self._callUpdater(event=event, dynalite=dynalite))
        else:
            self._listenerFunction(event=event, dynalite=dynalite)

    @asyncio.coroutine
    def _callUpdater(self, event=None, dynalite=None):
        """Call listener callback function."""
        self._listenerFunction(event=event, dynalite=dynalite)


class DynalitePreset(object):
    """Class to represent a Dynalite area preset."""

    def __init__(
        self,
        name=None,
        value=None,
        fade=2,
        logger=None,
        broadcastFunction=None,
        area=None,
        dynetControl=None,
    ):
        """Initialize the preset."""
        if not value:
            raise PresetError("A preset must have a value")
        self.logger = logger
        self.active = False
        self.name = name if name else "Preset " + str(value)
        self.value = int(value)
        self.fade = float(fade)
        self.area = area
        self.broadcastFunction = broadcastFunction
        self._control = dynetControl
        if self.broadcastFunction:
            broadcastData = {
                CONF_AREA: self.area.value,
                CONF_PRESET: self.value,
                CONF_NAME: self.name,
                CONF_STATE: "OFF",
            }
            self.broadcastFunction(
                DynetEvent(eventType=EVENT_NEWPRESET, data=broadcastData)
            )

    def turnOn(self, sendDynet=True, sendMQTT=True):
        """Turn the preset on."""
        self.active = True
        if self.area:
            self.area.activePreset = self.value
        if sendMQTT and self.broadcastFunction:
            broadcastData = {
                CONF_AREA: self.area.value,
                CONF_PRESET: self.value,
                CONF_NAME: self.name,
                CONF_STATE: CONF_STATE_ON,
            }
            self.broadcastFunction(
                DynetEvent(eventType=EVENT_PRESET, data=broadcastData)
            )
        if sendDynet and self._control:
            self._control.areaPreset(
                area=self.area.value, preset=self.value, fade=self.fade
            )
        for preset in self.area.preset:
            if self.value != preset:
                if self.area.preset[preset].active:
                    self.area.preset[preset].turnOff(sendDynet=False, sendMQTT=True)
        if self._control.active == CONF_ACTIVE_ON:
            self.area.requestAllChannelLevels(delay=INITIAL_RETRY_DELAY, immediate=False)
        else:
            pass # XXX need to move them to default by preset

    def turnOff(self, sendDynet=True, sendMQTT=True):
        """Turn the preset off."""
        self.active = False
        if sendMQTT and self.broadcastFunction:
            broadcastData = {
                CONF_AREA: self.area.value,
                CONF_PRESET: self.value,
                CONF_NAME: self.name,
                CONF_STATE: CONF_STATE_OFF,
            }
            self.broadcastFunction(
                DynetEvent(eventType=EVENT_PRESET, data=broadcastData)
            )
        if sendDynet and self._control:
            self._control.areaOff(
                area=self.area.value, fade=self.fade
            )  # XXX TODO check if this behavior is correct. In general, you select a preset, so there is no real "turn-off"


class DynaliteChannel(object):
    """Class to represent a Dynalite channel."""

    def __init__(
        self,
        name=None,
        value=None,
        fade=2,
        presets=None,
        logger=None,
        broadcastFunction=None,
        area=None,
        dynetControl=None,
    ):
        """Initialize the channel."""
        logger.debug(
            "DynaliteChannel init called area=%s channel=%s fade=%s"
            % (area.value, value, fade)
        )
        if not value:
            raise ChannelError("A channel must have a value")
        self.logger = logger
        self.level = 0
        self.name = name if name else "Channel " + str(value)
        self.value = int(value)
        self.fade = float(fade)
        self.presets = presets
        self.area = area
        self.broadcastFunction = broadcastFunction
        self._control = dynetControl
        if self.broadcastFunction:
            broadcastData = {
                CONF_AREA: self.area.value,
                CONF_CHANNEL: self.value,
                CONF_NAME: self.name,
                CONF_LEVEL: self.level,
            }
            self.broadcastFunction(
                DynetEvent(eventType=EVENT_NEWCHANNEL, data=broadcastData)
            )
        if self._control.active == CONF_ACTIVE_ON:
            self.requestChannelLevel(
                delay=STARTUP_RETRY_DELAY
            )  # ask for the initial level, but don't resend quickly because the network may still be waiting
        elif self._control.active == CONF_ACTIVE_INIT:
            self.requestChannelLevel(
                delay=NO_RETRY_DELAY_VALUE
            )  # ask for the initial level, but don't retry
            
            
    def turnOn(self, brightness=1.0, sendDynet=True, sendMQTT=True):
        """Turn the channel on or set it to a specific brightness level."""
        if sendDynet and self._control:
            self._control.setChannel(
                area=self.area.value,
                channel=self.value,
                level=brightness,
                fade=self.fade,
            )
        if self._control.active:
            self.requestChannelLevel()
        else:
            self.setLevel(brightness)
            if self.broadcastFunction or True:
                broadcastData = {
                    CONF_AREA: self.area.value,
                    CONF_CHANNEL: self.value,
                    CONF_NAME: self.name,
                    CONF_TRGT_LEVEL: 255 - 254.0 * self.level,
                    CONF_ACTION: CONF_ACTION_CMD,
                }
                self.broadcastFunction(
                    DynetEvent(eventType=EVENT_CHANNEL, data=broadcastData)
                )

    def turnOff(self, sendDynet=True, sendMQTT=True):
        """Turn the channel off."""
        self.turnOn(0, sendDynet, sendMQTT)

    def requestChannelLevel(self, delay=None):
        """Request the channel level."""
        if delay:
            self.area.requestChannelLevel(self.value, delay=delay)
        else:
            self.area.requestChannelLevel(self.value)

    def stopFade(self):
        """Stop fading of the channel."""
        self._control.stop_channel_fade(area=self.area.value, channel=self.value)

    def getLevel(self):
        """Get current channel level."""
        return self.level

    def setLevel(self, level):
        """Set current channel level."""
        self.level = level


class RequestCounter:
    """Helper class to ensure that requests to Dynet for current preset or current channel level get retried but there is only one of each running at each time."""

    def __init__(self, loop, logger=None):
        """Initialize the class."""
        self.loop = loop
        self.logger = logger
        self.counter = 0
        self.timer = None

    def update(self):
        """Update that a new value arrive, so current requests can be cancelled."""
        if self.timer:
            self.timer.cancel()
            self.timer = None
        self.counter += 1

    def timerCallback(self, counter, delay, func, *args):
        """Send request if update was not yet received."""
        self.timer = None
        if self.counter > counter:  # already updated after the timer was scheduled
            return
        func(*args)
        newDelay = min(delay * 2, MAXIMUM_RETRY_DELAY)
        self.timer = self.loop.call_later(
            delay, self.timerCallback, self.counter, newDelay, func, *args
        )

    def schedule(self, delay, immediate, func, *args):
        """Schedule a request until an update arrives with an initial delay and either immediate or not."""
        if delay == NO_RETRY_DELAY_VALUE:
            func(*args)
            return
        if self.timer:
            self.timer.cancel()
        if immediate:
            self.timerCallback(self.counter, delay, func, *args)
        else:
            newDelay = min(delay * 2, MAXIMUM_RETRY_DELAY)
            self.timer = self.loop.call_later(
                delay, self.timerCallback, self.counter, newDelay, func, *args
            )


class DynaliteArea(object):
    """Class to represent a Dynalite area."""

    def __init__(
        self,
        name=None,
        value=None,
        fade=2,
        areaPresets=None,
        defaultPresets=None,
        areaChannels=None,
        areaType=None,
        onPreset=None,
        offPreset=None,
        loop=None,
        logger=None,
        broadcastFunction=None,
        dynetControl=None,
    ):
        """Initialize the area."""
        if not value:
            raise PresetError("An area must have a value")
        self.loop = loop
        self.logger = logger
        self.name = name if name else "Area " + str(value)
        self.type = areaType.lower() if areaType else "light"
        self.value = int(value)
        self.fade = fade
        self.preset = {}
        self.channel = {}
        self.channelUpdateCounter = {}
        self.presetUpdateCounter = RequestCounter(self.loop, self.logger)
        self.activePreset = None
        self.state = None

        if self.type == "cover":
            self._onName = "OPEN"
            self._offName = "CLOSED"
            if onPreset is not None:
                self.openPreset = onPreset
            if offPreset is not None:
                self.closePreset = offPreset
        else:
            self._onName = CONF_STATE_ON
            self._offName = CONF_STATE_OFF
            if onPreset is not None:
                self.onPreset = onPreset
            if offPreset is not None:
                self.offPreset = offPreset

        self.broadcastFunction = broadcastFunction
        self._dynetControl = dynetControl
        
        if self._dynetControl.active == CONF_ACTIVE_ON:
            self.requestPreset(delay=STARTUP_RETRY_DELAY)  # ask for the initial preset
        elif self._dynetControl.active == CONF_ACTIVE_INIT:
            self.requestPreset(delay=NO_RETRY_DELAY_VALUE)  # no retry
        
        if areaPresets:
            for presetValue in areaPresets:
                preset = areaPresets[presetValue]
                presetName = preset[CONF_NAME] if CONF_NAME in preset else None
                presetFade = preset[CONF_FADE] if CONF_FADE in preset else fade
                self.preset[int(presetValue)] = DynalitePreset(
                    name=presetName,
                    value=presetValue,
                    fade=presetFade,
                    logger=self.logger,
                    broadcastFunction=self.broadcastFunction,
                    area=self,
                    dynetControl=self._dynetControl,
                )
        if defaultPresets:
            for presetValue in defaultPresets:
                if int(presetValue) not in self.preset:
                    preset = defaultPresets[presetValue]
                    presetName = preset[CONF_NAME] if preset[CONF_NAME] else None
                    presetFade = preset[CONF_FADE] if preset[CONF_FADE] else fade
                    self.preset[int(presetValue)] = DynalitePreset(
                        name=presetName,
                        value=presetValue,
                        fade=presetFade,
                        logger=self.logger,
                        broadcastFunction=self.broadcastFunction,
                        area=self,
                        dynetControl=self._dynetControl,
                    )
        if areaChannels:
            for channelValue in areaChannels:
                if (int(channelValue) >= 1) and (int(channelValue) <= 255):
                    channel = areaChannels[channelValue]
                    specific_name = (
                        channel[CONF_NAME]
                        if channel and (CONF_NAME in channel)
                        else "Channel " + channelValue
                    )
                    name = self.name + " " + specific_name
                    fade = (
                        channel[CONF_FADE]
                        if channel and (CONF_FADE in channel)
                        else self.fade
                    )  # if no fade provided, use the fade of the area
                    self.channel[int(channelValue)] = DynaliteChannel(
                        name=name,
                        value=channelValue,
                        fade=fade,
                        logger=self.logger,
                        broadcastFunction=self.broadcastFunction,
                        area=self,
                        dynetControl=self._dynetControl,
                    )
                    self.logger.debug(
                        "added area %s channel %s name %s"
                        % (self.name, channelValue, name)
                    )
                else:
                    self.logger.error(
                        "illegal channel value area %s channel %s"
                        % (self.name, channelValue)
                    )
        else:
            self.channel = {}

    def presetOn(self, preset, sendDynet=True, sendMQTT=True, autodiscover=False):
        """Turn a selected preset on and everyone else off."""
        if hasattr(self, "onPreset"):
            if self.onPreset == preset:
                self.state = self._onName
        else:
            self.state = self._offName
        if preset not in self.preset:
            if not autodiscover:
                return
            self.preset[preset] = DynalitePreset(
                value=preset,
                fade=self.fade,
                logger=self.logger,
                broadcastFunction=self.broadcastFunction,
                area=self,
                dynetControl=self._dynetControl,
            )
        self.preset[preset].turnOn(sendDynet=sendDynet, sendMQTT=sendMQTT)

    def presetOff(
        self, preset, sendDynet=True, sendMQTT=True
    ):  # XXX TODO check if this is used anywhere. generally presets cannot be turned off
        """Turn a selected preset off."""
        if preset not in self.preset:
            return  # XXX if we want it to auto-register presets need to fix race condition
            self.preset[preset] = DynalitePreset(
                value=preset,
                fade=self.fade,
                logger=self.logger,
                broadcastFunction=self.broadcastFunction,
                area=self,
                dynetControl=self._dynetControl,
            )
        else:  # this still has a bug that the preset won't be selected when chosen. Need a better fix for the race XXX
            self.preset[preset].turnOff(sendDynet=sendDynet, sendMQTT=sendMQTT)

    def requestPreset(self, delay=INITIAL_RETRY_DELAY, immediate=True):
        """Request the preset for the area."""

        def shouldRun():
            """Return whether or not command is still relevant."""
            return self.presetUpdateCounter.counter == currentCounter

        currentCounter = self.presetUpdateCounter.counter
        self.presetUpdateCounter.schedule(
            delay,
            immediate,
            self._dynetControl.request_area_preset,
            self.value,
            shouldRun,
        )

    def setChannelLevel(self, channel, level, autodiscover=False):
        """Set a channel in an area to a given level. Create it if necessary."""
        if channel in self.channelUpdateCounter:
            self.channelUpdateCounter[channel].update()
        if channel not in self.channel:
            if not autodiscover:
                return
            self.channel[channel] = DynaliteChannel(
                value=channel,
                fade=self.fade,
                logger=self.logger,
                broadcastFunction=self.broadcastFunction,
                area=self,
                dynetControl=self._dynetControl,
            )
        self.channel[channel].setLevel(level)

    def requestChannelLevel(self, channel, delay=INITIAL_RETRY_DELAY, immediate=True):
        """Request the level of a specific channel."""

        def shouldRun():
            """Return whether or not command is still relevant."""
            return self.channelUpdateCounter[channel].counter == currentCounter

        if channel not in self.channelUpdateCounter:
            self.channelUpdateCounter[channel] = RequestCounter(self.loop, self.logger)
        currentCounter = self.channelUpdateCounter[channel].counter
        self.channelUpdateCounter[channel].schedule(
            delay,
            immediate,
            self._dynetControl.request_channel_level,
            self.value,
            channel,
            shouldRun,
        )

    def requestAllChannelLevels(self, delay=INITIAL_RETRY_DELAY, immediate=True):
        """Request channel levels for all channels in an area."""
        if self.channel:
            for channel in self.channel:
                self.requestChannelLevel(channel, delay, immediate)


class Dynalite(object):
    """Class to represent the interaction with Dynalite."""

    def __init__(self, config=None, loop=None, logger=None):
        """Initialize the class."""
        self.loop = loop if loop else asyncio.get_event_loop()
        self.logger = logger if logger else logging.getLogger(__name__)
        self._config = DynaliteConfig(config=config)
        logging.basicConfig(
            level=self._config.log_level, format=self._config.log_formatter
        )

        self._configured = False
        self._autodiscover = False
        self._listeners = []

        self.devices = {CONF_AREA: {}}

        self._dynet = None
        self.control = None

    def start(self):
        """Queue request to start the class."""
        self.loop.create_task(self._start())

    @asyncio.coroutine
    def _start(self):
        """Start the class."""
        self._dynet = Dynet(
            host=self._config.host,
            port=self._config.port,
            active=self._config.active,
            loop=self.loop,
            broadcaster=self.processTraffic,
            onConnect=self._connected,
            onDisconnect=self._disconnection,
        )
        self.control = DynetControl(
            self._dynet, self.loop, self._config.active, areaDefinition=self.devices[CONF_AREA]
        )
        self.connect()  # connect asynchronously. not needed to register devices
        if not self._configured:
            self.loop.create_task(self._configure())

    def connect(self):
        """Queue command to connect to Dynet."""
        self.loop.create_task(self._connect())

    @asyncio.coroutine
    def _connect(self):
        """Connect to Dynet."""
        self._dynet.connect()

    @asyncio.coroutine
    def _connected(self, dynet=None, transport=None):
        """Handle a successful connection."""
        self.broadcast(DynetEvent(eventType=EVENT_CONNECTED, data={}))

    @asyncio.coroutine
    def _disconnection(self, dynet=None):
        """Handle a disconnection and try to reconnect."""
        self.broadcast(DynetEvent(eventType=EVENT_DISCONNECTED, data={}))
        yield from asyncio.sleep(1)  # Don't overload the network
        self.connect()

    def processTraffic(self, event):
        """Process an event that arrived from Dynet - queue."""
        self.loop.create_task(self._processTraffic(event))

    @asyncio.coroutine
    def _processTraffic(self, event):
        """Process an event that arrived from Dynet - async."""
        # The logic here is:
        # - new area is created - ask for the current preset
        # - preset selected - turn the preset on but don't send it as a command
        # - new channel is created - ask for the current level
        # - channel update - update the level and if it is fading (actual != target), schedule a timer to ask again
        # - channel set command - request current level (may not be the target because of fade)
        areaValue = event.data[CONF_AREA]
        if areaValue not in self.devices[CONF_AREA]:
            self.logger.debug("Update from unknown area: %s" % event.toJson)
            if self._autodiscover:
                areaName = "Area " + str(areaValue)
                areaFade = (
                    self._config.default[CONF_FADE]
                    if CONF_FADE in self._config.default
                    else 2
                )
                self.devices[CONF_AREA][areaValue] = DynaliteArea(
                    name=areaName,
                    value=areaValue,
                    fade=areaFade,
                    loop=self.loop,
                    logger=self.logger,
                    broadcastFunction=self.broadcast,
                    dynetControl=self.control,
                )
            else:
                return  # No need to do anything if the area is not defined and we do not have autodiscovery
        curArea = self.devices[CONF_AREA][areaValue]

        if event.eventType in [EVENT_NEWPRESET, EVENT_NEWCHANNEL]:
            self.logger.error(
                event.eventType + " in _processTraffic - we should not get here"
            )
        elif event.eventType == EVENT_PRESET:
            curArea.presetOn(
                event.data[CONF_PRESET],
                sendDynet=False,
                sendMQTT=False,
                autodiscover=self._autodiscover,
            )
            curArea.presetUpdateCounter.update()
        elif event.eventType == EVENT_CHANNEL:
            if event.data[CONF_ACTION] == CONF_ACTION_REPORT:
                if self._config.active == CONF_ACTIVE_ON:
                    curArea.setChannelLevel(
                        event.data[CONF_CHANNEL],
                        (255 - event.data[CONF_ACT_LEVEL]) / 254.0,
                        self._autodiscover,
                    )
                    if event.data[CONF_ACT_LEVEL] != event.data[CONF_TRGT_LEVEL]:
                        self.loop.call_later(
                            self._polltimer,
                            curArea.requestChannelLevel,
                            event.data[CONF_CHANNEL],
                        )
                else:
                    curArea.setChannelLevel(
                        event.data[CONF_CHANNEL],
                        (255 - event.data[CONF_TRGT_LEVEL]) / 254.0,
                        self._autodiscover,
                    )
                    
            elif event.data[CONF_ACTION] == CONF_ACTION_CMD:
                target_level = False
                if CONF_PRESET in event.data:
                    try:
                        target_level = curArea.channel[
                            event.data[CONF_CHANNEL]
                        ].presets[str(event.data[CONF_PRESET])]
                    except (KeyError, TypeError):
                        pass
                if CONF_TRGT_LEVEL in event.data:
                    target_level = (255 - event.data[CONF_TRGT_LEVEL]) / 254.0
                if target_level:  # check if this is relevant for "ALL"
                    if event.data[CONF_CHANNEL] == CONF_ALL:
                        raise Exception(
                            "CHANNEL event with ALL and target_level - should never happen"
                        )  # XXX find a better way to handle it
                    curArea.setChannelLevel(
                        event.data[CONF_CHANNEL], target_level, self._autodiscover
                    )
                if self._config.active == CONF_ACTIVE_ON:
                    if event.data[CONF_CHANNEL] == CONF_ALL:
                        curArea.requestAllChannelLevels()
                    else:
                        curArea.requestChannelLevel(event.data[CONF_CHANNEL])
            else:
                self.logger.warning("CHANNEL command unknown cmd: %s" % event.toJson)
        else:
            self.logger.debug("Unknown event type: %s" % event.toJson)
        # First handle, and then broadcast so broadcast receivers have updated device levels and presets
        self.broadcast(event)

    def broadcast(self, event):
        """Broadcast an event to all listeners - queue."""
        self.loop.create_task(self._broadcast(event))

    @asyncio.coroutine
    def _broadcast(self, event):
        """Broadcast an event to all listeners - async."""
        for listenerFunction in self._listeners:
            listenerFunction.update(event=event, dynalite=self)

    @asyncio.coroutine
    def _configure(self):
        """Configure the class from saved config attribute."""
        self._autodiscover = self._config.autodiscover
        self._polltimer = self._config.polltimer
        for areaValue in self._config.area:
            areaName = (
                self._config.area[areaValue][CONF_NAME]
                if CONF_NAME in self._config.area[areaValue]
                else None
            )
            areaPresets = (
                self._config.area[areaValue][CONF_PRESET]
                if CONF_PRESET in self._config.area[areaValue]
                else {}
            )
            areaFade = (
                self._config.area[areaValue][CONF_FADE]
                if CONF_FADE in self._config.area[areaValue]
                else None
            )
            if areaFade is None:
                areaFade = (
                    self._config.default[CONF_FADE]
                    if CONF_FADE in self._config.default
                    else 2
                )
            areaFade = float(areaFade)
            areaChannels = (
                self._config.area[areaValue][CONF_CHANNEL]
                if CONF_CHANNEL in self._config.area[areaValue]
                else None
            )
            if (
                CONF_NODEFAULT in self._config.area[areaValue]
                and self._config.area[areaValue][CONF_NODEFAULT]
            ):
                defaultPresets = None
            else:
                defaultPresets = self._config.preset

            self.logger.debug(
                "Generating Area '%d/%s' with a default fade of %f"
                % (int(areaValue), areaName, areaFade)
            )
            self.devices[CONF_AREA][int(areaValue)] = DynaliteArea(
                name=areaName,
                value=areaValue,
                fade=areaFade,
                areaPresets=areaPresets,
                areaChannels=areaChannels,
                defaultPresets=defaultPresets,
                loop=self.loop,
                logger=self.logger,
                broadcastFunction=self.broadcast,
                dynetControl=self.control,
            )
        self._configured = True
        self.broadcast(DynetEvent(eventType=EVENT_CONFIGURED, data={}))

    def state(self):
        """Create the state for testing - queue."""
        self.loop.create_task(self._state())

    @asyncio.coroutine
    def _state(self):
        """Create the state for testing - async."""
        for areaValue in self.devices[CONF_AREA]:
            area = self.devices[CONF_AREA][areaValue]
            for presetValue in area.preset:
                preset = area.preset[presetValue]
                presetState = "ON" if preset.active else "OFF"
                broadcastData = {
                    CONF_AREA: area.value,
                    CONF_PRESET: preset.value,
                    CONF_NAME: area.name + " " + preset.name,
                    CONF_STATE: presetState,
                }
                self.broadcast(
                    DynetEvent(eventType=EVENT_NEWPRESET, data=broadcastData)
                )
                if preset.active:
                    self.broadcast(
                        DynetEvent(eventType=EVENT_PRESET, data=broadcastData)
                    )
            self.control.areaReqPreset(area.value)

    def addListener(self, listenerFunction=None):
        """Create a new listener to the class."""
        broadcaster = Broadcaster(
            listenerFunction=listenerFunction, loop=self.loop, logger=self.logger
        )
        self._listeners.append(broadcaster)
        return broadcaster
