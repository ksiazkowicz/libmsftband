import struct
import math
from copy import deepcopy
from .helpers import serialize_text

ELEMENT_TEXT = 3001
ELEMENT_ICON = 3101
ELEMENT_TEXT_BUTTON = 3303
ELEMENT_IMAGE_BUTTON = 3101


class Layout:
    definition = {}

    @classmethod
    def defaults(cls):
        return {}

    @classmethod
    def get_key(cls, position):
        line = math.floor(position/10)
        if position >= 10:
            index = int(str(position)[1])
        else:
            index = position

        for item in cls.definition.get("items", []):
            if item.get("line", 0) == line and item.get("index", 0) == index:
                return item.get("key", "INVALID")
        return "INVALID"

    @classmethod
    def serialize_as_update(cls, page_id, input_data=None):
        # get defaults for this layout first
        data = cls.defaults()
        if input_data:
            # update with given data if available
            data.update(input_data)

        update_content = b""
        for item in cls.definition.get("items", []):
            kwargs = deepcopy(item)
            key = kwargs.pop("key")
            value = data.get(key, None)

            if value is None:
                continue

            if kwargs.get("item_type", ELEMENT_TEXT) == ELEMENT_ICON or \
               kwargs.get("item_type", ELEMENT_TEXT) == ELEMENT_IMAGE_BUTTON:
                kwargs["icon_id"] = value
            else:
                kwargs["content"] = value

            update_content += make_item(**kwargs)

        update_content = struct.pack("HH", len(update_content),
                                     cls.definition.get("layout", 0)) + \
            page_id.bytes_le + struct.pack("H", 0) + update_content
        return update_content


class MultilineTextLayout(Layout):
    definition = {
        "layout": 0,
        "items": [{
            "item_type": ELEMENT_TEXT,
            "line": 1,
            "index": 1,
            "key": "line_1"
        }, {
            "item_type": ELEMENT_TEXT,
            "line": 2,
            "index": 1,
            "key": "line_2"
        }, {
            "item_type": ELEMENT_TEXT,
            "line": 3,
            "index": 1,
            "key": "line_3"
        }]
    }


class NowPlayingLayout(Layout):
    definition = {
        "layout": 0,
        "items": [{
            "item_type": ELEMENT_TEXT,
            "line": 0,
            "index": 8,
            "key": "title"
        }, {
            "item_type": ELEMENT_TEXT,
            "line": 0,
            "index": 9,
            "key": "artist"
        }, {
            "item_type": ELEMENT_TEXT,
            "line": 1,
            "index": 0,
            "key": "album"
        }]
    }


class VolumeButtonsLayout(Layout):
    definition = {
        "layout": 1,
        "items": [{
            "item_type": ELEMENT_TEXT_BUTTON,
            "line": 0,
            "index": 7,
            "key": "VolumeUp",
        }, {
            "item_type": ELEMENT_TEXT_BUTTON,
            "line": 0,
            "index": 6,
            "key": "VolumeDown",
        }]
    }

    @classmethod
    def defaults(cls):
        return {
            "VolumeUp": "Volume +",
            "VolumeDown": "Volume -"
        }



class MusicControlLayout(Layout):
    definition = {
        "layout": 2,
        "items": [{
            "item_type": ELEMENT_IMAGE_BUTTON,
            "line": 1,
            "index": 1,
            "key": "prevButton",
        }, {
            "item_type": ELEMENT_TEXT_BUTTON,
            "line": 0,
            "index": 2,
            "key": "prevButtonText",
        }, {
            "item_type": ELEMENT_IMAGE_BUTTON,
            "line": 1,
            "index": 2,
            "key": "playButton",
        }, {
            "item_type": ELEMENT_TEXT_BUTTON,
            "line": 0,
            "index": 3,
            "key": "playButtonText",
        }, {
            "item_type": ELEMENT_IMAGE_BUTTON,
            "line": 1,
            "index": 3,
            "key": "nextButton",
        }, {
            "item_type": ELEMENT_TEXT_BUTTON,
            "line": 0,
            "index": 5,
            "key": "nextButtonText",
        }]
    }

    @classmethod
    def defaults(cls):
        return {
            "prevButton": 4,
            "prevButtonText": " ",
            "playButton": 2,
            "playButtonText": " ",
            "nextButton": 3,
            "nextButtonText": " ",
        }


class HeaderSecondaryLargeIconAndMetricLayout(Layout):
    definition = {
        "layout": 1,
        "items": [{
            "item_type": ELEMENT_TEXT,
            "line": 1,
            "index": 1,
            "key": "header"
        }, {
            "item_type": ELEMENT_TEXT,
            "line": 1,
            "index": 2,
            "key": "separator"
        }, {
            "item_type": ELEMENT_TEXT,
            "line": 1,
            "index": 3,
            "key": "secondary"
        }, {
            "item_type": ELEMENT_ICON,
            "line": 2,
            "index": 1,
            "key": "largeIcon"
        }, {
            "item_type": ELEMENT_TEXT,
            "line": 2,
            "index": 2,
            "key": "metric"
        }, {
            "item_type": ELEMENT_TEXT,
            "line": 2,
            "index": 3,
            "key": "secondary_metric"
        }]
    }


def make_item(item_type, line, index, content="", icon_id=None):
    """
    Returns item serialized as HHHcxcxcxcxcxcxcx...

    :param item_type: element item, text or icon
    :param line: position, which line
    :param index: position, which spot
    :param content: item text (if text)
    :param icon_id: item icon ID (if icon)
    """
    position = line*10 + index
    argument = len(content) if not icon_id else icon_id
    item = struct.pack("HHH", item_type, position, argument)
    if content:
        item += serialize_text(content)
    return item
