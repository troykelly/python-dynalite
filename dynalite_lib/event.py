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
