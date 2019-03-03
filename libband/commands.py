import struct

FACILITIES = {
    "CargoNotification": b"\xcc",
    "ModuleInstalledAppList": b"\xd4",
    "LibraryTime": b"\x75",
    "LibraryConfiguration": b'\x78',
    "LibraryBattery": b'\x7D',
    "LibraryPedometer": b'\x88',
    "LibraryRemoteSubscription": b"\x8f",
    "LibraryKeyboard": b'\x9f',
    "ModuleOobe": b'\xAD',
    "ModuleProfile": b'\xc5',
    "ModuleThemeColor": b'\xd8',
    "ModuleFireballUI": b'\xC3',
    "ModulePersistedStatistics": b'\xCE',
}


def make_command(facility, is_tx, index, prefix=b"\x08"):
    # TX bit, 2 bytes
    tx_bit = b"\x01\x00" if is_tx else b"\x00\x00"
    tx_int = struct.unpack('<H', tx_bit)[0]

    # category, for example Notifications, encoded as 2 bytes
    facility += (2 - len(facility)) * b"\x00"
    facility_int = struct.unpack('<H', facility)[0]

    # make command
    command = facility_int << 8 | tx_int << 7 | index

    return prefix + b"\xf9\x2e" + struct.pack("<H", command)

# ModuleThemeColor
SET_THEME_COLOR = make_command(
    FACILITIES["ModuleThemeColor"], False, 0) + struct.pack("<I", 24)

# Fireball UI
READ_ME_TILE_IMAGE = make_command(
    FACILITIES["ModuleFireballUI"], True, 14, b"\x0c") + struct.pack("<I", 0)
WRITE_ME_TILE_IMAGE_WITH_ID = make_command(
    FACILITIES["ModuleFireballUI"], False, 17, b"\x0c") + struct.pack("<I", 0)

# Installed Apps
START_STRIP_SYNC_START = make_command(
    FACILITIES["ModuleInstalledAppList"], False, 2) + struct.pack("<I", 0)
START_STRIP_SYNC_END = make_command(
    FACILITIES["ModuleInstalledAppList"], False, 3) + struct.pack("<I", 0)
GET_TILES_NO_IMAGES = make_command(
    FACILITIES["ModuleInstalledAppList"], True, 18) + struct.pack("<I", 1324)

# Cargo Notification
PUSH_NOTIFICATION = make_command(
    FACILITIES["CargoNotification"], False, 0)

# Library Configuration
SERIAL_NUMBER_REQUEST = make_command(
    FACILITIES["LibraryConfiguration"], True, 8) + struct.pack("<I", 12)

# Library Remote Subscription
SUBSCRIBE = make_command(FACILITIES["LibraryRemoteSubscription"], False, 0, b"\x0d")

# ModuleProfile
PROFILE_GET_DATA_APP = make_command(
    FACILITIES["ModuleProfile"], True, 6, b"\x0c") + 2*struct.pack("<I", 128)
PROFILE_SET_DATA_APP = make_command(
    FACILITIES["ModuleProfile"], True, 7, b"\x0c") + 2*struct.pack("<I", 128)
PROFILE_GET_DATA_FW = make_command(
    FACILITIES["ModuleProfile"], True, 8, b"\x0c") + 2*struct.pack("<I", 128)
PROFILE_SET_DATA_FW = make_command(
    FACILITIES["ModuleProfile"], True, 9, b"\x0c") + 2*struct.pack("<I", 128)

# ModuleOobe
OOBE_SET_STAGE = make_command(
    FACILITIES["ModuleOobe"], False, 0)
OOBE_GET_STAGE = make_command(
    FACILITIES["ModuleOobe"], True, 1)
OOBE_FINALIZE = make_command(
    FACILITIES["ModuleOobe"], False, 2)

# ModulePersistedStatistics
GET_STATISTICS_RUN = make_command(
    FACILITIES["ModulePersistedStatistics"], True, 2)
GET_STATISTICS_WORKOUT = make_command(
    FACILITIES["ModulePersistedStatistics"], True, 3)
GET_STATISTICS_SLEEP = make_command(
    FACILITIES["ModulePersistedStatistics"], True, 4)
GET_STATISTICS_GUIDED_WORKOUT = make_command(
    FACILITIES["ModulePersistedStatistics"], True, 5)
