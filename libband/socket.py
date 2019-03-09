import bluetooth
import time
import struct
from libband.status import decode_status
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
            except OSError as error:
                # assume user actually wanted to disconnect
                pass
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
            except OSError as error:
                # I guess we lost connection because of malformed packet
                self.device.wrapper.print("Connecting because %s" % error)
                self.connect()

    def send_for_result(self, packet, buffer_size=BUFFER_SIZE):
        results = []
        success = False

        # send packet
        self.send(packet)

        while True:
            self.socket.settimeout(6.0)
            result = self.receive(BUFFER_SIZE)

            # break when we get empty response 
            # (because we forgot to break on error? no clue)
            if not result:
                break

            # check if we got status bits
            if result[-6:-4] == b'\xfe\xa6':
                status = decode_status(struct.unpack("<I", result[-4:])[0])
                success = not status.get('is_error', False)
                if not success:
                    self.device.wrapper.print("Error: %s" % status)

                if len(result) > 6:
                    result = result[:-6]
                    results.append(result)
                break

            # nope, more data
            results.append(result)

        # we're done
        return success, results

    def make_command_packet(
        self, command, arguments_buffer_size, data_stage_size, arguments,
        prepend_size):
        result = bytes([])
        if prepend_size:
            result += bytes([8 + arguments_buffer_size])
        result += struct.pack("<H", 12025)
        result += struct.pack("<H", command)
        result += struct.pack("<I", data_stage_size)
        if arguments:
            result += arguments
        return result

    def cargo_read(self, command, response_size):
        command_packet = self.make_command_packet(
            command, 
            4, 
            response_size, 
            struct.pack("<I", response_size), 
            True)
        return self.send_for_result(command_packet)

    def cargo_write(self, command, arguments=None):
        packet = self.make_command_packet(
            command, 
            len(arguments) if arguments else 0, 
            0, arguments, True)
        return self.send_for_result(packet)

    def cargo_write_with_data(self, command, data, arguments=None):
        packet = self.make_command_packet(
            command, 
            len(arguments) if arguments else 0, 
            len(data) if data else 0, 
            arguments, 
            True)
        self.send(packet)
        return self.send_for_result(data)
    
