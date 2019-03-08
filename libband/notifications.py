from enum import IntEnum
import struct
from .parser import MsftBandParser
from datetime import datetime
from .filetimes import datetime_to_filetime


class NotificationTypes(IntEnum):
    """Complete list of all Notification types"""
    SMS = 1
    Email = 2
    IncomingCall = 11
    AnsweredCall = 12
    MissedCall = 13
    HangupCall = 14
    Voicemail = 15
    CalendarEventAdd = 16
    CalendarClear = 17
    Messaging = 18
    GenericDialog = 100
    GenericUpdate = 101
    GenericClearTile = 102
    GenericClearPage = 103
    

class Notification:
    guid = None
    notification_type = NotificationTypes.GenericDialog

    def serialize(self):
        return struct.pack("<H", self.notification_type) + self.guid.bytes_le


class MessagingNotification(Notification):
    notification_type = NotificationTypes.Messaging
    datetime = None

    def __init__(self, guid, title='', text=''):
        self.guid = guid
        self.title = title[:20]
        self.text = text[:20]
        self.datetime = datetime.now()
    
    def serialize(self):
        packet = super().serialize()
        packet += struct.pack("H", len(self.title) * 2)
        packet += struct.pack("H", len(self.text) * 2)
        packet += struct.pack("<Qxx", datetime_to_filetime(self.datetime))
        packet += MsftBandParser.serialize_text(self.title + self.text)
        return packet


class GenericClearTileNotification(Notification):
    notification_type = NotificationTypes.GenericClearTile

    def __init__(self, guid):
        self.guid = guid