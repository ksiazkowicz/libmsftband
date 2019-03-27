import struct
from .helpers import make_command
from .facilities import Facility


# LibraryTime
SET_DEVICE_TIME = make_command(Facility.LibraryTime, False, 1)
GET_DEVICE_TIME = make_command(Facility.LibraryTime, True, 2)

# ModuleThemeColor
SET_THEME_COLOR = make_command(Facility.ModuleThemeColor, False, 0)

# Fireball UI
READ_ME_TILE_IMAGE = make_command(Facility.ModuleFireballUI, True, 14)
WRITE_ME_TILE_IMAGE_WITH_ID = make_command(
    Facility.ModuleFireballUI, False, 17)
NAVIGATE_TO_SCREEN = make_command(Facility.ModuleFireballUI, False, 0)

# Installed Apps
GET_TILES = make_command(Facility.ModuleInstalledAppList, True, 0)
SET_TILES = make_command(Facility.ModuleInstalledAppList, False, 1)
START_STRIP_SYNC_START = make_command(
    Facility.ModuleInstalledAppList, False, 2)
START_STRIP_SYNC_END = make_command(
    Facility.ModuleInstalledAppList, False, 3)
GET_TILES_DEFAULTS = make_command(Facility.ModuleInstalledAppList, True, 4)
SET_TILE = make_command(Facility.ModuleInstalledAppList, False, 6)
GET_TILE = make_command(Facility.ModuleInstalledAppList, True, 7)
GET_TILE_SETTINGS_MASK = make_command(
    Facility.ModuleInstalledAppList, True, 13)
SET_TILE_SETTINGS_MASK = make_command(
    Facility.ModuleInstalledAppList, False, 14)
TILES_ENABLE_SETTING = make_command(
    Facility.ModuleInstalledAppList, False, 15)
TILES_DISABLE_SETTING = make_command(
    Facility.ModuleInstalledAppList, False, 16)
GET_TILES_NO_IMAGES = make_command(
    Facility.ModuleInstalledAppList, True, 18)
GET_MAX_TILE_COUNT = make_command(
    Facility.ModuleInstalledAppList, True, 21)
GET_MAX_TILE_ALLOCATED_COUNT = make_command(
    Facility.ModuleInstalledAppList, True, 22)

# Cargo Notification
CARGO_NOTIFICATION = make_command(Facility.ModuleNotification, False, 0)

# Library Configuration
SERIAL_NUMBER_REQUEST = make_command(Facility.LibraryConfiguration, True, 8)

# Library Remote Subscription
SUBSCRIBE = make_command(Facility.LibraryRemoteSubscription, False, 0)
UNSUBSCRIBE = make_command(Facility.LibraryRemoteSubscription, False, 1)
SUBSCRIPTION_GET_DATA_LENGTH = make_command(
    Facility.LibraryRemoteSubscription, True, 2)
SUBSCRIPTION_GET_DATA = make_command(
    Facility.LibraryRemoteSubscription, True, 3)
SUBSCRIPTION_SUBSCRIBE_ID = make_command(
    Facility.LibraryRemoteSubscription, False, 7)
SUBSCRIPTION_UNSUBSCRIBE_ID = make_command(
    Facility.LibraryRemoteSubscription, False, 8)

# ModuleProfile
PROFILE_GET_DATA_APP = make_command(Facility.ModuleProfile, True, 6)
PROFILE_SET_DATA_APP = make_command(Facility.ModuleProfile, False, 7)
PROFILE_GET_DATA_FW = make_command(Facility.ModuleProfile, True, 8)
PROFILE_SET_DATA_FW = make_command(Facility.ModuleProfile, False, 9)

# ModuleSystemSettings
GET_ME_TILE_IMAGE_ID = make_command(Facility.ModuleSystemSettings, True, 18)
CARGO_SYSTEM_SETTINGS_OOBE_COMPLETED_GET = make_command(
    Facility.ModuleSystemSettings, True, 19)
CARGO_SYSTEM_SETTINGS_OOBE_COMPLETED_SET = make_command(
    Facility.ModuleSystemSettings, False, 1)

# ModuleOobe
OOBE_SET_STAGE = make_command(
    Facility.ModuleOobe, False, 0)
OOBE_GET_STAGE = make_command(
    Facility.ModuleOobe, True, 1)
OOBE_FINALIZE = make_command(
    Facility.ModuleOobe, False, 2)

# ModulePersistedStatistics
GET_STATISTICS_RUN = make_command(
    Facility.ModulePersistedStatistics, True, 2)
GET_STATISTICS_WORKOUT = make_command(
    Facility.ModulePersistedStatistics, True, 3)
GET_STATISTICS_SLEEP = make_command(
    Facility.ModulePersistedStatistics, True, 4)
GET_STATISTICS_GUIDED_WORKOUT = make_command(
    Facility.ModulePersistedStatistics, True, 5)

# LibraryLogger
GET_CHUNK_COUNTS = make_command(Facility.LibraryLogger, True, 9)
FLUSH_LOG = make_command(Facility.LibraryLogger, False, 13)
GET_CHUNK_RANGE_METADATA = make_command(Facility.LibraryLogger, True, 14)
GET_CHUNK_RANGE_DATA = make_command(Facility.LibraryLogger, True, 15)
DELETE_CHUNK_RANGE = make_command(Facility.LibraryLogger, False, 16)

# LibraryJutil
CORE_GET_VERSION = make_command(Facility.LibraryJutil, True, 1)
CORE_GET_UNIQUE_ID = make_command(Facility.LibraryJutil, True, 2)
CORE_WHO_AM_I = make_command(Facility.LibraryJutil, True, 3)
CORE_GET_LOG_VERSION = make_command(Facility.LibraryJutil, True, 5)
CORE_GET_API_VERSION = make_command(Facility.LibraryJutil, True, 6)
CORE_SDK_CHECK = make_command(Facility.LibraryJutil, False, 7)
