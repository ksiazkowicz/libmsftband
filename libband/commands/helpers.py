import struct
import binascii
from libband.commands.facilities import Facility


def lookup_packet(packet):
    """
    Analyzes command sent to MSFT Band (from Bluetooth HCI log for example)
    and spits out all the parameters, for example - which command it is,
    how much data it expects in return, what arguments are being passed
    """
    binary_packet = binascii.unhexlify(packet)
    command_part_start = binary_packet.index(struct.pack("<H", 12025)) + 2
    command = binary_packet[command_part_start:command_part_start+2]
    
    data_stage_size = struct.unpack(
        "<I", binary_packet[command_part_start+2:command_part_start+6])
    
    arguments = binary_packet[command_part_start+6:]
    
    return {
        'command': lookup_command(struct.unpack("<H", command)[0]), 
        'data_stage_size': data_stage_size,
        'arguments': arguments
    }


def lookup_command(command):
    """
    Splits command encoded as ushort into Facility, TX bit and index
    """
    category = Facility((command & 65280) >> 8)
    is_tx_command = (command & 128) >> 7 == 1
    index = (command & 127)
    return category, is_tx_command, index


def make_command(facility, is_tx, index):
    """
    Given Facility, TX bit and index, spits out command encoded as ushort
    """
    # make command
    command = facility.value << 8 | int(is_tx) << 7 | index
    return command
