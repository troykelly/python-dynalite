"""
@ Author      : Troy Kelly
@ Date        : 23 Sept 2018
@ Description : Philips Dynalite Library - Unofficial interface for Philips Dynalite over RS485

@ Notes:        Requires a RS485 to IP gateway (Do not use the Dynalite one - use something cheaper)
"""

import asyncio
import logging
import json
import time
from .const import OpcodeType, SyncType, CONF_ACTIVE_ON, CONF_ACTIVE_INIT, CONF_ACTIVE_OFF
from .inbound import DynetInbound

DEFAULT_LOG = logging.getLogger(__name__)


class DynetError(Exception):
    """Class for Dynet errors."""

    def __init__(self, message):
        """Initialize the error."""
        self.message = message


class PacketError(Exception):
    """Class for Dynet packet errors."""

    def __init__(self, message):
        """Initialize the error."""
        self.message = message


class DynetPacket(object):
    """Class for a Dynet network packet."""

    def __init__(self, msg=None, shouldRun=None):
        """Initialize the packet."""
        self.opcodeType = None
        self.sync = None
        self.area = None
        self.data = []
        self.command = None
        self.join = None
        self.chk = None
        if msg is not None:
            self.fromMsg(msg)
        self.shouldRun = shouldRun

    def toMsg(self, sync=28, area=0, command=0, data=[0, 0, 0], join=255):
        """Convert packet to a binary message."""
        bytes = []
        bytes.append(sync)
        bytes.append(area)
        bytes.append(data[0])
        bytes.append(command)
        bytes.append(data[1])
        bytes.append(data[2])
        bytes.append(join)
        bytes.append(self.calcsum(bytes))
        self.fromMsg(bytes)

    def fromMsg(self, msg):
        """Decode a Dynet message."""
        messageLength = len(msg)
        if messageLength < 8:
            raise PacketError("Message too short (%d bytes): %s" % (len(msg), msg))

        if messageLength > 8:
            raise PacketError("Message too long (%d bytes): %s" % (len(msg), msg))

        self._msg = msg

        self.sync = self._msg[0]
        self.area = self._msg[1]
        self.data = [self._msg[2], self._msg[4], self._msg[5]]
        self.command = self._msg[3]
        self.join = self._msg[6]
        self.chk = self._msg[7]
        if self.sync == 28:
            if OpcodeType.has_value(self.command):
                self.opcodeType = OpcodeType(self.command).name

    def toJson(self):
        """Convert to JSON."""
        return json.dumps(self.__dict__)

    def calcsum(self, msg):
        """Calculate the checksum."""
        msg = msg[:7]
        return -(sum(ord(c) for c in "".join(map(chr, msg))) % 256) & 0xFF

    def __repr__(self):
        """Print the packet."""
        return json.dumps(self.__dict__)


class DynetConnection(asyncio.Protocol):
    """Class for an asyncio protocol for the connection to Dynet."""

    def __init__(
        self,
        connectionMade=None,
        connectionLost=None,
        receiveHandler=None,
        connectionPause=None,
        connectionResume=None,
        loop=None,
        logger=DEFAULT_LOG,
    ):
        """Initialize the connection."""
        self._transport = None
        self._paused = False
        self._loop = loop
        self._logger = logger
        self.connectionMade = connectionMade
        self.connectionLost = connectionLost
        self.receiveHandler = receiveHandler
        self.connectionPause = connectionPause
        self.connectionResume = connectionResume

    def connection_made(self, transport):
        """Call when connection is made."""
        self._transport = transport
        self._paused = False
        if self.connectionMade is not None:
            if self._loop is None:
                self.connectionMade(transport)
            else:
                self._loop.create_task(self.connectionMade(transport))

    def connection_lost(self, exc=None):
        """Call when connection is lost."""
        self._transport = None
        if self.connectionLost is not None:
            if self._loop is None:
                self.connectionLost(exc)
            else:
                self._loop.create_task(self.connectionLost(exc))

    def pause_writing(self):
        """Call when connection is paused."""
        self._paused = True
        if self.connectionPause is not None:
            if self._loop is None:
                self.connectionPause()
            else:
                self._loop.create_task(self.connectionPause())

    def resume_writing(self):
        """Call when connection is resumed."""
        self._paused = False
        if self.connectionResume is not None:
            if self._loop is None:
                self.connectionResume()
            else:
                self._loop.create_task(self.connectionResume())

    def data_received(self, data):
        """Call when data is received."""
        if self.receiveHandler is not None:
            if self._loop is None:
                self.receiveHandler(data)
            else:
                self._loop.create_task(self.receiveHandler(data))

    def eof_received(self):
        """Call when EOF for connection."""
        self._logger.debug("EOF Received")


class DynetControl(object):
    """Class to control devices on Dynet network."""

    def __init__(self, dynet, loop, active, areaDefinition=None, logger=DEFAULT_LOG):
        """Initialize the class."""
        self._dynet = dynet
        self._loop = loop
        self.active = active
        self._area = areaDefinition
        self._logger = logger

    def areaPreset(self, area, preset, fade=2):
        """Area preset was set - queue."""
        return self._loop.create_task(
            self._areaPreset(area=area, preset=preset, fade=fade)
        )

    @asyncio.coroutine
    def _areaPreset(self, area, preset, fade):
        """Area preset was set - async."""
        packet = DynetPacket()
        preset = preset - 1
        bank = int((preset) / 8)
        opcode = preset - (bank * 8)
        if opcode > 3:
            opcode = opcode + 6
        fadeLow = int(fade / 0.02) - (int((fade / 0.02) / 256) * 256)
        fadeHigh = int((fade / 0.02) / 256)
        packet.toMsg(
            sync=28, area=area, command=opcode, data=[fadeLow, fadeHigh, bank], join=255
        )
        self._dynet.write(packet)

    def setChannel(self, area, channel, level, fade=2):
        """Set a channel to a given level - queue."""
        return self._loop.create_task(
            self._setChannel(area=area, channel=channel, level=level, fade=fade)
        )

    @asyncio.coroutine
    def _setChannel(self, area, channel, level, fade):
        """Set a channel to a given level - async."""
        packet = DynetPacket()
        channel_bank = 0xFF if (channel <= 4) else (int((channel - 1) / 4) - 1)
        target_level = int(255 - 254 * level)
        opcode = 0x80 + ((channel - 1) % 4)
        fade_time = int(fade / 0.02)
        if (fade_time) > 0xFF:
            fade_time = 0xFF
        packet.toMsg(
            sync=28,
            area=area,
            command=opcode,
            data=[target_level, channel_bank, fade_time],
            join=255,
        )
        self._dynet.write(packet)

    def request_channel_level(self, area, channel, shouldRun=None):
        """Request a level for a specific channel. - queue."""
        return self._loop.create_task(
            self._request_channel_level(area=area, channel=channel, shouldRun=shouldRun)
        )

    @asyncio.coroutine
    def _request_channel_level(self, area, channel, shouldRun):
        """Request a level for a specific channel. - async."""
        packet = DynetPacket(shouldRun=shouldRun)
        packet.toMsg(
            sync=28,
            area=area,
            command=OpcodeType.REQUEST_CHANNEL_LEVEL.value,
            data=[channel - 1, 0, 0],
            join=255,
        )
        self._dynet.write(packet)

    def stop_channel_fade(self, area, channel):
        """Stop fading of a channel - queue."""
        return self._loop.create_task(
            self._stop_channel_fade(area=area, channel=channel)
        )

    @asyncio.coroutine
    def _stop_channel_fade(self, area, channel):
        """Stop fading of a channel - async."""
        packet = DynetPacket()
        packet.toMsg(
            sync=28,
            area=area,
            command=OpcodeType.STOP_FADING.value,
            data=[channel - 1, 0, 0],
            join=255,
        )
        self._dynet.write(packet)

    def areaOff(self, area, fade=2):
        """Turn an area off - queue."""
        return self._loop.create_task(self._areaOff(area=area, fade=fade))

    @asyncio.coroutine
    def _areaOff(self, area, fade):
        """Turn an area off - async."""
        packet = DynetPacket()
        if fade > 25.5:
            fade = 25.5
        if fade < 0:
            fade = 0
        packet.toMsg(
            sync=28, area=area, command=104, data=[255, 0, int(fade * 10)], join=255
        )
        self._dynet.write(packet)

    def request_area_preset(self, area, shouldRun=None):
        """Request current preset of an area - queue."""
        return self._loop.create_task(
            self._request_area_preset(area=area, shouldRun=shouldRun)
        )

    @asyncio.coroutine
    def _request_area_preset(self, area, shouldRun):
        """Request current preset of an area - async."""
        packet = DynetPacket(shouldRun=shouldRun)
        packet.toMsg(
            sync=28,
            area=area,
            command=OpcodeType.REQUEST_PRESET.value,
            data=[0, 0, 0],
            join=255,
        )
        self._dynet.write(packet)


class Dynet(object):
    """Class to handle communication with Dynet network."""

    def __init__(
        self,
        host=None,
        port=None,
        active=CONF_ACTIVE_OFF,
        broadcaster=None,
        onConnect=None,
        onDisconnect=None,
        loop=None,
        logger=DEFAULT_LOG,
    ):
        """Initialize the class."""
        if host is None or port is None or loop is None:
            raise DynetError("Must supply a host, port and loop for Dynet connection")
        self._host = host
        self._port = port
        self._loop = loop
        self._logger = logger
        self.broadcast = broadcaster
        self._onConnect = onConnect
        self._onDisconnect = onDisconnect
        self._conn = lambda: DynetConnection(
            connectionMade=self._connection,
            connectionLost=self._disconnection,
            receiveHandler=self._receive,
            connectionPause=self._pause,
            connectionResume=self._resume,
            loop=self._loop,
        )
        self._transport = None
        self._handlers = {}
        self._connection_retry_timer = 1
        self._paused = False
        self._inBuffer = []
        self._outBuffer = []
        self._timeout = 30
        self.active = active

        self._lastSent = None
        self._messageDelay = 200
        self._sending = False

    def cleanup(self):
        """Clean up with new connection or disconnection."""
        self._connection_retry_timer = 1
        self._transport = None

    def connect(self, onConnect=None):
        """Connect to Dynet - queue."""
        return self._loop.create_task(self._connect())

    async def _connect(self):
        """Connect to Dynet - async."""
        self._logger.debug("Connecting to Dynet on %s:%d" % (self._host, self._port))
        try:
            await asyncio.wait_for(
                self._loop.create_connection(
                    self._conn, host=self._host, port=self._port
                ),
                timeout=self._timeout,
            )
        except (ValueError, OSError, asyncio.TimeoutError) as err:
            self._logger.warning(
                "Could not connect to Dynet (%s). Retrying in %d seconds",
                err,
                self._connection_retry_timer,
            )
            self._loop.call_later(self._connection_retry_timer, self.connect)
            self._connection_retry_timer = (
                2 * self._connection_retry_timer
                if self._connection_retry_timer < 32
                else 60
            )

    @asyncio.coroutine
    def _receive(self, data=None):
        """Handle data that was received."""
        if data is not None:
            for byte in data:
                self._inBuffer.append(int(byte))

        if len(self._inBuffer) < 8:
            self._logger.debug(
                "Received %d bytes, not enough to process: %s"
                % (len(self._inBuffer), self._inBuffer)
            )

        packet = None
        while len(self._inBuffer) >= 8 and packet is None:
            firstByte = self._inBuffer[0]
            if SyncType.has_value(firstByte):
                if firstByte == SyncType.DEBUG_MSG.value:
                    bytemsg = "".join(chr(c) for c in self._inBuffer[1:7])
                    self._logger.debug("Dynet DEBUG message %s" % bytemsg)
                    self._inBuffer = self._inBuffer[8:]
                    continue
                elif firstByte == SyncType.DEVICE.value:
                    self._logger.debug(
                        "Not handling Dynet DEVICE message %s" % self._inBuffer[:8]
                    )
                    self._inBuffer = self._inBuffer[8:]
                    continue
                elif firstByte == SyncType.LOGICAL.value:
                    try:
                        packet = DynetPacket(msg=self._inBuffer[:8])
                    except PacketError as err:
                        self._logger.warning(err)
                        packet = None

            if packet is None:
                hexString = ":".join("{:02x}".format(c) for c in self._inBuffer[:8])
                self._logger.debug(
                    "Unable to process packet %s - moving one byte forward" % hexString
                )
                del self._inBuffer[0]
                continue
            else:
                self._inBuffer = self._inBuffer[8:]

            self._logger.debug("Have packet: %s" % packet)

            if hasattr(packet, "opcodeType") and packet.opcodeType is not None:
                inboundHandler = DynetInbound()
                if hasattr(inboundHandler, packet.opcodeType.lower()):
                    event = getattr(inboundHandler, packet.opcodeType.lower())(packet)
                    if event:
                        self.broadcast(event)
                else:
                    self._logger.debug(
                        "Unhandled Dynet Inbound (%s): %s" % (packet.opcodeType, packet)
                    )
            else:
                self._logger.debug("Unhandled Dynet Inbound: %s" % packet)
        # If there is still buffer to process - start again
        if len(self._inBuffer) >= 8:
            self._loop.create_task(self._receive())

    @asyncio.coroutine
    def _pause(self):
        """Pause transmission on Dynet."""
        self._logger.debug("Pausing Dynet on %s:%d" % (self._host, self._port))
        # Need to schedule a resend here
        self._paused = True

    @asyncio.coroutine
    def _resume(self):
        """Resume transmission on Dynet."""
        self._logger.debug("Resuming Dynet on %s:%d" % (self._host, self._port))
        # Need to schedule a resend here
        self._paused = False

    @asyncio.coroutine
    def _connection(self, transport=None):
        """Handle a new successful connection."""
        self._logger.debug("Connected to Dynet on %s:%d" % (self._host, self._port))
        self.cleanup()
        if transport is not None:
            self.write()  # write whatever is queued in the buffer
            self._transport = transport
            if self._onConnect is not None:
                self._loop.create_task(self._onConnect(dynet=self, transport=transport))
        else:
            raise DynetError("Connected but no transport channel provided")

    @asyncio.coroutine
    def _disconnection(self, exc=None):
        """Handle a network disconnection from Dynet."""
        self._logger.debug(
            "Disconnected from Dynet on %s:%d" % (self._host, self._port)
        )
        self.cleanup()
        if self._onDisconnect is not None:
            self._loop.create_task(self._onDisconnect(dynet=self))

        if exc is not None:
            self._logger.warning(exc)

    def write(self, packet=None):
        """Write a packet or trigger write loop - queue."""
        self._loop.create_task(self._write(packet))

    @asyncio.coroutine
    def _write(self, newPacket=None):
        """Write a packet or trigger write loop - async."""
        if newPacket is not None:
            self._outBuffer.append(newPacket)

        if self._transport is None:
            self._logger.debug("_write before transport is ready. queuing")
            return

        if self._paused or self._sending:
            self._logger.debug("Connection busy - queuing packet")
            self._loop.call_later(1, self.write)
            return

        if self._lastSent is None:
            self._lastSent = int(round(time.time() * 1000))

        current_milli_time = int(round(time.time() * 1000))
        elapsed = current_milli_time - self._lastSent
        delay = 0 - (elapsed - self._messageDelay)
        if delay > 0:
            self._loop.call_later(delay / 1000, self.write)
            return

        if len(self._outBuffer) == 0:
            return

        packet = self._outBuffer[0]
        if packet.shouldRun is None or packet.shouldRun():
            self._sending = True
            msg = bytearray()
            msg.append(packet.sync)
            msg.append(packet.area)
            msg.append(packet.data[0])
            msg.append(packet.command)
            msg.append(packet.data[1])
            msg.append(packet.data[2])
            msg.append(packet.join)
            msg.append(packet.chk)
            assert self.active in [CONF_ACTIVE_ON, CONF_ACTIVE_INIT] or packet.command not in [OpcodeType.REQUEST_CHANNEL_LEVEL.value, OpcodeType.REQUEST_PRESET.value]
            self._transport.write(msg)
            self._logger.debug("Dynet Sent: %s" % msg)
            self._lastSent = int(round(time.time() * 1000))
            self._sending = False

        del self._outBuffer[0]
        if len(self._outBuffer) > 0:
            self._loop.call_later(self._messageDelay / 1000, self.write)
