"""Utility functions"""

import logging
import ssl
from .message import add_message_handler, sd_encode

LOG = logging.getLogger(__name__)

# pylint: disable=invalid-name
get_descriptions_in_progress = {}
sync_handlers = []


def add_sync_handler(sync_handler):
    """Register a fn that synchronizes part of the panel."""
    sync_handlers.append(sync_handler)


def call_sync_handlers():
    """Invoke the synchronization handlers."""
    LOG.debug("Synchronizing panel...")
    for sync_handler in sync_handlers:
        sync_handler()
