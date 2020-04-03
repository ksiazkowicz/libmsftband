from collections import defaultdict
import struct

from libband import BUFFER_SIZE, TIMEOUT
from libband.socket import BandSocket
from libband.status import decode_status


class MockBandSocket(BandSocket):
    """
    Emulates BandSocket for unit tests.
    """
    _connected = False
    _received_packets = []
    _expected_results = defaultdict(list)

    def _make_socket(self):
        return None

    def call(self, packet=None, results=[]):
        self._expected_results[packet].append(results)

    def connect(self, timeout=TIMEOUT):
        if self._connected:
            raise Exception

        # simulate connection
        self.device.wrapper.send("Status", [self.port, "Connected"])
        self._connected = True

    def disconnect(self):
        if not self._connected:
            raise Exception

        # simulate disconnection
        self.device.wrapper.send("Status", "Disconnected")
        self._connected = False

    def send(self, packet):
        if not self._connected:
            raise Exception
        self._received_packets.append(packet)

    def send_for_result(self, packet, buffer_size=BUFFER_SIZE):
        if not self._connected:
            raise Exception
        self._received_packets.append(packet)

        try:
            results = self._expected_results[packet].pop(0)
        except IndexError:
            results = self._expected_results[None].pop(0)

        last_result = results[-1]
        status = decode_status(struct.unpack("<I", last_result[-4:])[0])
        success = not status.get('is_error', False)
        if not success:
            self.device.wrapper.print("Error: %s" % status)

        if len(last_result) > 6:
            results[-1] = last_result[:-6]
        else:
            results.pop()

        return status, results
