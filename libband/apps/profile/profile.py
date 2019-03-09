from libband.parser import MsftBandParser
from libband.filetimes import datetime_to_filetime
import struct, uuid


class Profile:
    version = 1
    last_sync = None
    user_id = None
    birthdate = None
    weight = None
    height = None
    gender = 0
    band_name = 'MSFT Band'
    band_language = 'en-us'
    locale = None
    run_display_units = None
    telemetry_enabled = False


    def __init__(self, data):
        self.version = struct.unpack("<H", data[0:2])[0]
        self.last_sync = MsftBandParser.deserialize_time(struct.unpack("Q", data[2:10])[0])
        self.user_id = uuid.UUID(bytes_le=data[10:26])
        self.birthdate = MsftBandParser.deserialize_time(struct.unpack("Q", data[26:34])[0])
        self.weight = struct.unpack("<I", data[34:38])[0] / 1000
        self.height = struct.unpack("<H", data[38:40])[0] / 10
        self.gender = data[40]

        self.band_name = MsftBandParser.bytes_to_text(data[41:73])
        self.band_language = MsftBandParser.bytes_to_text(data[73:85])
        self.locale = {
            "name": self.band_language,
            "id": struct.unpack("<H", data[85:87])[0],
            "language": struct.unpack("<H", data[87:89])[0],
            "date_separator": struct.unpack("sx", data[89:91])[0],
            "number_separator": struct.unpack("sx", data[91:93])[0],
            "decimal_separator": struct.unpack("sx", data[93:95])[0],
            "time_format": data[95],
            "date_format": data[96],
            "distance_short_units": data[97],
            "distance_long_units": data[98],
            "mass_units": data[99],
            "volume_units": data[100],
            "energy_units": data[101],
            "temperature_units": data[102]
        }
        self.run_display_units = data[103]
        self.telemetry_enabled = data[104] == 1

    def __dict__(self):
        return {
            "version": self.version,
            "last_sync": self.last_sync,
            "user_id": self.user_id,
            "birthdate": self.birthdate,
            "weight": self.weight,
            "height": self.height,
            "gender": "Male" if self.gender == 0 else "Female",
            "name": self.band_name,
            "locale": self.locale,
            "run_display_units": self.run_display_units,
            "telemetry_enabled": self.telemetry_enabled,
        }

    def as_packet(self):
        packet = bytes([])
        packet += struct.pack("<H", self.version)
        packet += struct.pack("Q", datetime_to_filetime(self.last_sync))
        packet += self.user_id.bytes_le
        packet += struct.pack("Q", datetime_to_filetime(self.birthdate))
        packet += struct.pack("<I", int(self.weight * 1000))
        packet += struct.pack("<H", int(self.height * 10))
        packet += bytes([self.gender])
        packet += MsftBandParser.serialize_text(self.band_name[:16], 16)
        packet += MsftBandParser.serialize_text(self.band_language[:6], 6)
        packet += struct.pack("H", self.locale['id'])
        packet += struct.pack("H", self.locale['language'])
        packet += MsftBandParser.serialize_text(self.locale['date_separator'])
        packet += MsftBandParser.serialize_text(self.locale['number_separator'])
        packet += MsftBandParser.serialize_text(self.locale['decimal_separator'])
        packet += bytes([self.locale['time_format']])
        packet += bytes([self.locale['date_format']])
        packet += bytes([self.locale['distance_short_units']])
        packet += bytes([self.locale['distance_long_units']])
        packet += bytes([self.locale['mass_units']])
        packet += bytes([self.locale['volume_units']])
        packet += bytes([self.locale['energy_units']])
        packet += bytes([self.locale['temperature_units']])
        packet += bytes([self.run_display_units])
        packet += bytes([self.telemetry_enabled])
        packet += struct.pack('x'*23)
        return packet
