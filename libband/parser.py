import struct
import sys
from PIL import Image
from unidecode import unidecode
from libband.filetimes import get_time, WINDOWS_TICKS_TO_POSIX_EPOCH

MAX_TIME = 2650467743999990000


class MsftBandParser:
    @staticmethod
    def cuint32_to_hex(color):
        return "#{0:02x}{1:02x}{2:02x}".format(
            color >> 16 & 255,
            color >> 8 & 255,
            color & 255
        )

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
                except Exception:
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

    @staticmethod
    def decode_icon_rle(icon):
        num = icon[0] << 8 | icon[1]
        num2 = icon[2] << 8 | icon[3]
        num3 = num * num2
        if num == 0 or num2 == 0 or num3 > 15270:
            print('Invalid file format')
            return None, None, None

        byte_array = bytearray(int(num3 / 2 + num3 % 2))
        num4 = 0
        num5 = icon[4] << 8 | icon[5]
        for i in range(6, num5):
            b = icon[i] >> 4
            b2 = icon[i] & 15
            if b2 == 0:
                num4 += b
            else:
                b3 = 0
                while b3 < b:
                    num6 = num4 % 2
                    if num6 != 0:
                        if num6 == 1:
                            num7 = int(num4 / 2)
                            byte_array[num7] = byte_array[num7] | b2
                    else:
                        byte_array[int(num4 / 2)] = b2 << 4
                    b3 += 1
                    num4 += 1

        return num, num2, bytes(byte_array)

    @staticmethod
    def encode_icon_rle(width, height, icon):
        rle_array = bytearray(1024)
        num = 0
        num2 = 6
        rle_array[0] = width >> 8
        rle_array[1] = width
        rle_array[2] = height >> 8
        rle_array[3] = height

        # width = 10
        # height = 10

        for i in range(0, height):
            b = 0
            num3 = 0
            num4 = num % 2
            if num4 != 0:
                if num4 == 1:
                    b = icon[int(num / 2)] & 15
                    num += 1
            else:
                b = (icon[int(num / 2)] >> 4) & 15
                num += 1
            num3 += 1
            for j in range(1, width):
                b2 = 0

                num4 = num % 2
                if num4 != 0:
                    if num4 == 1:
                        b2 = icon[int(num / 2)] & 15
                        num += 1
                else:
                    b2 = (icon[int(num / 2)] >> 4) & 15
                    num += 1
                if b != b2:
                    if num3 > 0:
                        rle_array[num2] = ((num3 << 4) | b) % 255
                        num2 += 1
                    b = b2
                    num3 = 0
                num3 += 1

                if num3 == 15:
                    if num2 >= 1024:
                        raise Exception('Encoding failed')
                    rle_array[num2] = (num3 << 4) | b
                    num2 += 1
                    num3 = 0
            if num3 > 0:
                if num2 >= 1024:
                    raise Exception('Encoding failed')
                rle_array[num2] = (num3 << 4) | b
                num2 += 1
        rle_array[4] = (num2 >> 8) % 256
        rle_array[5] = num2 % 256
        return rle_array

    @staticmethod
    def alpha4_to_bgra32(image):
        bgra32_length = len(image) * 2 * 4
        bgra32_array = bytes([])
        position = 0
        num = 0
        # width = height = math.sqrt(bgra32_length / 4)
        while position < bgra32_length:
            num2 = num % 2
            if num2 != 0:
                if num2 == 1:
                    index = int(num / 2)
                    # value = image[index] % 256
                    value = (image[index] % 16) * 255 / 15
                    bgra32_array += bytes([
                        int(value)
                    ])
            else:
                index = int(num / 2)
                value = ((image[index] % 256) >> 4) * 255/15
                bgra32_array += bytes([
                   int(value)
                ])
            if position % 4 == 3:
                num += 1
            position += 1
        return bgra32_array

    def bgra32_to_alpha4(image):
        array_size = int((len(image)/4) / 2 + (len(image)/4) % 2)
        byte_array = bytearray(array_size)
        position = 0
        num = 0
        while position < len(image):
            if position % 4 == 3:
                num2 = num % 2
                if num2 != 0:
                    if num2 == 1:
                        num3 = num / 2
                        num += 1
                        value = (image[position] % 256) >> 4
                        byte_array[int(num3)] |= int(value)
                else:
                    num4 = num / 2
                    num += 1
                    value = image[position] % 256
                    byte_array[int(num4)] |= int(value)
            position += 1
        return byte_array
