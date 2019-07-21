from __future__ import print_function
from enum import IntEnum
import struct
import binascii
import uuid
import threading

from .notifications import NotificationTypes, GenericClearTileNotification
from .parser import MsftBandParser
from .commands import SERIAL_NUMBER_REQUEST, CARGO_NOTIFICATION, \
                      GET_TILES_NO_IMAGES, CORE_WHO_AM_I, \
                      SET_THEME_COLOR, START_STRIP_SYNC_END, \
                      START_STRIP_SYNC_START, READ_ME_TILE_IMAGE, \
                      WRITE_ME_TILE_IMAGE_WITH_ID, SUBSCRIBE, \
                      CARGO_SYSTEM_SETTINGS_OOBE_COMPLETED_GET, \
                      NAVIGATE_TO_SCREEN, GET_ME_TILE_IMAGE_ID, \
                      GET_TILES, SET_TILES, \
                      UNSUBSCRIBE, SUBSCRIPTION_GET_DATA_LENGTH, \
                      SUBSCRIPTION_GET_DATA, SUBSCRIPTION_SUBSCRIBE_ID, \
                      SUBSCRIPTION_UNSUBSCRIBE_ID
from .socket import BandSocket
from .sensors import Sensor, decode_sensor_reading
from . import PUSH_SERVICE_PORT, layouts


class DummyWrapper:
    def print(self, *args, **kwargs):
        print(*args, **kwargs)

    def send(self, signal, args):
        print(signal, args)

    def atexit(self, func):
        import atexit
        atexit.register(func)


class BandType(IntEnum):
    """
    MSFT Band device types
    
    Cargo - MSFT Band 1
    Envoy - MSFT Band 2
    """
    Unknown = 0
    Cargo = 1
    Envoy = 2


class BandDevice:
    address = ""
    cargo = None
    push = None
    tiles = None
    band_type = BandType.Cargo  # TODO: actually detect this from Device
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

    def connect(self):
        self.cargo.connect()

        # start push thread
        self.push_thread = threading.Thread(target=self.listen_pushservice)
        self.push_thread.start()

    def disconnect(self):
        self.push.disconnect()
        self.cargo.disconnect()

    def who_am_i(self):
        return self.cargo.cargo_read(CORE_WHO_AM_I, 1)

    def check_if_oobe_completed(self):
        result, data = self.cargo.cargo_read(
            CARGO_SYSTEM_SETTINGS_OOBE_COMPLETED_GET, 4)
        if data:
            return struct.unpack("<I", data[0])[0] != 0
        return False

    def get_me_tile_image_id(self):
        result, data = self.cargo.cargo_read(GET_ME_TILE_IMAGE_ID, 4)
        if data:
            return data[0]
        return 0

    def get_me_tile_image(self):
        """
        Sends READ_ME_TILE_IMAGE command to device and returns a bgr565
        byte array with Me tile image
        """
        # calculate byte count based on device type
        if self.band_type == BandType.Cargo:
            byte_count = 310 * 102 * 2
        elif self.band_type == BandType.Envoy:
            byte_count = 310 * 128 * 2
        else:
            byte_count = 0

        # read Me Tile image
        result, data = self.cargo.cargo_read(READ_ME_TILE_IMAGE, byte_count)
        pixel_data = b''.join(data)
        return pixel_data

    def set_me_tile_image(self, pixel_data, image_id):
        result, data = self.cargo.cargo_write_with_data(
            WRITE_ME_TILE_IMAGE_WITH_ID,
            pixel_data,
            struct.pack("<I", image_id))
        return result, data

    def navigate_to_screen(self, screen):
        """
        Tells the device to navigate to a given screen.
        AFAIK works only with OOBE screens in OOBE mode
        """
        return self.cargo.cargo_write_with_data(
            NAVIGATE_TO_SCREEN, struct.pack("<H", screen))

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
            try:
                result = self.push.receive()
            except OSError:
                break

            packet_type = struct.unpack("H", result[0:2])[0]
            self.wrapper.print(packet_type)

            if packet_type == 1:
                sensor = decode_sensor_reading(result)
                self.wrapper.print(sensor)
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
        arguments = struct.pack("Bxxxx", subscription_type)
        result, info = self.cargo.cargo_write(SUBSCRIBE, arguments)
        return result

    def unsubscribe(self, subscription_type):
        arguments = struct.pack("B", subscription_type)
        result, info = self.cargo.cargo_write(UNSUBSCRIBE, arguments)
        return result

    def sync(self):
        for service in self.services.values():
            self.wrapper.print("%s" % service, end='')
            try:
                result = getattr(service, "sync")()
            except Exception as exc:
                self.wrapper.print(exc)
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
        self.cargo.cargo_write(START_STRIP_SYNC_START)
        colors = struct.pack("I"*6, *[int(x) for x in colors])
        self.cargo.cargo_write_with_data(SET_THEME_COLOR, colors)
        self.cargo.cargo_write(START_STRIP_SYNC_END)

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

    def get_max_tile_capacity(self):
        # TODO: actual logic for calculating that
        return 15

    def set_tiles(self):
        self.cargo.cargo_write(START_STRIP_SYNC_START)
        # icons = []
        tiles = []

        data = bytes([])
        for x in self.tiles:
            # icons.append(x['icon'])
            tile = bytes([])
            tile += x['guid'].bytes_le
            tile += struct.pack("<I", x['order'])
            tile += struct.pack("<I", x['theme_color'])
            tile += struct.pack("<H", len(x['name']))
            tile += struct.pack("<H", x['settings_mask'])
            tile += MsftBandParser.serialize_text(x['name'], 30)
            tiles.append(tile)
        # data = b''.join(icons)
        data += struct.pack("<I", len(tiles))
        data += b''.join(tiles)

        result = self.cargo.cargo_write_with_data(SET_TILES, data, struct.pack("<I", len(tiles)))
        self.cargo.cargo_write(START_STRIP_SYNC_END)
        return result

    def request_tiles(self, icons=False):
        max_tiles = self.get_max_tile_capacity()
        response_size = 88 * max_tiles + 4
        command = GET_TILES_NO_IMAGES

        if icons:
            response_size += max_tiles * 1024
            command = GET_TILES

        result, tiles = self.cargo.cargo_read(
            command, response_size)
        tile_data = b"".join(tiles)

        tile_list = []
        tile_icons = []

        begin = 0

        if icons:
            for i in range(0, max_tiles):
                tile_icons.append(tile_data[begin:begin+1024])
                begin += 1024

        # first 4 bytes are tile count
        tile_count = struct.unpack("<I", tile_data[begin:begin+4])[0]
        begin += 4
        i = 0

        # while there are tiles
        while i < tile_count:
            # get guuid
            guid = uuid.UUID(bytes_le=tile_data[begin:begin+16])
            order = struct.unpack("<I", tile_data[begin+16:begin+20])[0]
            theme_color = struct.unpack("<I", tile_data[begin+20:begin+24])[0]
            name_length = struct.unpack("<H", tile_data[begin+24:begin+26])[0]
            settings_mask = struct.unpack("<H", tile_data[begin+26:begin+28])[0]
            
            # get tile name
            if name_length:
                name = MsftBandParser.bytes_to_text(
                    tile_data[begin+28:begin+80])
            else:
                name = ''

            # append tile to list
            tile_list.append({
                "guid": guid,
                "order": order,
                "theme_color": theme_color,
                "name_length": name_length,
                "settings_mask": settings_mask,
                "name": name,
                "icon": tile_icons[i] if icons else None
            })

            # move to next tile
            begin += 88
            i += 1
        self.tiles = tile_list

    def send_notification(self, notification):
        self.cargo.cargo_write_with_data(
            CARGO_NOTIFICATION, notification.serialize())
