import pytest
from libband.tests.utils import MockBandSocket


@pytest.fixture(autouse=True)
def mock_band(mocker):
    mocker.patch('libband.device.BandSocket', MockBandSocket)
    mocker.patch('libband.socket.BandSocket', MockBandSocket)
