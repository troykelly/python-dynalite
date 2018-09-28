"""
@ Author      : Troy Kelly
@ Date        : 23 Sept 2018
@ Description : Philips Dynalite Library - Unofficial interface for Philips Dynalite over RS485

@ Notes:        Requires a RS485 to IP gateway (Do not use the Dynalite one - use something cheaper)
"""

import json

class DynetEvent(object):

    def __init__(self, eventType=None, message=None, data={}, direction=None):
        self.eventType = eventType.upper() if eventType else None
        self.msg = message
        self.data = data
        self.direction = direction

    def toJson(self):
        return json.dumps(self.__dict__)

    def __repr__(self):
        return json.dumps(self.__dict__)


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
        return DynetEvent(eventType='PRESET', message=("Area %d Preset %d Fade %d seconds." % (packet.area, packet.preset, packet.fade)), data={'area': packet.area, 'preset': packet.preset, 'fade': packet.fade, 'join': packet.join}, direction="IN")

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
        return DynetEvent(eventType='REQPRESET', message=("Request Area %d preset" % (packet.area)), data={'area': packet.area, 'join': packet.join}, direction="IN")

    def report_preset(self, packet):
        packet.preset = packet.data[0] + 1
        # packet.fade = (packet.data[1] + (packet.data[2] * 256)) * 0.02
        return DynetEvent(eventType='PRESET', message=("Current Area %d Preset is %d" % (packet.area, packet.preset)), data={'area': packet.area, 'preset': packet.preset, 'join': packet.join}, direction="IN")

    def linear_preset(self, packet):
        packet.preset = packet.data[0] + 1
        packet.fade = (packet.data[1] + (packet.data[2] * 256)) * 0.02
        return DynetEvent(eventType='PRESET', message=("Area %d Preset %d Fade %d seconds." % (packet.area, packet.preset, packet.fade)), data={'area': packet.area, 'preset': packet.preset, 'fade': packet.fade, 'join': packet.join}, direction="IN")
