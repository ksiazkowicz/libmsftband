import struct
from datetime import datetime
from libband.commands import SET_DEVICE_TIME, GET_DEVICE_TIME
from libband.filetimes import datetime_to_filetime
from .app import App


class TimeService(App):
    app_name = "Time Service"
    guid = None

    def sync(self):
        return self.set_device_time(datetime.now())

    def get_device_time(self):
        result, responses = self.band.cargo.cargo_read(GET_DEVICE_TIME, 16)
        if result:
            return struct.unpack("H"*8, responses[0])

    def set_device_time(self, new_time):
        result, response = self.band.cargo.cargo_write_with_data(
            SET_DEVICE_TIME,
            struct.pack("<Q", datetime_to_filetime(new_time))
        )
        return result

