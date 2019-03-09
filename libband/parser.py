import struct
import sys
from PIL import Image
from unidecode import unidecode
from libband.filetimes import get_time, WINDOWS_TICKS_TO_POSIX_EPOCH

MAX_TIME = 2650467743999990000


class MsftBandParser:
    @staticmethod
    def cuint32_to_hex(color):
        return "#{0:02x}{1:02x}{2:02x}".format(color >> 16 & 255, 
                                               color >> 8 & 255, 
                                               color & 255)
    
    @staticmethod
    def encode_color(alpha, r, g, b):
        return (alpha << 24 | r << 16 | g << 8 | b)

    @staticmethod
    def decode_color(color):
        return {
            "r": color >> 16 & 255,
            "g": color >> 8 & 255,
            "b": color & 255
        }

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

    @staticmethod
    def bgr565_to_image(size, image):
        """
        Converts bgr565 image from Band to PIL Image object
        """
        return Image.frombytes('RGB', size, image, 'raw', 'BGR;16')
    
    @staticmethod
    def image_to_bgr565(image):
        """
        Converts PIL Image object to bgr565 image

        If you're asking why I'm not using Image.tobytes, it's because
        it pretends that it doesn't know how to convert RGB image
        to bgr565.

        FFS, get off those pills PIL developers
        """
        width, height = image.size
        pixel_array = []
        for y in range(0, height):
            for x in range(0, width):
                r, g, b = image.getpixel((x, y))
                color = b >> 3 | (g & 252) << 3 | (r & 248) << 8
                pixel_array.append(color)
        return struct.pack('H' * (width * height), *pixel_array)

