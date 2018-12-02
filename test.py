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
dynalite = None


def handleEvent(event=None, dynalite=None):
    LOG.debug(event.toJson())


def handleConnect(event=None, dynalite=None):
    LOG.info("Connected to Dynalite")
    # dynalite.devices['area'][8].preset[10].turnOn()
    dynalite.state()


if __name__ == '__main__':
    with open(OPTIONS_FILE, 'r') as f:
        cfg = json.load(f)

    dynalite = Dynalite(config=cfg, loop=loop)

    bcstr = dynalite.addListener(listenerFunction=handleEvent)
    bcstr.monitorEvent('*')

    onConnect = dynalite.addListener(listenerFunction=handleConnect)
    onConnect.monitorEvent('CONNECTED')

    dynalite.start()
    loop.run_forever()
