import pytest
from asynctest import CoroutineMock
import asyncio
from unittest.mock import patch, Mock
import logging

from dynalite_lib.dynet import DynetControl, OpcodeType

LOGGER = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_dynet_control_area_preset():
    expected_bank = {1: 0, 14: 1}
    expected_opcode = {1: OpcodeType.PRESET_1, 14: OpcodeType.PRESET_6}
    loop = asyncio.get_event_loop()
    area = 3
    fade = 11.0 # equals to 550 in 0.02 increments = 2*256 + 38
    expected_fade_low = 38
    expected_fade_high = 2 
    area_def = Mock()
    for preset in [1,14]:
        dynet = Mock()
        dyn_control = DynetControl(dynet, loop, area_def)
        await dyn_control.areaPreset(area, preset, fade)
        dynet.write.assert_called_once()
        packet = dynet.write.mock_calls[0][1][0]
        assert packet.sync == 0x1c
        assert packet.area == area
        assert packet.data == [expected_fade_low, expected_fade_high, expected_bank[preset]]
        assert packet.command == expected_opcode[preset].value
        assert packet.join == 0xff
        assert packet.shouldRun is None

@pytest.mark.asyncio
async def test_dynet_control_set_channel():
    set_level = {1: 0.0, 14: 1.0} # turn off channel 1 and on channel 14
    expected_target_level = {1: 255, 14: 1}
    expected_bank = {1: 0xff, 14: 2}
    expected_opcode = {1: OpcodeType.SET_CHANNEL_1_TO_LEVEL_WITH_FADE, 14: OpcodeType.SET_CHANNEL_2_TO_LEVEL_WITH_FADE}
    set_fade = {1: 0.5, 14: 10.0}
    expected_fade = {1: 25, 14: 0xff}
    loop = asyncio.get_event_loop()
    area = 3
    area_def = Mock()
    for channel in [1,14]:
        dynet = Mock()
        dyn_control = DynetControl(dynet, loop, area_def)
        with patch.object(dyn_control, "request_channel_level") as req_chan_lvl:
            await dyn_control.setChannel(area, channel, set_level[channel], set_fade[channel])
            dynet.write.assert_called_once()
            packet = dynet.write.mock_calls[0][1][0]
            assert packet.sync == 0x1c
            assert packet.area == area
            assert packet.data == [expected_target_level[channel], expected_bank[channel], expected_fade[channel]]
            assert packet.command == expected_opcode[channel].value
            assert packet.join == 0xff
            assert packet.shouldRun is None
            req_chan_lvl.assert_called_once_with(area=area, channel=channel)

@pytest.mark.asyncio
async def test_dynet_control_req_chan_level():
    loop = asyncio.get_event_loop()
    area = 3
    channel = 5
    should_run = Mock()
    area_def = Mock()
    dynet = Mock()
    dyn_control = DynetControl(dynet, loop, area_def)
    await dyn_control.request_channel_level(area, channel, should_run)
    dynet.write.assert_called_once()
    packet = dynet.write.mock_calls[0][1][0]
    assert packet.sync == 0x1c
    assert packet.area == area
    assert packet.data == [channel - 1, 0, 0]
    assert packet.command == OpcodeType.REQUEST_CHANNEL_LEVEL.value
    assert packet.join == 0xff
    assert packet.shouldRun is should_run

@pytest.mark.asyncio
async def test_dynet_control_stop_chan_fade():
    loop = asyncio.get_event_loop()
    area = 3
    area_def = Mock()
    channel = 5
    dynet = Mock()
    dyn_control = DynetControl(dynet, loop, area_def)
    await dyn_control.stop_channel_fade(area, channel)
    dynet.write.assert_called_once()
    packet = dynet.write.mock_calls[0][1][0]
    assert packet.sync == 0x1c
    assert packet.area == area
    assert packet.data == [channel - 1, 0, 0]
    assert packet.command == OpcodeType.STOP_FADING.value
    assert packet.join == 0xff
    assert packet.shouldRun is None

@pytest.mark.asyncio
async def test_dynet_control_area_off():
    expected_fade = {1.0: 10, 100.0: 255, -1.0: 0}
    loop = asyncio.get_event_loop()
    area = 3
    area_def = Mock()
    for fade in expected_fade:
        dynet = Mock()
        dyn_control = DynetControl(dynet, loop, area_def)
        await dyn_control.areaOff(area, fade)
        dynet.write.assert_called_once()
        packet = dynet.write.mock_calls[0][1][0]
        assert packet.sync == 0x1c
        assert packet.area == area
        assert packet.data == [255, 0, expected_fade[fade]]
        assert packet.command == OpcodeType.TURN_ALL_AREAS_OFF.value
        assert packet.join == 0xff
        assert packet.shouldRun is None

@pytest.mark.asyncio
async def test_dynet_control_req_area_preset():
    loop = asyncio.get_event_loop()
    area = 3
    should_run = Mock()
    area_def = Mock()
    dynet = Mock()
    dyn_control = DynetControl(dynet, loop, area_def)
    await dyn_control.request_area_preset(area, should_run)
    dynet.write.assert_called_once()
    packet = dynet.write.mock_calls[0][1][0]
    assert packet.sync == 0x1c
    assert packet.area == area
    assert packet.data == [0, 0, 0]
    assert packet.command == OpcodeType.REQUEST_PRESET.value
    assert packet.join == 0xff
    assert packet.shouldRun is should_run

