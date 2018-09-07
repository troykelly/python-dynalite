"""
Constants used across package
"""

from enum import Enum


class Max(Enum):
    """Max number of elements on the panel"""
    AREAS = 255
    PRESETS = 64

class OpcodeType(Enum):
    """Types of Dyney Opcodes"""
    PRESET_1 = 0
    PRESET_2 = 1
    PRESET_3 = 2
    PRESET_4 = 3
    OFF = 4
    DECREASE_LEVEL = 5
    INCREMENT_LEVEL = 6
    PROGRAM_OUT_CURRENT_PRESET = 8
    PRESET_5 = 10
    PRESET_6 = 11
    PRESET_7 = 12
    PRESET_8 = 13
    RESET_TO_PRESET = 15
    DMX = 16
    PE_CONTROL = 17
    AREA_JOIN_LEVEL = 20
    LOCK_CONTROL_PANELS = 21
    ENABLE_CONTROL_PANELS = 22
    PANIC = 23
    UNPANIC = 24
    SET_AREA_LINK = 32
    CLEAR_AREA_LINK = 33
    REQUEST_AREA_LINKS = 35
    OCCUPANCY_CONTROL = 49
    AREA_JOIN_MASK = 64
    PANEL_LIGHTING = 72
    REQUEST_AREA_TEMP = 73
    RAMP_ALL_CHANNELS = 95
    REPORT_CHANNEL_LEVEL = 96
    REQUEST_CHANNEL_LEVEL = 97
    REPORT_PRESET = 98
    REQUEST_PRESET = 99
    PRESET_OFFSET = 100
    SAVE_CURRENT_PRESET = 102
    RESTORE_CURRENT_PRESET = 103
    TURN_ALL_AREAS_OFF = 104
    TURN_ALL_AREAS_ON = 105
    TOGGLE_CHANNEL_STATE = 112
    START_FADING_FAST = 113
    START_FADING_MED = 114
    START_FADING_SLOW = 115
    STOP_FADING = 118
    START_FADING_ALL = 121
    STOP_FADING_ALL = 122
    PROGRAM_TOGGLE_PRESET = 125


class PanelLightingType(Enum):
    """Types of Dyney Opcodes"""
    INDICATOR = 1
    BACKLIGHT = 2


# Map to convert message code to descriptive string
MESSAGE_MAP = {
    0: 'First preset in bank',
    1: 'Second preset in bank',
    2: 'Third preset in bank',
    3: 'Forth preset in bank',
    4: 'Area off',
    5: 'Decrease area level',
    6: 'Increment area level',
    8: 'Program current preset',
    10: 'Fifth preset in bank',
    11: 'Sixth preset in bank',
    12: 'Seventh preset in bank',
    13: 'Eighth preset in bank',
    15: 'Reset to preset',
    16: 'DMX Control',
    17: 'PE Detector Control',
    20: 'Area join level',
    21: 'Control panels lock',
    22: 'Control panels unlock',
    23: 'Panic',
    24: 'Unpanic',
    32: 'Set area link',
    33: 'Clear area link',
    35: 'Request area links',
    49: 'Occupancy/motion detection control',
    64: 'Area join mask',
    72: 'Set panel lighting',
    73: 'Request area temps',
    95: 'Ramp all channels above zero',
    96: 'Report channel level',
    97: 'Request channel level',
    98: 'Report area preset',
    99: 'Request area preset',
    100: 'Preset offset',
    102: 'Save current preset',
    103: 'Restore current preset',
    104: 'Turn all areas off',
    105: 'Turn all areas on',
    112: 'Toggel channel state',
    113: 'Start fading fast',
    114: 'Start fading medium',
    115: 'Start fading slow',
    118: 'Stop fading',
    121: 'Start fading all',
    122: 'Stop fading all',
    125: 'Program toggle preset',
}
