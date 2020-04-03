import pytest

from libband.commands.facilities import Facility
from libband.device import BandDevice
from libband.screens import BandScreens
from libband.versions import BandType, DeviceVersion, FirmwareVersion


@pytest.fixture
def cargo():
    device = BandDevice('ab:cd:ef:gh')
    # CORE_GET_VERSION command
    # App version 10.3.3304.0 R
    # Band Type: Cargo
    # Bootloader 10.2.2430.0 R
    # Updater: 10.3.3304.0 R
    device.cargo.call(
        packet=b'\x0c\xf9.\x81v9\x00\x00\x009\x00\x00\x00',
        results=[
            b'1BL\x00\x00\t\n\x00\x02\x00\x00\x00\x00\x00~\t\x00\x00\x002UP'
            b'\x00\x00\t\n\x00\x03\x00\x00\x00\x00\x00\xe8\x0c\x00\x00\x00'
            b'App\x00\x00\t\n\x00\x03\x00\x00\x00\x00\x00\xe8\x0c\x00\x00\x00',
            b'\xfe\xa6\x00\x00\x00\x00'
        ]
    )

    # Checks if OOBE is completed - it is
    device.cargo.call(
        packet=b'\x0c\xf9.\x93\xca\x04\x00\x00\x00\x04\x00\x00\x00',
        results=[
            b'\x01\x00\x00\x00',
            b'\xfe\xa6\x00\x00\x00\x00'
        ]
    )
    return device


@pytest.fixture
def connected_cargo(cargo):
    cargo.connect()
    return cargo


def test_get_firmware_version(connected_cargo):
    connected_cargo.cargo.call(
        packet=b'\x0c\xf9.\x81v9\x00\x00\x009\x00\x00\x00',
        results=[
            b'1BL\x00\x00\t\n\x00\x02\x00\x00\x00\x00\x00~\t\x00\x00\x002UP'
            b'\x00\x00\t\n\x00\x03\x00\x00\x00\x00\x00\xe8\x0c\x00\x00\x00'
            b'App\x00\x00\t\n\x00\x03\x00\x00\x00\x00\x00\xe8\x0c\x00\x00\x00',
            b'\xfe\xa6\x00\x00\x00\x00'
        ]
    )

    connected_cargo.get_firmware_version()
    assert connected_cargo.version == DeviceVersion(
        application=FirmwareVersion(
            app_name='App',
            version_major=10,
            version_minor=3,
            build_number=3304,
            revision=0,
            pcb_id=9
        ),
        updater=FirmwareVersion(
            app_name='2UP',
            version_major=10,
            version_minor=3,
            build_number=3304,
            revision=0,
            pcb_id=9
        ),
        bootloader=FirmwareVersion(
            app_name='1BL',
            version_major=10,
            version_minor=2,
            build_number=2430,
            revision=0,
            pcb_id=9
        )
    )


def test_band_type(connected_cargo):
    assert connected_cargo.band_type == BandType.Cargo


def test_navigate_to_screen(connected_cargo):
    expected_packet = b'\x0c\xf9.\x81v9\x00\x00\x009\x00\x00\x00'
    connected_cargo.cargo.call(results=[b'\xfe\xa6\x02\x00\xc3\xa0'])
    assert connected_cargo.navigate_to_screen(BandScreens.SleepCompleted) == (
        {
            'is_error': True,
            'facility': Facility.ModuleFireballUI,
            'code': 2
        },
        []
    )
    assert expected_packet in connected_cargo.cargo._received_packets
