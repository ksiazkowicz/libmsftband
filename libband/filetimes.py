import datetime
import struct
import time

WINDOWS_TICKS = int(1/10**-7)  # 10,000,000 (100 nanoseconds or .1 microseconds)
WINDOWS_EPOCH = datetime.datetime.strptime('1601-01-01 00:00:00',
                                           '%Y-%m-%d %H:%M:%S')
POSIX_EPOCH = datetime.datetime.strptime('1970-01-01 00:00:00',
                                         '%Y-%m-%d %H:%M:%S')
EPOCH_DIFF = (POSIX_EPOCH - WINDOWS_EPOCH).total_seconds()  # 11644473600.0
WINDOWS_TICKS_TO_POSIX_EPOCH = EPOCH_DIFF * WINDOWS_TICKS  # 116444736000000000.0

def get_time(filetime):
    """Convert windows filetime winticks to python datetime.datetime."""
    winticks = filetime #struct.unpack('<Q', filetime)[0]
    microsecs = (winticks - WINDOWS_TICKS_TO_POSIX_EPOCH) / WINDOWS_TICKS
    return datetime.datetime.fromtimestamp(int(microsecs))

def convert_back(timestamp_string):
    """Convert a timestamp in Y=M=D H:M:S.f format into a windows filetime."""
    dt = datetime.datetime.strptime(timestamp_string, '%Y-%m-%d %H:%M:%S.%f')
    posix_secs = int(time.mktime(dt.timetuple()))
    winticks = (posix_secs + int(EPOCH_DIFF)) * WINDOWS_TICKS
    return winticks

def int_to_bytes(n, minlen=0):  # helper function
    """ int/long to bytes (little-endian byte order).
        Note: built-in int.to_bytes() method could be used in Python 3.
    """
    nbits = n.bit_length() + (1 if n < 0 else 0)  # plus one for any sign bit
    nbytes = (nbits+7) // 8  # number of whole bytes
    ba = bytearray()
    for _ in range(nbytes):
        ba.append(n & 0xff)
        n >>= 8
    if minlen > 0 and len(ba) < minlen:  # zero pad?
        ba.extend([0] * (minlen-len(ba)))
    return ba  # with low bytes first

def hexbytes(s):  # formatting helper function
    """Convert string to string of hex character values."""
    ba = bytearray(s)
    return ''.join('\\x{:02x}'.format(b) for b in ba)
