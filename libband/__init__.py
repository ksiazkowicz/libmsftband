import uuid

CARGO_SERVICE_PORT = 4
PUSH_SERVICE_PORT = 5

TIMEOUT = 2

BUFFER_SIZE = 8192

NOTIFICATION_TYPES = {
    "Sms": b"\x01\x00",
    "Email": b"\x02\x00",
    "IncomingCall": b"\x0B\x00",
    "AnsweredCall": b"\x0c\x00",
    "MissedCall": b"\x0D\x00",
    "HangupCall": b"\x0E\x00",
    "Voicemail": b"\x0F\x00",
    "CalendarEventAdd": b"\x10\x00",
    "CalendarClear": b"\x11\x00",
    "Messaging": b"\x12\x00",
    "GenericDialog": b"\x64\x00",
    "GenericUpdate": b"\x65\x00",
    "GenericClearTile": b"\x66\x00",
    "GenericClearPage": b"\x67\x00"
}

OPENCAGE_KEY = ''
