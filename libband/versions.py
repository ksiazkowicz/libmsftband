from dataclasses import dataclass
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


@dataclass
class FirmwareVersion:
    app_name: str = ''
    pcb_id: int = 0
    version_major: int = 0
    version_minor: int = 0
    build_number: int = 0
    revision: int = 0
    debug_build: int = 0

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


@dataclass
class DeviceVersion:
    bootloader: FirmwareVersion = FirmwareVersion()
    application: FirmwareVersion = FirmwareVersion()
    updater: FirmwareVersion = FirmwareVersion()

    @property
    def band_type(self):
        if self.bootloader.pcb_id >= 20:
            return BandType.Envoy
        elif self.bootloader.pcb_id == 0:
            return BandType.Unknown
        return BandType.Cargo
