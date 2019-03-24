from enum import IntEnum
import struct

class Sensor(IntEnum):
    Unknown = -1
    Accelerometer128MS = 0
    Accelerometer32MS = 1
    AccelerometerGyroscope128MS = 4
    AccelerometerGyroscope32MS = 5
    Distance = 13
    Gsr = 15
    HeartRate = 16
    Pedometer = 19
    SkinTemperature = 20
    UV = 21
    AmbientLight = 25
    RRInterval = 26
    DeviceContact = 35
    BatteryGauge = 38
    UVFast = 40
    Calories1S = 46
    Accelerometer16MS = 48
    AccelerometerGyroscope16MS = 49
    Barometer = 58
    Elevation = 71
    CaloriesWithDailyValues = 107
    ElevationWithDailyValues = 110
    UVWithDailyValues = 111
    AmbientLightWithDailyValues = 112
    Gsr200MS = 113
    LogEntry = 124


class SensorReading():
    subscription_type = Sensor.Unknown
    packet_length = 0
    missed_samples = 0
    sample_size = 0

    def __str__(self):
        return '%s Value: %s' % (
            self.subscription_type, self.value)

    @property
    def header_length(self):
        return 4 + 1 + 1 + 2

    def decode_packet(self, packet):
        self.packet_length, self.missed_samples, self.sample_size = \
            struct.unpack("LxBH", packet[:self.header_length])


class DeviceContactSensor(SensorReading):
    subscription_type = Sensor.DeviceContact

    def decode_packet(self, packet):
        super().decode_packet(packet)
        self.value = packet[self.header_length + 1] == 1


class PedometerSensor(SensorReading):
    subscription_type = Sensor.Pedometer

    def decode_packet(self, packet):
        super().decode_packet(packet)
        self.value = struct.unpack("L", packet[
            self.header_length:self.header_length + self.packet_length])


class HeartRateSensor(SensorReading):
    subscription_type = Sensor.HeartRate
    quality = False

    def decode_packet(self, packet):
        super().decode_packet(packet)
        self.value = packet[self.header_length + 1]
        self.quality = packet[self.header_length + 2] >= 6


class BatteryGaugeSensor(SensorReading):
    subscription_type = Sensor.BatteryGauge
    filtered_voltage = 0
    battery_gauge_alerts = 0

    def decode_packet(self, packet):
        super().decode_packet(packet)
        beginning = self.header_length
        self.filtered_voltage = struct.unpack(
            "H", packet[beginning + 1 : beginning + 2])
        self.battery_gauge_alerts = struct.unpack(
            "H", packet[beginning + 2 : beginning + 4])
        self.value = (packet[beginning + 1] / 10) * 10
        self.value = 100 if self.value > 100 else self.value


def decode_sensor_reading(packet):
    """
    Detect which sensor reading we got and decode it
    """
    subscription_type = packet[6]

    if subscription_type == Sensor.HeartRate:
        sensor = HeartRateSensor()
    elif subscription_type == Sensor.Pedometer:
        sensor = PedometerSensor()
    elif subscription_type == Sensor.DeviceContact:
        sensor = DeviceContactSensor()
    elif subscription_type == Sensor.BatteryGauge:
        sensor = BatteryGaugeSensor()
    else:
        sensor = SensorReading()
    sensor.decode_packet(packet[2:])
    return sensor
