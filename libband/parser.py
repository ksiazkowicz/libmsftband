import struct
import sys
from unidecode import unidecode
from libband.filetimes import get_time, WINDOWS_TICKS_TO_POSIX_EPOCH

MAX_TIME = 2650467743999990000


class MsftBandParser:
    @staticmethod
    def deserialize_time(filetime):
        if filetime > WINDOWS_TICKS_TO_POSIX_EPOCH and filetime <= MAX_TIME:
            return get_time(filetime)

        return get_time(WINDOWS_TICKS_TO_POSIX_EPOCH)

    @staticmethod
    def char_to_bytes(char):
        try:
            if sys.version_info[0] == 3:
                try:
                    return bytes(char, "latin-1")
                except:
                    return bytes([char])
            else:
                return char.encode("latin-1")
        except UnicodeEncodeError:
            return MsftBandParser.char_to_bytes(unidecode(char))

    @staticmethod
    def text_to_bytes(text):
        """Converts text to list of unicode bytes"""
        return [MsftBandParser.char_to_bytes(x) for x in text]

    @staticmethod
    def serialize_text(text, fixed_length=False):
        """Serializes given text (latin-1 char + padding)*length"""
        length = len(text)
        packet = struct.pack(length*"sx", *MsftBandParser.text_to_bytes(text))
        if fixed_length > length:
            packet += struct.pack('xx'*(fixed_length - length))
        return packet

    @staticmethod
    def bytes_to_text(input):
        """Converts given bytes (latin-1 char + padding)*length to text"""
        content = struct.unpack((int(len(input)/2))*"sx", input)
        return "".join([x.decode("latin-1") for x in content]).rstrip("\x00")
