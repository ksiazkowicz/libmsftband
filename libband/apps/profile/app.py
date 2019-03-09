import struct
from datetime import datetime
from libband.commands import PROFILE_GET_DATA_APP, PROFILE_SET_DATA_APP, PROFILE_GET_DATA_FW
from libband.filetimes import datetime_to_filetime
from libband.apps.app import App
from .profile import Profile


class ProfileService(App):
    app_name = "Profile Service"
    guid = None
    profile = None

    def sync(self):
        if not self.profile:
            self.get_profile()
        else:
            self.profile.last_sync = datetime.now()
            self.save_profile()

    def get_profile(self):
        result, info = self.band.cargo.cargo_read(PROFILE_GET_DATA_APP, 128)
        
        if not result:
            return
        self.profile = Profile(info[0])
        return self.profile.__dict__()

    def get_profile_fw(self):
        result, info = self.band.cargo.cargo_read(PROFILE_GET_DATA_FW, 282)
        # TODO: add support for this thing
        # print(result, info)
        return result

    def save_profile(self):
        return self.band.cargo.cargo_write_with_data(
            PROFILE_SET_DATA_APP, self.profile.as_packet())
