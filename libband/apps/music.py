import struct
import uuid
from .app import App
from libband import NOTIFICATION_TYPES, layouts
from libband.commands import PUSH_NOTIFICATION, FACILITIES, make_command
from libband.tiles import MUSIC_CONTROL


NOW_PLAYING_PAGE = uuid.UUID("132e8f71-04a1-40e1-8d92-6e15214a80e2")
CONTROLS_PAGE = uuid.UUID("84c43f9d-90c9-4efb-8aa6-d673617d3ac4")
VOLUME_PAGE = uuid.UUID("545024f9-ccec-4962-8c21-e3835cf6b506")


class MusicService(App):
    app_name = "Music Service"
    guid = MUSIC_CONTROL

    def metadata_update(self, title, artist, album):
        update_prefix = NOTIFICATION_TYPES["GenericUpdate"]
        update_prefix += MUSIC_CONTROL.bytes_le

        success = False

        pages = [
            layouts.MusicControlLayout.serialize_as_update(CONTROLS_PAGE),
            layouts.NowPlayingLayout.serialize_as_update(NOW_PLAYING_PAGE, {
                "title": title[:25], "artist": artist[:25], "album": album[:25]
            }),
            layouts.VolumeButtonsLayout.serialize_as_update(VOLUME_PAGE),
        ]

        for page in pages:
            page_update = update_prefix + page
            self.band.cargo.send(
                PUSH_NOTIFICATION + struct.pack("<i", len(page_update)))

            success, result = self.band.cargo.send_for_result(page_update)
        return success

    def push(self, guid, command, message):
        message = super().push(guid, command, message)
        if message:
            try:
                button_id = struct.unpack("H", command[-2:])[0]
            except:
                # can't unpack button ID
                return
            if CONTROLS_PAGE.bytes_le in command:
                button = layouts.MusicControlLayout.get_key(button_id)
                message["command"] = button
            elif VOLUME_PAGE.bytes_le in command:
                button = layouts.VolumeButtonsLayout.get_key(button_id)
                message["command"] = button
        
        return message
