"""
@ Author      : Troy Kelly
@ Date        : 23 Sept 2018
@ Description : Philips Dynalite Library - Unofficial interface for Philips Dynalite over RS485
"""

from enum import Enum

CONF_ACT_LEVEL = "actual_level"
CONF_ACTION = "action"
CONF_ACTION_CMD = "cmd"
CONF_ACTION_REPORT = "report"
CONF_ACTIVE = "active"
CONF_ACTIVE_ON = "on"
CONF_ACTIVE_OFF = "off"
CONF_ACTIVE_INIT = "init"
CONF_ALL = "ALL"
CONF_AREA = "area"
CONF_CHANNEL = "channel"
CONF_AUTO_DISCOVER = "autodiscover"
CONF_DEFAULT = "default"
CONF_DIR_IN = "IN"
CONF_FADE = "fade"
CONF_HOST = "host"
CONF_JOIN = "join"
CONF_LEVEL = "level"
CONF_LOGLEVEL = "log_level"
CONF_LOGFORMATTER = "log_formatter"
CONF_NAME = "name"
CONF_NODEFAULT = "nodefault"
CONF_PORT = "port"
CONF_POLLTIMER = "polltimer"
CONF_PRESET = "preset"
CONF_STATE = "state"
CONF_STATE_ON = "ON"
CONF_STATE_OFF = "OFF"
CONF_TRGT_LEVEL = "target_level"

EVENT_CHANNEL = "CHANNEL"
EVENT_CONFIGURED = "CONFIGURED"
EVENT_CONNECTED = "CONNECTED"
EVENT_DISCONNECTED = "DISCONNECTED"
EVENT_NEWPRESET = "NEWPRESET"
EVENT_NEWCHANNEL = "NEWCHANNEL"
EVENT_PRESET = "PRESET"
EVENT_REQPRESET = "REQPRESET"

# if a request for channel level didn't get acknowledge, when to retry (subsequent retries will be 2x, 4x, 8x, etc.)
INITIAL_RETRY_DELAY = 1
# initial retry timeout for the beginning, since it could take time to settle on Dynet for large environments
STARTUP_RETRY_DELAY = 60
# Minimal retry frequency in seconds - default 1 hour, so if something never answers, it will be pinged once an hour XXX consider changing
MAXIMUM_RETRY_DELAY = 60 * 60
# no retry value for delay
NO_RETRY_DELAY_VALUE = -1

class SyncType(Enum):
    """Types of Sync Code."""

    LOGICAL = 28  # 0x1c
    DEVICE = 92  # 0x5c
    DEBUG_MSG = 108  # 0x6c

    @classmethod
    def has_value(cls, value):
        """Return the item that has this as a value."""
        return any(value == item.value for item in cls)


class OpcodeType(Enum):
    """Types of Dynet Opcodes."""

    PRESET_1 = 0
    PRESET_2 = 1
    PRESET_3 = 2
    PRESET_4 = 3
    RECALL_OFF = 4
    DECREASE_LEVEL = 5
    INCREMENT_LEVEL = 6
    ENTER_PROGRAM_MODE = 7
    PROGRAM_OUT_CURRENT_PRESET = 8
    PROGRAM_LEVELS_PRESET = 9
    PRESET_5 = 10
    PRESET_6 = 11
    PRESET_7 = 12
    PRESET_8 = 13
    RESET_TO_PRESET = 15
    DMX = 16
    PE_CONTROL = 17
    SET_PE_MIN = 18
    SET_PE_MAX = 19
    AREA_JOIN_LEVEL = 20
    LOCK_CONTROL_PANELS = 21
    ENABLE_CONTROL_PANELS = 22
    PANIC = 23
    UNPANIC = 24
    SET_PE_SPEED = 25
    DISABLE_LIGHT_LEVEL = 26
    ENABLE_LIGHT_LEVEL = 27
    DISABLE_LIGHT_LEVEL_PRESETS = 28
    ENABLE_LIGHT_LEVEL_PRESETS = 29
    DECREMENT_PRESET = 30
    INCREMENT_PRESET = 31
    SET_AREA_LINK = 32
    CLEAR_AREA_LINK = 33
    REPLY_AREA_LINK = 34
    REQUEST_AREA_LINKS = 35
    SET_FADE_TIME = 40
    SUSPEND_OCCUPANCY_PRESETS = 44
    RESUME_OCCUPANCY_PRESETS = 45
    MOTION_ACTIVITY_SYNC = 46
    OCCUPANCY_NOTIFIER = 47
    SUSPEND_OCCUPANCY_SYNC_PRESETS = 48
    SUSPEND_OCCUPANCY_DETECTION_PRESETS = 49
    DISABLE_OCCUPANCY_PRESET = 58
    ENABLE_OCCUPANCY_PRESET = 59
    DISABLE_OCCUPANCY_ALL = 60
    ENABLE_OCCUPANCY_ALL = 61
    AREA_JOIN_MASK = 64
    PANEL_LIGHTING = 72
    REQUEST_AREA_TEMP = 73
    RAMP_ALL_CHANNELS = 95
    REPORT_CHANNEL_LEVEL = 96
    REQUEST_CHANNEL_LEVEL = 97
    REPORT_PRESET = 98
    REQUEST_PRESET = 99
    PRESET_OFFSET = 100
    LINEAR_PRESET = 101
    SAVE_CURRENT_PRESET = 102
    RESTORE_CURRENT_PRESET = 103
    TURN_ALL_AREAS_OFF = 104
    TURN_ALL_AREAS_ON = 105
    FADE_CHANNEL_AREA_TO_PRESET = 107
    TOGGLE_CHANNEL_STATE = 112
    START_FADING_FAST = 113
    START_FADING_MED = 114
    START_FADING_SLOW = 115
    STOP_FADING = 118
    START_FADING_ALL = 121
    STOP_FADING_ALL = 122
    PROGRAM_TOGGLE_PRESET = 125
    SET_CHANNEL_1_TO_LEVEL_WITH_FADE = 128
    SET_CHANNEL_2_TO_LEVEL_WITH_FADE = 129
    SET_CHANNEL_3_TO_LEVEL_WITH_FADE = 130
    SET_CHANNEL_4_TO_LEVEL_WITH_FADE = 131

    @classmethod
    def has_value(cls, value):
        """Return the item that has this as a value."""
        return any(value == item.value for item in cls)
