from PIL import Image, ImageChops
import pytest

from libband.parser import MsftBandParser


@pytest.mark.xfail(reason='Image comes out a bit off')
def test_image_to_bgr565_and_back():
    """
    Checks if converting image to bgr565 format and back produces the same
    output.
    """
    original_image = Image.open('libband/tests/test_img.jpg')
    bgr565 = MsftBandParser.image_to_bgr565(original_image)
    converted_back = MsftBandParser.bgr565_to_image((768, 326), bgr565)

    # If images are equal, bounding box should be None
    diff = ImageChops.difference(original_image, converted_back)
    assert diff.getbbox() is None


def test_decode_and_encode_rle():
    """
    Checks if decoding RLE icon from Band and encoding it back to RLE format
    produces the same output.
    """
    # load known good RLE icon
    f = open('libband/tests/test_rle.rle', 'rb')
    rle_icon = f.read()
    f.close()

    # decode the icon and back
    width, height, decoded_icon = MsftBandParser.decode_icon_rle(rle_icon)
    encoded_icon = MsftBandParser.encode_icon_rle(width, height, decoded_icon)
    assert rle_icon == encoded_icon


@pytest.mark.xfail(reason='Image comes out a bit off')
def test_bgra32_alpha4_and_back():
    """
    Let's convert RLE icon to PIL icon and back to see if we get the same
    output
    """
    # load known good RLE icon
    f = open('libband/tests/test_rle.rle', 'rb')
    rle_icon = f.read()
    f.close()

    # decode icon and convert to PIL Image
    width, height, decoded_icon = MsftBandParser.decode_icon_rle(rle_icon)
    bgra32 = MsftBandParser.alpha4_to_bgra32(decoded_icon)
    image = Image.frombytes('RGBA', (width, height), bgra32, 'raw', 'BGRA')

    # convert back to bgra32 and RLE
    pil_bgra32 = image.tobytes()
    assert bgra32 == pil_bgra32

    # convert pil_bgra32 to alpha4
    alpha4 = MsftBandParser.bgra32_to_alpha4(pil_bgra32)
    assert alpha4 == decoded_icon

    # let's encode the image to RLE format 
    encoded_icon = MsftBandParser.encode_icon_rle(width, height, alpha4)
    assert rle_icon == encoded_icon
