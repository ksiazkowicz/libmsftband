import bluetooth
import time
import struct
from . import CARGO_SERVICE_PORT, TIMEOUT, BUFFER_SIZE


class BandSocket:
    device = None
    socket = None
    port = CARGO_SERVICE_PORT
    max_reconnects = 5
    reconnect_count = 0

    def __init__(self, device=None, port=CARGO_SERVICE_PORT):
        self.device = device
        self.port = port
        self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

    def connect(self, timeout=TIMEOUT):
        self.reconnect_count = 0
        self.device.wrapper.send("Status", [self.port, "Connecting"])
        while True:
            try:
                self.socket.close()
                self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                self.socket.connect((self.device.address, self.port))
                break
            except bluetooth.btcommon.BluetoothError as error:
                self.socket.close()
                self.device.wrapper.print("Could not connect: %s" % error)
                time.sleep(timeout)
                self.reconnect_count += 1
            if self.reconnect_count > self.max_reconnects:
                self.device.wrapper.send("Status", [self.port, "Disconnected"])
                return
        self.reconnect_count = 0
        self.device.wrapper.send("Status", [self.port, "Connected"])

    def disconnect(self):
        try:
            self.socket.close()
        except:
            pass
        self.reconnect_count = 0
        self.device.wrapper.send("Status", "Disconnected")

    def receive(self, buffer_size=BUFFER_SIZE):
        while True:
            try:
                result = self.socket.recv(buffer_size)
                break
            except bluetooth.btcommon.BluetoothError as error:
                self.device.wrapper.print("Connecting because %s" % error)
                self.connect()
        return result

    def send(self, packet):
        while True:
            # try to reconnect if failed
            try:
                self.socket.send(packet)
                break
            except bluetooth.btcommon.BluetoothError as error:
                self.device.wrapper.print("Connecting because %s" % error)
                self.connect()

    def send_for_result(self, packet, buffer_size=BUFFER_SIZE):
        results = []
        success = True

        # send packet
        self.send(packet)

        while True:
            self.socket.settimeout(5.0)
            result = self.receive(BUFFER_SIZE)

            # check if we got final result
            if result[0:2] == b'\xfe\xa6':
                error_code = struct.unpack("<I", result[2:6])[0]
                if error_code:
                    self.device.wrapper.print("Error: %s" % error_code)
                success = not error_code
                break

            # nope, more data
            results.append(result)

        # we're done
        return success, results

