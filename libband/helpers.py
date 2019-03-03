import struct
import sys
from unidecode import unidecode


def char_to_bytes(char):
    try:
        if sys.version_info[0] == 3:
            return bytes(char, "latin-1")
        else:
            return char.encode("latin-1")
    except UnicodeEncodeError:
        return char_to_bytes(unidecode(char))


def text_to_bytes(text):
    """Converts text to list of unicode bytes"""
    return [char_to_bytes(x) for x in text]


def serialize_text(text):
    """Serializes given text (latin-1 char + padding)*length"""
    return struct.pack(len(text)*"sx", *text_to_bytes(text))


def bytes_to_text(input):
    """Converts given bytes (latin-1 char + padding)*length to text"""
    content = struct.unpack((int(len(input)/2))*"sx", input)
    return "".join([x.decode("latin-1") for x in content]).rstrip("\x00")
