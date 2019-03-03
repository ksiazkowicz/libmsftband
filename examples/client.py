import json

from libband.device import BandDevice
from libband.apps.weather import WeatherService
from libband.apps.time import TimeService
from libband.apps.phone import PhoneService
from libband.apps.metrics import MetricsService
from libband.apps.profile import ProfileService


class ExampleClient:
    device = None
    services = {}

    def call(self, service_name, method, args):
        service = self.services.get(service_name, None)
        if service:
            getattr(service, method)(*args)

    def select_device(self, mac_address):
        """Sets a device, move services to new device"""
        self.device = BandDevice(mac_address)
        if self.services:
            for name, service in self.services.items():
                service.band = self.device
        else:
            time_service = TimeService(self.device)
            weather_service = WeatherService(self.device)
            metrics_service = MetricsService(self.device)
            phone_service = PhoneService(self.device)
            profile_service = ProfileService(self.device)

            self.services = {
                "TimeService": time_service,
                "WeatherApp": weather_service,
                "MetricsApp": metrics_service,
                "PhoneApp": phone_service,
                "ProfileApp": profile_service,
            }
        self.device.services = self.services
        self.device.connect()

    def sync(self):
        if self.device:
            self.device.sync()
            return True
        return False

