import struct
from libband.apps.app import App
from libband.commands import SUBSCRIBE, UNSUBSCRIBE


class SensorStreamService(App):
    app_name = 'Sensor Stream'
    subscriptions = []

    def subscribe(self, subscription_type):
        arguments = struct.pack("Bxxxx", subscription_type)
        result, info = self.band.cargo.cargo_write(SUBSCRIBE, arguments)
        if result:
            self.subscriptions.append(subscription_type)
        return result

    def unsubscribe(self, subscription_type):
        arguments = struct.pack("B", subscription_type)
        result, info = self.band.cargo.cargo_write(UNSUBSCRIBE, arguments)
        if result:
            self.subscriptions.remove(subscription_type)
        return result

    def sync(self):
        # There is actually no sync logic
        return
