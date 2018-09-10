"""Definition of an Dynalite Areas"""

from .const import Max, TextDescriptions
from .elements import Element, Elements
from .message import add_message_handler


class Area(Element):
    """Class representing a Light"""
    def __init__(self, index, dynalite):
        super().__init__(index, dynalite)
        self.status = 0

    def turn_off(self):
        """(Helper) Turn off lights"""
        #self._dynalite.send(pf_encode(self._index))

    def turn_on(self, brightness=100, time=0):
        """(Helper) Turn on light"""
        if brightness == 100:
            pass
            #self._dynalite.send(pn_encode(self._index))
        else:
            pass
            #self._dynalite.send(pc_encode(self._index, 9, brightness, time))

    def toggle(self):
        """(Helper) Toggle light"""
        #self._dynalite.send(pt_encode(self._index))


class Areas(Elements):
    """Handling for multiple lights"""
    def __init__(self, dynalite):
        super().__init__(dynalite, Area, Max.AREAS.value)
        #add_message_handler('PC', self._pc_handler)
        #add_message_handler('PS', self._ps_handler)

    def sync(self):
        """Retrieve lights from ElkM1"""
        #for i in range(4):
            #self.dynalite.send(ps_encode(i))
        self.get_descriptions(TextDescriptions.AREAS.value)

    # # pylint: disable=unused-argument
    # def _pc_handler(self, housecode, index, light_level):
    #     self.elements[index].setattr('status', light_level, True)
    #
    # def _ps_handler(self, bank, statuses):
    #     for i in range(bank*64, (bank+1)*64):
    #         self.elements[i].setattr('status', statuses[i-bank*64], True)
