import socket
import time
import threading

class dynalite:
    def __init__(self, host, port):
        ''' Constructor for this class. '''
        self.host = host
        self.port = port
        self.messagesize = 7    # How many bytes in a message
        self.template = bytearray([28, 0, 0, 0, 0, 0, 0])
        self.connected = False
        self.timeout = 900

    def connect(self, handler):
        self.handler = handler
        thread = threading.Thread(target=self.socketReceive, args=())
        thread.daemon = False                            # Daemonize thread
        thread.start()                                  # Start the execution

    def connectSocket(self):
        self.connected = False

        while not self.connected:
            try:
                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.s.connect((self.host, self.port))
                self.s.settimeout(self.timeout)
                self.connected = True
                self.handler({"type": "connection", "status": "connected",
                              "host": self.host, "port": self.port})
            except (socket.error, socket.timeout) as e:
                self.handler({"type": "connection", "status": "failed",
                              "host": self.host, "port": self.port})
                time.sleep(2)
        return True

    def socketReceive(self):
        if self.connected is not True:
            self.connectSocket()
        while True:
            try:
                buf = self.s.recv(1024)
                self.handler(self.process_message(buf))
            except (socket.error, socket.timeout) as e:
                self.connectSocket()

    def getHost(self):
        return self.host

    def getPort(self):
        return self.port

    def getMessageSize(self):
        return self.messagesize

    def getTemplate(self):
        return self.template

    def process_message(self, msg):
        if self.valid_checksum(msg) is not True:
            return False
        sync = msg[0]
        area = msg[1]
        data1 = msg[2]
        opcode = msg[3]
        data2 = msg[4]
        data3 = msg[5]
        join = msg[6]
        chk = msg[7]

        if sync != 28:
            try:
                self.handler({"type": "in", "msg": data,
                              "error": "Not a logical message"})
            except AttributeError:
                # No handler available
                pass
            return False

        if opcode < 9:
            event = self.process_preset(
                area, opcode, data1, data2, data3, join)
            event["msg"] = msg
        elif opcode == 72:
            event = self.process_indicatorled(area, data1, data2, data3, join)
            event["msg"] = msg
        elif opcode == 98:
            event = self.process_areastatus(area, data1)
            event["msg"] = msg
        elif opcode == 99:
            event = self.process_reqareastatus(area)
            event["msg"] = msg
        elif opcode == 101:
            event = self.process_linearpreset(area, data1, data2, data3, join)
            event["msg"] = msg
        else:
            event = {"type": "unknown", "msg": msg, "area": area}

        if len(msg) > self.messagesize + 1:
            print("Extra data:\t", msg)

        return event

    def valid_checksum(self, msg):
        if len(msg) < self.messagesize + 1:
            return False
        tocheck = bytearray(
            [msg[0], msg[1], msg[2], msg[3], msg[4], msg[5], msg[6]])
        chk = int(self.calc_checksum(tocheck), 16)
        if msg[7] != chk:
            return False
        return True

    def calc_checksum(self, s):
        """
        Calculates checksum for sending commands to the ELKM1.
        Sums the ASCII character values mod256 and returns
        the lower byte of the two's complement of that value.
        """
        return '%2X' % (-(sum(ord(c) for c in "".join(map(chr, s))) % 256) & 0xFF)

    def send(self, data):
        if self.connected is not True:
            self.connectSocket()

        data.append(int(self.calc_checksum(data), 16))

        try:
            self.s.sendall(data)
            try:
                self.handler({"type": "out", "msg": data})
            except AttributeError:
                # No handler available
                pass
            time.sleep(0.2)
        except (socket.error, socket.timeout) as e:
            self.connectSocket()

    def process_preset(self, area, opcode, fadeLow, fadeHigh, bank, join):
        preset = (opcode + (bank * 8)) + 1
        fade = (fadeLow + (fadeHigh * 256)) * 0.02
        return {"type": "preset", "area": area, "preset": preset, "fade": fade}

    def process_linearpreset(self, area, preset, fadeLow, fadeHigh, join):
        preset = preset + 1
        fade = (fadeLow + (fadeHigh * 256)) * 0.02
        return {"type": "preset", "area": area, "preset": preset, "fade": fade}

    def process_indicatorled(self, area, type, dimming, fadeVal, join):
        if type == 1:
            typeName = 'indicator'
        elif type == 2:
            typeName = 'backlight'
        else:
            typeName = 'unknown'

        if fadeVal > 0:
            fade = fadeVal / 50
        else:
            fade = 0

        dimpc = round((256 - dimming) / 255, 2) * 100

        return {"type": "indicator", "sub": typeName, "area": area, "dim": dimpc, "fade": fade}

    def process_areastatus(self, area, preset):
        preset = preset + 1
        return {"type": "presetupdate", "area": area, "preset": preset}

    def process_reqareastatus(self, area):
        return {"type": "presetrequest", "area": area}

    def reqPreset(self, area):
        cmd = self.template[:]
        cmd[1] = area
        cmd[3] = 99
        cmd[6] = 255
        self.send(cmd)
        return True

    def setPreset(self, area, preset, fade=2, join=255):
        cmd = self.template[:]
        cmd[1] = area
        if fade == 0:
            cmd[2] = 0
            cmd[4] = 0
        else:
            cmd[2] = int(fade / 0.02) - (int((fade / 0.02) / 256) * 256)
            cmd[4] = int((fade / 0.02) / 256)

        cmd[6] = join

        if preset < 1:
            return False
        elif preset > 64:
            return False

        bank = int((preset - 1) / 8)
        opcode = int(preset - (bank * 8)) - 1

        if opcode > 3:
            opcode = opcode + 6

        cmd[3] = opcode
        cmd[5] = bank

        self.send(cmd)
        return True

    def setIndicatorLED(self, area, type, dimpc, fadeVal=2, join=255):
        cmd = self.template[:]
        cmd[1] = area
        cmd[2] = type
        cmd[3] = 72

        if dimpc == 0:
            cmd[4] = 255
        elif dimpc == 1:
            cmd[4] = 255
        elif dimpc < 0:
            cmd[4] = 255
        elif dimpc > 100:
            cmd[4] = 1
        else:
            cmd[4] = int(256 - (dimpc / 100 * 255))

        if fadeVal < 0:
            cmd[5] = 0
        elif fadeVal > 5:
            cmd[5] = 255
        else:
            cmd[5] = int(fadeVal * 50)

        cmd[6] = join
        self.send(cmd)
        return True
