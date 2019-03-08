from __future__ import print_function
import struct
import binascii
import uuid
import threading

from .notifications import NotificationTypes, GenericClearTileNotification
from .parser import MsftBandParser
from .commands import SERIAL_NUMBER_REQUEST, CARGO_NOTIFICATION, \
                      GET_TILES_NO_IMAGES, \
                      SET_THEME_COLOR, START_STRIP_SYNC_END, \
                      START_STRIP_SYNC_START, READ_ME_TILE_IMAGE, \
                      WRITE_ME_TILE_IMAGE_WITH_ID, SUBSCRIBE
from .socket import BandSocket
from . import PUSH_SERVICE_PORT, layouts


class DummyWrapper:
    def print(self, *args, **kwargs):
        print(*args, **kwargs)

    def send(self, signal, args):
        print(signal, args)

    def atexit(self, func):
        import atexit
        atexit.register(func)


class BandDevice:
    address = ""
    cargo = None
    push = None
    tiles = None
    band_language = None
    band_name = None
    serial_number = None
    push_thread = None
    services = {}
    wrapper = DummyWrapper()

    def __init__(self, address):
        self.address = address
        self.push = BandSocket(self, PUSH_SERVICE_PORT)
        self.cargo = BandSocket(self)
        self.wrapper.atexit(self.disconnect)

        # start push thread
        self.push_thread = threading.Thread(target=self.listen_pushservice)
        self.push_thread.start()

    def connect(self):
        self.cargo.connect()

    def disconnect(self):
        self.push.disconnect()
        self.cargo.disconnect()

    def process_push(self, guid, command, message):
        for service in self.services.values():
            if service.guid == guid:
                new_message = service.push(guid, command, message)
                if new_message:
                    message = new_message
                    break
        return message

    def process_tile_callback(self, result):
        opcode = struct.unpack("I", result[6:10])[0]
        guid = uuid.UUID(bytes_le=result[10:26])
        command = result[26:44]
        tile_name = MsftBandParser.bytes_to_text(result[44:84])

        message = {
            "opcode": opcode,
            "guid": str(guid),
            "command": binascii.hexlify(command),
            "tile_name": tile_name,
        }
        message = self.process_push(guid, command, message)
        self.wrapper.send("PushService", message)

    def process_notification_callback(self, result):
        opcode = struct.unpack("I", result[2:6])[0]
        guid = uuid.UUID(bytes_le=result[6:22])
        command = result[22:]

        message = {
            "opcode": opcode,
            "guid": str(guid),
            "command": str(binascii.hexlify(command)),
        }

        message = self.process_push(guid, command, message)
        self.wrapper.send("PushService", message)

    def listen_pushservice(self):
        self.push.connect()
        while True:
            result = self.push.receive()
            packet_type = struct.unpack("H", result[0:2])[0]
            self.wrapper.print(packet_type)

            if packet_type == 1:
                # sensor data
                packet_length = struct.unpack("L", result[2:6])[0]
                subscription_type = struct.unpack("B", result[6:7])[0]
                missed_samples = struct.unpack("B", result[7:8])[0]
                sample_size = struct.unpack("H", result[9:11])[0]

                if subscription_type == 16:
                    # Heart Rate sensor
                    value = result[11]
                    quality = result[12] >= 6
                    self.wrapper.print("Heart Rate: %d (%s)" % (
                        value, "Locked" if quality else "Acquiring"))
                elif subscription_type == 19:
                    # Pedometer
                    value = struct.unpack("L", result[11:15])
                    self.wrapper.print("Pedometer: %d" % value)
                elif subscription_type == 35:
                    # Device Contact sensor
                    value = result[11]
                    self.wrapper.print("Device Contact: %s" % ("True" if value else "False"))
                elif subscription_type == 38:
                    # Battery Gauge
                    percent_charge = result[11]
                    filtered_voltage = struct.unpack("H", result[11:13])[0]
                    battery_gauge_alerts = struct.unpack("H", result[13:15])[0]

                    percent = (percent_charge / 10)*10
                    if percent > 100:
                        percent = 100

                    self.wrapper.send("Sensor::Battery", percent)
                    self.wrapper.print("Battery Gauge: %d | Filtered Voltage: %s | Alerts: %s" % (
                        percent_charge, filtered_voltage, battery_gauge_alerts))
                else:
                    self.wrapper.print(binascii.hexlify(result))
                    self.wrapper.print(subscription_type, missed_samples, sample_size)
            elif packet_type == 100:
                self.process_notification_callback(result)
            elif packet_type == 101:
                self.process_notification_callback(result)
            elif packet_type == 204:
                self.wrapper.print(binascii.hexlify(result))
                self.process_tile_callback(result)
            else:
                self.wrapper.print(packet_type)
                self.wrapper.print(binascii.hexlify(result))

    def subscribe(self, subscription_type):
        command = SUBSCRIBE + b"\x00"*4 + struct.pack("L", subscription_type) + struct.pack("L", 0) # b"\x00"
        result = self.cargo.send_for_result(command)

    def sync(self):
        for service in self.services.values():
            self.wrapper.print("%s" % service, end='')
            try:
                result = getattr(service, "sync")()
            except:
                result = False
            self.wrapper.print("          [%s]" % ("OK" if result else "FAIL"))

        self.wrapper.print("Sync finished")

    def clear_tile(self, guid):
        self.send_notification(GenericClearTileNotification(guid))

    def set_theme(self, colors):
        """
        Takes an array of 6 colors encoded as ints

        Base, Highlight, Lowlight, SecondaryText, HighContrast, Muted
        """
        self.cargo.send_for_result(START_STRIP_SYNC_START)
        colors = struct.pack("I"*6, *[int(x) for x in colors])
        self.cargo.cargo_write_with_data(SET_THEME_COLOR, colors)
        self.cargo.send_for_result(START_STRIP_SYNC_END)

    def get_tiles(self):
        if not self.tiles:
            self.request_tiles()
        return self.tiles

    def get_serial_number(self):
        if not self.serial_number:
            # ask nicely for serial number
            result, number = self.cargo.cargo_read(SERIAL_NUMBER_REQUEST, 12)
            if result:
                self.serial_number = number[0].decode("utf-8")
        return self.serial_number

    def request_tiles(self):
        result, tiles = self.cargo.send_for_result(GET_TILES_NO_IMAGES)
        tile_data = b"".join(tiles)

        tile_list = []

        # no idea what these 4 bytes are yet
        begin = 4
        # while there are tiles
        while begin + 88 <= len(tile_data):
            # get guuid
            guid = uuid.UUID(bytes_le=tile_data[begin:begin+16])
            # that thing after guuid that might be an icon (?)
            icon = tile_data[begin+16:begin+16+12]

            # get tile name
            name = MsftBandParser.bytes_to_text(tile_data[begin+28:begin+80])

            # append tile to list
            tile_list.append({
                "guid": guid,
                "icon": icon,
                # convert name to readable format
                "name": name
            })

            # move to next tile
            begin += 88
        self.tiles = tile_list

    def send_notification(self, notification):
        self.cargo.cargo_write_with_data(
            CARGO_NOTIFICATION, notification.serialize())

    def response_result(self, response):
        error_code = struct.unpack("<I", response[2:6])[0]
        if error_code:
            self.wrapper.print("Error: %s" % error_code)
        return not error_code
