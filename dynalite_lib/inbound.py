"""
@ Author      : Troy Kelly
@ Date        : 23 Sept 2018
@ Description : Philips Dynalite Library - Unofficial interface for Philips Dynalite over RS485

@ Notes:        Requires a RS485 to IP gateway (Do not use the Dynalite one - use something cheaper)
"""

from .event import DynetEvent
from .const import (
    EVENT_PRESET,
    EVENT_CHANNEL,
    EVENT_REQPRESET,
    CONF_AREA,
    CONF_FADE,
    CONF_PRESET,
    CONF_CHANNEL,
    CONF_JOIN,
    CONF_STATE,
    CONF_STATE_ON,
    CONF_DIR_IN,
    CONF_ACTION,
    CONF_ACTION_REPORT,
    CONF_ACTION_CMD,
    CONF_TRGT_LEVEL,
    CONF_ACT_LEVEL,
    CONF_ALL,
)


class DynetInbound(object):
    def __init__(self):
        self._logger = None

    def preset(self, packet):
        if packet.command > 3:
            packet.preset = packet.command - 6
        else:
            packet.preset = packet.command
        packet.preset = (packet.preset + (packet.data[2] * 8)) + 1
        packet.fade = (packet.data[0] + (packet.data[1] * 256)) * 0.02
        return DynetEvent(
            eventType=EVENT_PRESET,
            message=(
                "Area %d Preset %d Fade %d seconds."
                % (packet.area, packet.preset, packet.fade)
            ),
            data={
                CONF_AREA: packet.area,
                CONF_PRESET: packet.preset,
                CONF_FADE: packet.fade,
                CONF_JOIN: packet.join,
                CONF_STATE: CONF_STATE_ON,
            },
            direction=CONF_DIR_IN,
        )

    def preset_1(self, packet):
        return self.preset(packet)

    def preset_2(self, packet):
        return self.preset(packet)

    def preset_3(self, packet):
        return self.preset(packet)

    def preset_4(self, packet):
        return self.preset(packet)

    def preset_5(self, packet):
        return self.preset(packet)

    def preset_6(self, packet):
        return self.preset(packet)

    def preset_7(self, packet):
        return self.preset(packet)

    def preset_8(self, packet):
        return self.preset(packet)

    def request_preset(self, packet):
        return DynetEvent(
            eventType=EVENT_REQPRESET,
            message=("Request Area %d preset" % (packet.area)),
            data={CONF_AREA: packet.area, CONF_JOIN: packet.join},
            direction=CONF_DIR_IN,
        )

    def report_preset(self, packet):
        packet.preset = packet.data[0] + 1
        return DynetEvent(
            eventType=EVENT_PRESET,
            message=("Current Area %d Preset is %d" % (packet.area, packet.preset)),
            data={
                CONF_AREA: packet.area,
                CONF_PRESET: packet.preset,
                CONF_JOIN: packet.join,
                CONF_STATE: CONF_STATE_ON,
            },
            direction=CONF_DIR_IN,
        )

    def linear_preset(self, packet):
        packet.preset = packet.data[0] + 1
        packet.fade = (packet.data[1] + (packet.data[2] * 256)) * 0.02
        return DynetEvent(
            eventType=EVENT_PRESET,
            message=(
                "Area %d Preset %d Fade %d seconds."
                % (packet.area, packet.preset, packet.fade)
            ),
            data={
                CONF_AREA: packet.area,
                CONF_PRESET: packet.preset,
                CONF_FADE: packet.fade,
                CONF_JOIN: packet.join,
                CONF_STATE: CONF_STATE_ON,
            },
            direction=CONF_DIR_IN,
        )

    def report_channel_level(self, packet):
        channel = packet.data[0] + 1
        target_level = packet.data[1]
        actual_level = packet.data[2]
        return DynetEvent(
            eventType=EVENT_CHANNEL,
            message=(
                "Area %d Channel %d Target Level %d Actual Level %d."
                % (packet.area, channel, target_level, actual_level)
            ),
            data={
                CONF_AREA: packet.area,
                CONF_CHANNEL: channel,
                CONF_ACTION: CONF_ACTION_REPORT,
                CONF_TRGT_LEVEL: target_level,
                CONF_ACT_LEVEL: actual_level,
                CONF_JOIN: packet.join,
                CONF_STATE: CONF_STATE_ON,
            },
            direction=CONF_DIR_IN,
        )

    def set_channel_x_to_level_with_fade(self, packet, channel_offset):
        channel = ((packet.data[1] + 1) % 256) * 4 + channel_offset
        target_level = packet.data[0]
        return DynetEvent(
            eventType=EVENT_CHANNEL,
            message=(
                "Area %d Channel %d Target Level %d"
                % (packet.area, channel, target_level)
            ),
            data={
                CONF_AREA: packet.area,
                CONF_CHANNEL: channel,
                CONF_ACTION: CONF_ACTION_CMD,
                CONF_TRGT_LEVEL: target_level,
                CONF_JOIN: packet.join,
                CONF_STATE: CONF_STATE_ON,
            },
            direction=CONF_DIR_IN,
        )

    def set_channel_1_to_level_with_fade(self, packet):
        return self.set_channel_x_to_level_with_fade(packet, 1)

    def set_channel_2_to_level_with_fade(self, packet):
        return self.set_channel_x_to_level_with_fade(packet, 2)

    def set_channel_3_to_level_with_fade(self, packet):
        return self.set_channel_x_to_level_with_fade(packet, 3)

    def set_channel_4_to_level_with_fade(self, packet):
        return self.set_channel_x_to_level_with_fade(packet, 4)

    def request_channel_level(self, packet):
        return

    def stop_fading(self, packet):
        channel = packet.data[0] + 1
        if channel == 256:  # all channels in area
            channel = CONF_ALL
        return DynetEvent(
            eventType=EVENT_CHANNEL,
            message=("Area %d Channel %s" % (packet.area, channel)),
            data={
                CONF_AREA: packet.area,
                CONF_CHANNEL: channel,
                CONF_ACTION: CONF_ACTION_CMD,
                CONF_JOIN: packet.join,
                CONF_STATE: CONF_STATE_ON,
            },
            direction=CONF_DIR_IN,
        )

    def fade_channel_area_to_preset(self, packet):
        channel = packet.data[0] + 1
        packet.preset = packet.data[1] + 1
        packet.fade = packet.data[2] * 0.02
        if channel == 256:  # all channels in area
            return DynetEvent(
                eventType=EVENT_PRESET,
                message=(
                    "Current Area %d Preset is %d fade %s"
                    % (packet.area, packet.preset, packet.fade)
                ),
                data={
                    CONF_AREA: packet.area,
                    CONF_PRESET: packet.preset,
                    CONF_FADE: packet.fade,
                    CONF_JOIN: packet.join,
                    CONF_STATE: CONF_STATE_ON,
                },
                direction=CONF_DIR_IN,
            )
        else:
            return DynetEvent(
                eventType=EVENT_CHANNEL,
                message=(
                    "Area %d Channel %s preset %s fade %s"
                    % (packet.area, channel, packet.preset, packet.fade)
                ),
                data={
                    CONF_AREA: packet.area,
                    CONF_CHANNEL: channel,
                    CONF_FADE: packet.fade,
                    CONF_ACTION: CONF_ACTION_CMD,
                    CONF_PRESET: packet.preset,
                    CONF_JOIN: packet.join,
                    CONF_STATE: CONF_STATE_ON,
                },
                direction=CONF_DIR_IN,
            )
