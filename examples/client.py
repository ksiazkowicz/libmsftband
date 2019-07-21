from libband.device import BandDevice
from libband.apps import (
    WeatherService, TimeService, PhoneService, MetricsService, ProfileService,
    CalendarService, SensorLogService, SensorStreamService
)


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
            self.services = {
                Service.__name__: Service(self.device)
                for Service in (
                    TimeService, WeatherService, MetricsService, PhoneService,
                    ProfileService, CalendarService, SensorLogService,
                    SensorStreamService
                )
            }
        self.device.services = self.services
        self.device.connect()

    def sync(self):
        if self.device:
            self.device.sync()
            return True
        return False
