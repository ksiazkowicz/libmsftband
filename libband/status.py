from libband.commands import Facility


def make_status(is_error, facility, code, custom=False):
    return int(is_error) << 31 \
        | 536870912 if custom else 0 \
        | facility << 16 \
        | code


def decode_status(error_code):
    is_error = (error_code & 2147483648) >> 31 == 1
    facility = (error_code & 134152192) >> 16
    code = (error_code & 65535)
    return {
        'is_error': is_error,
        'facility': Facility(facility),
        'code': code
    }


def is_severity_error(status):
    return (status & 2147483648) > 0

