import binascii
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
    DistanceWithDailyValues = 108
    PedometerWithDailyValues = 109
    ElevationWithDailyValues = 110
    UVWithDailyValues = 111
    AmbientLightWithDailyValues = 112
    Gsr200MS = 113
    LogEntry = 124


class MotionType(IntEnum):
    Unknown = 0
    Idle = 1
    Walking = 2
    Jogging = 3
    Running = 4


class UVIndexLevel(IntEnum):
    NoUV = 0
    Low = 1
    Medium = 2
    High = 3
    VeryHigh = 4


class SensorReading():
    subscription_type = Sensor.Unknown
    packet_length = 0
    missed_samples = 0
    sample_size = 0
    _packet = b''

    def get_value_verbose(self):
        return binascii.hexlify(self._packet)

    def __str__(self):
        return f'{self.subscription_type}: Value: {self.get_value_verbose()}'

    @property
    def header_length(self):
        return 4 + 1 + 1 + 2

    def decode_packet(self, packet):
        self._packet = packet
        (
            self.packet_length,
            self.subscription_type,
            self.missed_samples,
            self.sample_size
        ) = struct.unpack("LBBH", packet[:self.header_length])


class DeviceContactSensor(SensorReading):
    def get_value_verbose(self):
        return 'Wearing' if self.value else 'Not wearing'

    def decode_packet(self, packet):
        super().decode_packet(packet)
        self.value = packet[self.header_length + 1] == 1


class PedometerSensor(SensorReading):
    def get_value_verbose(self):
        return f'{self.value} steps'

    def decode_packet(self, packet):
        super().decode_packet(packet)
        self.value = struct.unpack(
            "L", packet[self.header_length:self.header_length + 4]
        )[0]


class PedometerSensorWithDailyValues(PedometerSensor):
    def get_value_verbose(self):
        return f'{self.value} steps ({self.value_today} today)'

    def decode_packet(self, packet):
        super().decode_packet(packet)
        self.value, self.value_today = struct.unpack(
            "LL", packet[self.header_length:self.header_length + 8]
        )


class HeartRateSensor(SensorReading):
    quality = False

    def get_value_verbose(self):
        return f'{self.value} ({"Locked" if self.quality else "Acquiring"})'

    def decode_packet(self, packet):
        super().decode_packet(packet)
        self.value, self.quality = struct.unpack(
            'BB', packet[self.header_length:]
        )
        self.quality = self.quality >= 6


class BatteryGaugeSensor(SensorReading):
    filtered_voltage = 0
    battery_gauge_alerts = 0

    def get_value_verbose(self):
        return f'{self.value}%'

    def decode_packet(self, packet):
        super().decode_packet(packet)
        self.value, self.filtered_voltage, self.battery_gauge_alerts = (
            struct.unpack('<BHH', packet[self.header_length:])
        )


class SkinTemperatureSensor(SensorReading):
    def get_value_verbose(self):
        return self.value

    def decode_packet(self, packet):
        super().decode_packet(packet)
        decoded = struct.unpack(f'h{"x"*8}', packet[self.header_length:])[0]
        self.value = decoded / 100.0


class DistanceSensor(SensorReading):
    speed = 0
    pace = 0
    current_motion = MotionType.Idle

    def get_value_verbose(self):
        return f'{self.value} total. Speed: {self.speed}. Pace: {self.pace}'

    def decode_packet(self, packet):
        super().decode_packet(packet)
        self.value, self.speed, self.pace = (
            struct.unpack(f'L{"x"*8}LLxx', packet[self.header_length:])
        )


class DistanceSensorWithDailyValues(DistanceSensor):
    value_today = 0
    current_motion = MotionType.Idle

    def get_value_verbose(self):
        return (
            f'{self.value} total ({self.value_today} today). '
            f'Speed: {self.speed}. Pace: {self.pace}. '
            f'Current Motion: {self.current_motion}'
        )

    def decode_packet(self, packet):
        super().decode_packet(packet)
        (
            self.value,
            self.speed,
            self.pace,
            self.current_motion,
            self.value_today
        ) = struct.unpack(f'LLLBL', packet[self.header_length:])
        self.current_motion = MotionType(self.current_motion)


class AccelerometerSensor(SensorReading):
    def get_value_verbose(self):
        return (
            f'ax: {self.acceleration_x}, ay: {self.acceleration_y} '
            f'az: {self.acceleration_z}'
        )

    def decode_packet(self, packet):
        super().decode_packet(packet)
        ax, ay, az = struct.unpack(
            'hhh',
            packet[self.header_length:self.header_length+6]
        )
        self.acceleration_x = ax * 0.000244140625
        self.acceleration_y = ay * 0.000244140625
        self.acceleration_z = az * 0.000244140625


class AccelerometerGyroscopeSensor(AccelerometerSensor):
    def get_value_verbose(self):
        return (
            f'{super().get_value_verbose()} '
            f'vx: {self.velocity_x}, vy: {self.velocity_y} '
            f'vz: {self.velocity_z}'
        )

    def decode_packet(self, packet):
        super().decode_packet(packet)
        vx, vy, vz = struct.unpack(
            'hhh',
            packet[self.header_length+6:]
        )
        self.velocity_x = vx * 0.030487804878048783
        self.velocity_y = vy * 0.030487804878048783
        self.velocity_z = vz * 0.030487804878048783


class UVSensor(SensorReading):
    def get_value_verbose(self):
        return f'{self.value.name}'

    def decode_packet(self, packet):
        super().decode_packet(packet)
        self.value = UVIndexLevel(
            struct.unpack('xxHxx', packet[self.header_length:])[0]
        )


class AmbientLightSensor(SensorReading):
    def get_value_verbose(self):
        return f'{self.value}'

    def decode_packet(self, packet):
        super().decode_packet(packet)
        self.value = struct.unpack('Hxxxx', packet[self.header_length:])[0]


class Calorie1SSensor(SensorReading):
    def get_value_verbose(self):
        return f'{self.value} cal'

    def decode_packet(self, packet):
        super().decode_packet(packet)
        self.value = struct.unpack(
            f'I{"x"*16}', packet[self.header_length:]
        )[0]


class RRIntervalSensor(SensorReading):
    def get_value_verbose(self):
        return f'{self.value}'

    def decode_packet(self, packet):
        super().decode_packet(packet)
        self.value = struct.unpack(
            f'xxxxH', packet[self.header_length:]
        )[0] * 0.016592


class GsrSensor(SensorReading):
    def get_value_verbose(self):
        return f'{self.value}'

    def decode_packet(self, packet):
        super().decode_packet(packet)
        self.value = struct.unpack('<xIxx', packet[self.header_length:])


def decode_sensor_reading(packet):
    """
    Detect which sensor reading we got and decode it
    """
    subscription_type = packet[6]
    sensor = {
        Sensor.Accelerometer128MS: AccelerometerSensor,
        Sensor.Accelerometer32MS: AccelerometerSensor,
        Sensor.AccelerometerGyroscope128MS: AccelerometerGyroscopeSensor,
        Sensor.AccelerometerGyroscope32MS: AccelerometerGyroscopeSensor,
        Sensor.Distance: DistanceSensor,
        Sensor.Gsr: GsrSensor,
        Sensor.HeartRate: HeartRateSensor,
        Sensor.Pedometer: PedometerSensor,
        Sensor.SkinTemperature: SkinTemperatureSensor,
        Sensor.UV: UVSensor,
        Sensor.AmbientLight: AmbientLightSensor,
        Sensor.DeviceContact: DeviceContactSensor,
        Sensor.BatteryGauge: BatteryGaugeSensor,
        Sensor.UVFast: UVSensor,
        Sensor.Calories1S: Calorie1SSensor,
        Sensor.Accelerometer16MS: AccelerometerSensor,
        Sensor.AccelerometerGyroscope16MS: AccelerometerGyroscopeSensor,
        # MSFT Band 2 Only
        Sensor.RRInterval: RRIntervalSensor,
        # TODO: Barometer
        # TODO: Elevation
        # TODO: Calories With Daily Values
        Sensor.DistanceWithDailyValues: DistanceSensorWithDailyValues,
        Sensor.PedometerWithDailyValues: PedometerSensorWithDailyValues,
        # TODO: Elevation With Daily Values
        # TODO: UV With Daily Values
        # TODO: Ambient Light With Daily Values
        # TODO: Gsr200MS
        # TODO: LogEntry (maybe this one is only on non-production devices?)
    }.get(subscription_type, SensorReading)()
    try:
        sensor.decode_packet(packet[2:])
    except Exception as exc:
        print(binascii.hexlify(packet[2:]))
        print(exc)
    return sensor
