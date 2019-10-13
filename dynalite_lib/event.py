"""Class to represent an event on the Dynet network."""
import json


class DynetEvent(object):
    """Class to represent an event on the Dynet network."""

    def __init__(self, eventType=None, message=None, data={}, direction=None):
        """Initialize the event."""
        self.eventType = eventType.upper() if eventType else None
        self.msg = message
        self.data = data
        self.direction = direction

    def toJson(self):
        """Convert to JSON."""
        return json.dumps(self.__dict__)

    def __repr__(self):
        """Print the event."""
        return json.dumps(self.__dict__)
