#!/usr/bin/env python3
import time
# Import classes
from Dynalite import Dynalite

HOST = '10.7.3.212'  # Standard loopback interface address (localhost)
PORT = 12345        # Port to listen on (non-privileged ports are > 1023)

def handleEvent(event):
    print(event)
    return True

# Create an object
dynet = Dynalite.Dynalite(HOST, PORT)

dynet.connect()
time.sleep(0.5)
dynet.setPreset(8,9,2)
time.sleep(2)
dynet.setPreset(8,4,2)
time.sleep(2)
dynet.reqPreset(1)
time.sleep(2)
dynet.reqPreset(2)
time.sleep(2)
dynet.reqPreset(3)
time.sleep(2)
dynet.reqPreset(4)
time.sleep(2)
dynet.reqPreset(5)
time.sleep(2)
dynet.reqPreset(6)
time.sleep
print(dynet.areaPresets)
