import struct
from datetime import datetime
from .app import App
from libband.tiles import CALLS
from libband.helpers import bytes_to_text
from libband.parser import MsftBandParser
from libband.filetimes import datetime_to_filetime
from libband.notifications import Notification, NotificationTypes


class CallNotification(Notification):
    datetime = None
    call_id = None
    caller = 'Test Caller'

    def __init__(self, guid, call_id, caller):
        self.guid = guid
        self.call_id = call_id
        self.caller = caller
        self.datetime = datetime.now()

    def serialize(self):
        caller = self.caller[:20]
        packet = super().serialize()
        packet += struct.pack("H", len(caller) * 2)
        packet += struct.pack("L", self.call_id)
        packet += struct.pack("<Qxx", datetime_to_filetime(self.datetime))
        packet += MsftBandParser.serialize_text(caller)
        return packet


class IncomingCallNotification(CallNotification):
    notification_type = NotificationTypes.IncomingCall


class MissedCallNotification(CallNotification):
    notification_type = NotificationTypes.MissedCall


class AnsweredCallNotification(CallNotification):
    notification_type = NotificationTypes.AnsweredCall


class HangupCallNotification(CallNotification):
    notification_type = NotificationTypes.HangupCall


class VoicemailNotification(CallNotification):
    notification_type = NotificationTypes.Voicemail


class PhoneService(App):
    app_name = "Phone Service"
    guid = CALLS

    def answered_call(self, call_id, caller):
        self.band.send_notification(AnsweredCallNotification(
            self.guid, call_id, caller))

    def incoming_call(self, call_id, caller):
        self.band.send_notification(IncomingCallNotification(
            self.guid, call_id, caller))

    def missed_call(self, call_id, caller):
        self.band.send_notification(MissedCallNotification(
            self.guid, call_id, caller))

    def hangup_call(self, call_id, caller):
        self.band.send_notification(HangupCallNotification(
            self.guid, call_id, caller))

    def voicemail(self, call_id, caller):
        self.band.send_notification(VoicemailNotification(
            self.guid, call_id, caller))

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
