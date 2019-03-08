from enum import IntEnum
from .app import App
from libband.notifications import Notification, NotificationTypes
from libband.tiles import CALENDAR
from libband.parser import MsftBandParser
from libband.filetimes import datetime_to_filetime
import struct
import binascii


class CalendarEventAcceptedState(IntEnum):
    Accepted = 0
    Tentative = 1
    Free = 2


class CalendarEventCategory(IntEnum):
    NoSpecialFormatting = 0
    Cancelled = 1


class CalendarEvent(Notification):
    guid = CALENDAR
    notification_type = NotificationTypes.CalendarEventAdd
    title = "Test Event"
    location = ""
    start_time = None
    notification_time = 15
    duration = 60
    all_day = 0
    event_category = CalendarEventCategory.NoSpecialFormatting
    accepted_state = CalendarEventAcceptedState.Accepted

    def __init__(
        self, title, location, start_time, duration, all_day=False, 
        notification_time=15, 
        event_category=CalendarEventCategory.NoSpecialFormatting,
        accepted_state=CalendarEventAcceptedState.Accepted):
        self.title = title
        self.location = location
        self.start_time = start_time
        self.duration = duration
        self.all_day = all_day
        self.notification_time = notification_time
        self.event_category = event_category
        self.accepted_state = accepted_state

    def serialize(self):
        if self.location:
            title = self.title[:20]
            location = self.location[:160]
        else:
            title = ''
            location = self.title[:160]

        packet = super().serialize()
        packet += struct.pack("H", len(title) * 2)
        packet += struct.pack("H", len(location) * 2)
        packet += struct.pack("<Q", datetime_to_filetime(self.start_time))
        packet += struct.pack("H", self.notification_time)
        packet += struct.pack("H", self.duration)
        packet += struct.pack("H", self.accepted_state)
        packet += bytes([self.all_day])
        packet += bytes([self.event_category])
        packet += struct.pack("xx")
        packet += MsftBandParser.serialize_text(title + location)
        return packet


class CalendarService(App):
    app_name = "Calendar Service"
    guid = CALENDAR
    events = []

    def send_events(self):
        self.clear_tile()
        for event in self.events[:8]:
            self.band.send_notification(event)
