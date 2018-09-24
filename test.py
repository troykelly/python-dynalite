#!/usr/bin/env python3
import json
import logging
import asyncio
from dynalite_lib import Dynalite

logging.basicConfig(level=logging.DEBUG,
                    format="[%(asctime)s] %(name)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s")
LOG = logging.getLogger(__name__)

OPTIONS_FILE = 'test/options.json'

loop = asyncio.get_event_loop()


def handleEvent(event):
    LOG.info("Received Event: %s" % event.eventType)
    LOG.debug(event.toJson())


if __name__ == '__main__':
    with open(OPTIONS_FILE, 'r') as f:
        cfg = json.load(f)

    dynalite = Dynalite(config=cfg, loop=loop)

    bcstr = dynalite.addListener(listenerFunction=handleEvent)
    bcstr.monitorEvent('*')

    dynalite.start()
    loop.run_forever()
