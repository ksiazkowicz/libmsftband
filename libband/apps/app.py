from libband.notifications import GenericClearTileNotification


class App:
    band = None
    app_name = "App"
    guid = None

    def __init__(self, band):
        self.band = band

    def __str__(self):
        return self.app_name

    def sync(self):
        return True

    def push(self, guid, command, message):
        if self.guid and guid == self.guid:
            return message
        return False

    def clear_tile(self):
        self.band.send_notification(GenericClearTileNotification(self.guid))
