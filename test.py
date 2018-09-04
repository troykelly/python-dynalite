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
dynalite = Dynalite(HOST, PORT)

dynalite.connect(handleEvent)
time.sleep(0.5)
dynalite.setPreset(8,1,2)
time.sleep(2)
dynalite.setPreset(8,4,2)
time.sleep(2)
dynalite.reqPreset(1)
time.sleep(2)
dynalite.reqPreset(2)
time.sleep(2)
dynalite.reqPreset(3)
time.sleep(2)
dynalite.reqPreset(4)
time.sleep(2)
dynalite.reqPreset(5)
time.sleep(2)
dynalite.reqPreset(6)
