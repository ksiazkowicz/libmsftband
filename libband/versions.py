from enum import IntEnum
import struct


class BandType(IntEnum):
    """
    MSFT Band device types

    Cargo - MSFT Band 1
    Envoy - MSFT Band 2
    """
    Unknown = 0
    Cargo = 1
    Envoy = 2


class FirmwareVersion:
    app_name = ''
    pcb_id = 0
    version_major = 0
    version_minor = 0
    build_number = 0
    revision = 0
    debug_build = 0

    @staticmethod
    def deserialize(packet):
        version = FirmwareVersion()
        version.app_name = packet[:5].rstrip(b'\0').decode('utf-8')
        (
            version.pcb_id, version.version_major, version.version_minor,
            version.revision, version.build_number, version.debug_build
        ) = struct.unpack('<BHHIIB', packet[5:19])
        return version

    def __repr__(self):
        return (
            f'{self.version_major}.{self.version_minor}.{self.build_number}.'
            f'{self.revision} {"D" if self.debug_build else "R"}'
        )


class DeviceVersion:
    bootloader = FirmwareVersion()
    application = FirmwareVersion()
    updater = FirmwareVersion()

    @property
    def band_type(self):
        if self.bootloader.pcb_id >= 20:
            return BandType.Envoy
        elif self.bootloader.pcb_id == 0:
            return BandType.Unknown
        return BandType.Cargo
