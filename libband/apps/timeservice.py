import struct
from datetime import datetime
from libband.commands import FACILITIES, make_command
from libband.filetimes import convert_back
from .app import App


class TimeService(App):
    app_name = "Time Service"
    guid = None

    def sync(self):
        new_device_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        self.band.cargo.send(make_command(
            FACILITIES["LibraryTime"], False, 1) + struct.pack("<I", 8))
        result, response = self.band.cargo.send_for_result(
            struct.pack("<Q", convert_back(new_device_time)))
        return result

    def get_device_time(self):
        result, responses = self.band.cargo.send_for_result(make_command(
            FACILITIES["LibraryTime"], True, 2) + struct.pack("<I", 16))
        if result:
            return struct.unpack("H"*8, responses[0])
