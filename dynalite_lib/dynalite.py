"""Master class that combines all ElkM1 pieces together."""

import asyncio
from functools import partial
import logging
from importlib import import_module

from .message import add_message_handler, message_decode
from .proto import Connection

LOG = logging.getLogger(__name__)


class Dynalite:
    """Represents all the components in a Dynalite system."""

    def __init__(self, config, loop=None):
        """Initialize a new Dynalite instance."""
        self.loop = loop if loop else asyncio.get_event_loop()
        self._config = config
        self._conn = None
        self._transport = None
        self.connection_lost_callbk = None
        self._connection_retry_timer = 1

        self._heartbeat = None

        # Setup for all the types of elements tracked
        if 'element_list' in config:
            self.element_list = config['element_list']
        else:
            self.element_list = ['areas']

        for element in self.element_list:
            self._create_element(element)

    def _create_element(self, element):
        module = import_module('dynalite_lib.'+element)
        class_ = getattr(module, element.capitalize())
        setattr(self, element, class_(self))

    async def _connect(self, connection_lost_callbk=None):
        """Asyncio connection to Dynalite."""
        self.connection_lost_callbk = connection_lost_callbk
        host = self._config['host']
        port = self._config['port']
        LOG.info("Connecting to Dynalite at %s", host)
        conn = partial(Connection, self.loop, self._connected,
                       self._disconnected, self._got_data)
        try:
            await asyncio.wait_for(self.loop.create_connection(
                conn, host=host, port=port), timeout=30)
        except (ValueError, OSError, asyncio.TimeoutError) as err:
            LOG.warning("Could not connect to Dynalite (%s). Retrying in %d seconds",
                        err, self._connection_retry_timer)
            self.loop.call_later(self._connection_retry_timer, self.connect)
            self._connection_retry_timer = 2 * self._connection_retry_timer \
                if self._connection_retry_timer < 32 else 60

    def _connected(self, transport, conn):
        """Connected to Dynalite"""
        LOG.info("Connected to Dynalite")
        self._conn = conn
        self._transport = transport
        self._connection_retry_timer = 1
        self._heartbeat = self.loop.call_later(120, self._reset_connection)


    def _reset_connection(self):
        LOG.warning("Dynalite connection heartbeat timed out, disconnecting")
        self._transport.close()
        self._heartbeat = None

    def _disconnected(self):
        LOG.warning("Dynalite disconnected")
        self._conn = None
        self.loop.call_later(self._connection_retry_timer, self.connect)
        if self._heartbeat:
            self._heartbeat.cancel()
            self._heartbeat = None

    def _got_data(self, data):  # pylint: disable=no-self-use
        LOG.debug("got_data '%s'", data)
        try:
            message_decode(data)
        except ValueError as err:
            LOG.debug(err)

    def is_connected(self):
        """Status of connection to Dyanlite."""
        return self._conn is not None

    def connect(self):
        """Connect to the Dynalite"""
        asyncio.ensure_future(self._connect())

    def run(self):
        """Enter the asyncio loop."""
        self.loop.run_forever()

    def send(self, msg):
        """Send a message to Dynalite panel."""
        if self._conn:
            self._conn.write_data(msg.message, msg.response_command)

    def pause(self):
        """Pause the connection from sending/receiving."""
        if self._conn:
            self._conn.pause()

    def resume(self):
        """Restart the connection from sending/receiving."""
        if self._conn:
            self._conn.resume()
