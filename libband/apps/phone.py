import binascii
import struct
from .app import App
from libband.tiles import CALLS
from libband.helpers import bytes_to_text


class PhoneService(App):
    app_name = "Phone Service"
    guid = CALLS

    def push(self, guid, command, message):
        message = super().push(guid, command, message)
        if message:
            if message["opcode"] == 348:
                call_id = struct.unpack("L", command[4:8])[0]
                text = bytes_to_text(command[10:-1])
                message["command"] = "reply"
                message["call_id"] = call_id
                message["text"] = text
        
        return message
