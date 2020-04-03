import pytest

from libband.commands.facilities import Facility
from libband.commands.helpers import (
    lookup_command, make_command, lookup_packet
)

EXAMPLE_COMMANDS = [
    # GET_TILES
    (54400, Facility.ModuleInstalledAppList, True, 0),
    # SET_THEME_COLOR
    (55296, Facility.ModuleThemeColor, False, 0),
    # SUBSCRIPTION_UNSUBSCRIBE_ID
    (36616, Facility.LibraryRemoteSubscription, False, 8)
]


@pytest.mark.parametrize(
    ('command', 'facility', 'tx', 'index'), EXAMPLE_COMMANDS
)
def test_lookup_command(command, facility, tx, index):
    assert lookup_command(command) == (facility, tx, index)


@pytest.mark.parametrize(
    ('command', 'facility', 'tx', 'index'), EXAMPLE_COMMANDS
)
def test_make_command(command, facility, tx, index):
    assert make_command(facility, tx, index) == command


@pytest.mark.parametrize(
    ('packet', 'expected_result'),
    [
        (
            '08f92e837601000000',
            {
                'arguments': b'',
                'command': (Facility.LibraryJutil, True, 3),
                'data_stage_size': 1
            }
        ),
        (
            '08f92e88780c000000',
            {
                'arguments': b'',
                'command': (Facility.LibraryConfiguration, True, 8),
                'data_stage_size': 12
            }
        ),
        (
            '0cf92e86c58000000080000000',
            {
                'arguments': b'\x80\x00\x00\x00',
                'command': (Facility.ModuleProfile, True, 6),
                'data_stage_size': 128
            }
        )
    ]
)
def test_lookup_packet(packet, expected_result):
    assert lookup_packet(packet) == expected_result
