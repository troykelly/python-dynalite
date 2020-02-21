import pytest
from asynctest import CoroutineMock
import asyncio
from unittest.mock import patch, Mock

from dynalite_lib.dynet import DynetConnection

def test_dynet_connection_con_made():
    con_made = Mock()
    con_lost = Mock()
    recv_handle = Mock()
    con_pause = Mock()
    con_resume = Mock()
    transport = Mock()
    dyn_con = DynetConnection(connectionMade=con_made, connectionLost=con_lost, receiveHandler=recv_handle, connectionPause=con_pause, connectionResume=con_resume)
    dyn_con.connection_made(transport)
    con_made.assert_called_once_with(transport)
    con_made.reset_mock()
    con_lost.assert_not_called()
    recv_handle.assert_not_called()
    con_pause.assert_not_called()
    con_resume.assert_not_called()
    loop = Mock()
    dyn_con_loop = DynetConnection(connectionMade=con_made, connectionLost=con_lost, receiveHandler=recv_handle, connectionPause=con_pause, connectionResume=con_resume, loop=loop)
    dyn_con_loop.connection_made(transport)
    con_made.assert_called_once_with(transport)
    con_lost.assert_not_called()
    recv_handle.assert_not_called()
    con_pause.assert_not_called()
    con_resume.assert_not_called()
    loop.create_task.assert_called_once_with(con_made(transport))

def test_dynet_connection_con_lost():
    con_made = Mock()
    con_lost = Mock()
    recv_handle = Mock()
    con_pause = Mock()
    con_resume = Mock()
    exc = Mock()
    dyn_con = DynetConnection(connectionMade=con_made, connectionLost=con_lost, receiveHandler=recv_handle, connectionPause=con_pause, connectionResume=con_resume)
    dyn_con.connection_lost(exc=exc)
    con_made.assert_not_called()
    con_lost.assert_called_once_with(exc)
    con_lost.reset_mock()
    recv_handle.assert_not_called()
    con_pause.assert_not_called()
    con_resume.assert_not_called()
    loop = Mock()
    dyn_con_loop = DynetConnection(connectionMade=con_made, connectionLost=con_lost, receiveHandler=recv_handle, connectionPause=con_pause, connectionResume=con_resume, loop=loop)
    dyn_con_loop.connection_lost(exc)
    con_made.assert_not_called()
    con_lost.assert_called_once_with(exc)
    recv_handle.assert_not_called()
    con_pause.assert_not_called()
    con_resume.assert_not_called()
    loop.create_task.assert_called_once_with(con_lost(exc))

def test_dynet_connection_con_paused():
    con_made = Mock()
    con_lost = Mock()
    recv_handle = Mock()
    con_pause = Mock()
    con_resume = Mock()
    dyn_con = DynetConnection(connectionMade=con_made, connectionLost=con_lost, receiveHandler=recv_handle, connectionPause=con_pause, connectionResume=con_resume)
    dyn_con.pause_writing()
    con_made.assert_not_called()
    con_lost.assert_not_called()
    recv_handle.assert_not_called()
    con_pause.assert_called_once_with()
    con_pause.reset_mock()
    con_resume.assert_not_called()
    loop = Mock()
    dyn_con_loop = DynetConnection(connectionMade=con_made, connectionLost=con_lost, receiveHandler=recv_handle, connectionPause=con_pause, connectionResume=con_resume, loop=loop)
    dyn_con_loop.pause_writing()
    con_made.assert_not_called()
    con_lost.assert_not_called()
    recv_handle.assert_not_called()
    con_pause.assert_called_once_with()
    con_resume.assert_not_called()
    loop.create_task.assert_called_once_with(con_pause())

def test_dynet_connection_resume():
    con_made = Mock()
    con_lost = Mock()
    recv_handle = Mock()
    con_pause = Mock()
    con_resume = Mock()
    dyn_con = DynetConnection(connectionMade=con_made, connectionLost=con_lost, receiveHandler=recv_handle, connectionPause=con_pause, connectionResume=con_resume)
    dyn_con.resume_writing()
    con_made.assert_not_called()
    con_lost.assert_not_called()
    recv_handle.assert_not_called()
    con_pause.assert_not_called()
    con_resume.assert_called_once_with()
    con_resume.reset_mock()
    loop = Mock()
    dyn_con_loop = DynetConnection(connectionMade=con_made, connectionLost=con_lost, receiveHandler=recv_handle, connectionPause=con_pause, connectionResume=con_resume, loop=loop)
    dyn_con_loop.resume_writing()
    con_made.assert_not_called()
    con_lost.assert_not_called()
    recv_handle.assert_not_called()
    con_pause.assert_not_called()
    con_resume.assert_called_once_with()
    loop.create_task.assert_called_once_with(con_resume())

def test_dynet_connection_data_recv():
    con_made = Mock()
    con_lost = Mock()
    recv_handle = Mock()
    con_pause = Mock()
    con_resume = Mock()
    data = Mock()
    dyn_con = DynetConnection(connectionMade=con_made, connectionLost=con_lost, receiveHandler=recv_handle, connectionPause=con_pause, connectionResume=con_resume)
    dyn_con.data_received(data)
    con_made.assert_not_called()
    con_lost.assert_not_called()
    recv_handle.assert_called_once_with(data)
    recv_handle.reset_mock()
    con_pause.assert_not_called()
    con_resume.assert_not_called()
    loop = Mock()
    dyn_con_loop = DynetConnection(connectionMade=con_made, connectionLost=con_lost, receiveHandler=recv_handle, connectionPause=con_pause, connectionResume=con_resume, loop=loop)
    dyn_con_loop.data_received(data)
    con_made.assert_not_called()
    con_lost.assert_not_called()
    recv_handle.assert_called_once_with(data)
    con_pause.assert_not_called()
    con_resume.assert_not_called()
    loop.create_task.assert_called_once_with(recv_handle(data))

def test_dynet_connection_eof():
    con_made = Mock()
    con_lost = Mock()
    recv_handle = Mock()
    con_pause = Mock()
    con_resume = Mock()
    dyn_con = DynetConnection(connectionMade=con_made, connectionLost=con_lost, receiveHandler=recv_handle, connectionPause=con_pause, connectionResume=con_resume)
    dyn_con.eof_received()
    con_made.assert_not_called()
    con_lost.assert_not_called()
    recv_handle.assert_not_called()
    con_pause.assert_not_called()
    con_resume.assert_not_called()
