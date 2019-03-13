from enum import IntEnum
import struct

class Sensor(IntEnum):
    Unknown = 0
    HeartRate = 16
    Pedometer = 19
    DeviceContact = 35
    BatteryGauge = 38


class SensorReading():
    subscription_type = Sensor.Unknown
    packet_length = 0
    missed_samples = 0
    sample_size = 0

    @property
    def header_length(self):
        return 4 + 1 + 1 + 2

    def decode_packet(self, packet):
        self.packet_length, self.missed_samples, self.sample_size = \
            struct.unpack("LxBH", packet[:self.header_length])


class PedometerSensor(SensorReading):
    subscription_type = Sensor.Pedometer

    def decode_packet(self, packet):
        super().decode_packet(packet)
        self.value = struct.unpack("L", packet[
            self.header_length:self.header_length + self.packet_length])
        print('Pedometer: %d' % self.value)
        