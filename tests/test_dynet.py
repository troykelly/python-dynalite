import pytest
from asynctest import CoroutineMock
import asyncio
from unittest.mock import patch, Mock

from dynalite_lib.dynet import Dynet, DynetError
import logging
LOGGER = logging.getLogger(__name__)

def func():
    pass

def async_mock(mock):
    """Return the return value of a mock from async."""

    async def async_func(*args, **kwargs):
        return mock(*args, **kwargs)

    return async_func


    
@pytest.mark.asyncio
async def test_dynet_no_host_loop_port():
    host = "1.2.3.4"
    port = 5678
    broadcaster = Mock()
    on_connect = Mock()
    on_disconnect = Mock()
    loop = asyncio.get_event_loop()
    with patch("dynalite_lib.dynet.DynetConnection") as dyn_connection:
        with pytest.raises(DynetError):
            dynet = Dynet(None, port, broadcaster, on_connect, on_disconnect, loop)
        with pytest.raises(DynetError):
            dynet = Dynet(host, None, broadcaster, on_connect, on_disconnect, loop)
        with pytest.raises(DynetError):
            dynet = Dynet(host, port, broadcaster, on_connect, on_disconnect, None)
            
@pytest.mark.asyncio
async def test_dynet_connect():
    host = "1.2.3.4"
    port = 5678
    broadcaster = Mock()
    on_connect = Mock()
    on_disconnect = Mock()
    loop = asyncio.get_event_loop()
    with patch("dynalite_lib.dynet.DynetConnection") as dyn_connection:
        dynet = Dynet(host, port, broadcaster, on_connect, on_disconnect, loop)
        assert dynet._conn() is dyn_connection.return_value
        connection = Mock()
        with patch.object(loop, "create_connection", async_mock(connection)):
            await dynet.connect()
            connection.assert_called_once()
            assert connection.mock_calls[0][1][0]() is dyn_connection.return_value
            assert connection.mock_calls[0][2]["host"] == host
            assert connection.mock_calls[0][2]["port"] == port
            
@pytest.mark.asyncio
async def test_dynet_connect_failure():
    host = "1.2.3.4"
    port = 5678
    broadcaster = Mock()
    on_connect = Mock()
    on_disconnect = Mock()
    loop = asyncio.get_event_loop()
    with patch("dynalite_lib.dynet.DynetConnection") as dyn_connection:
        dynet = Dynet(host, port, broadcaster, on_connect, on_disconnect, loop)
        assert dynet._conn() is dyn_connection.return_value
        connection = Mock()
        connection.side_effect = ValueError('Boom!')
        with patch.object(loop, "create_connection", async_mock(connection)):
            with patch.object(loop, "call_later") as later_mock:
                await dynet.connect()
                connection.assert_called_once()
                assert connection.mock_calls[0][1][0]() is dyn_connection.return_value
                assert connection.mock_calls[0][2]["host"] == host
                assert connection.mock_calls[0][2]["port"] == port
                LOGGER.error("call_later calls = %s", later_mock.mock_calls)
                assert later_mock.mock_calls[2][1][1] == dynet.connect@pytest.mark.asyncio

async def test_dynet_receive():
    host = "1.2.3.4"
    port = 5678
    broadcaster = Mock()
    on_connect = Mock()
    on_disconnect = Mock()
    loop = asyncio.get_event_loop()
    with patch("dynalite_lib.dynet.DynetConnection") as dyn_connection:
        dynet = Dynet(host, port, broadcaster, on_connect, on_disconnect, loop)
        assert dynet._conn() is dyn_connection.return_value
        connection = Mock()
        connection.side_effect = ValueError('Boom!')
        with patch.object(loop, "create_connection", async_mock(connection)):
            with patch.object(loop, "call_later") as later_mock:
                await dynet.connect()
                connection.assert_called_once()
                assert connection.mock_calls[0][1][0]() is dyn_connection.return_value
                assert connection.mock_calls[0][2]["host"] == host
                assert connection.mock_calls[0][2]["port"] == port
                LOGGER.error("call_later calls = %s", later_mock.mock_calls)
                assert later_mock.mock_calls[2][1][1] == dynet.connect
                
            
            
        