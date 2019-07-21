import os
import struct

from libband.commands import (
    GET_CHUNK_COUNTS, GET_CHUNK_RANGE_DATA, GET_CHUNK_RANGE_METADATA,
    DELETE_CHUNK_RANGE, FLUSH_LOG
)
from .app import App


class SensorLogService(App):
    app_name = 'Sensor Log'
    log_path = 'logs'

    def flush_log(self):
        return self.band.cargo.cargo_write(FLUSH_LOG)

    def delete_chunk_range(self, metadata):
        arguments = struct.pack("<III", *metadata)
        return self.band.cargo.cargo_write_with_data(
            DELETE_CHUNK_RANGE, arguments
        )

    def get_remaining_chunks(self):
        result, counts = self.band.cargo.cargo_read(GET_CHUNK_COUNTS, 8)
        if counts:
            return struct.unpack("<I", counts[0][:4])[0]
        return 0

    def get_chunk_range_metadata(self, chunk_count):
        arguments = struct.pack("<I", chunk_count)
        result, range_metadata = self.band.cargo.cargo_read(
            GET_CHUNK_RANGE_METADATA, 12, arguments
        )
        if range_metadata:
            starting_seq, ending_seq, byte_count = struct.unpack(
                "<III", range_metadata[0]
            )
            return starting_seq, ending_seq, byte_count
        return None

    def get_chunk_range_data(self, metadata):
        arguments = struct.pack("<III", *metadata)
        result, range_data = self.band.cargo.cargo_read(
            GET_CHUNK_RANGE_DATA, metadata[2], arguments
        )
        return result, range_data

    def fetch_sensor_log(self, max_chunk_count=128):
        """
        Fetches sensor log from device (max 128 chunks)
        """
        # prepare variable for storing sensor log
        sensor_log = {}

        # attempt to flush log, prepares device for sending sensor log dump
        flushed = False
        while not flushed:
            flushed = self.flush_log()

        # while there are chunks remaining, fetch them and remove from device
        remaining_chunks = self.get_remaining_chunks()
        while remaining_chunks > 0:
            # calculate how many chunks we should fetch
            chunks_to_fetch = min(max_chunk_count, remaining_chunks)

            # get metadata for given chunk
            metadata = self.get_chunk_range_metadata(chunks_to_fetch)
            starting_seq, ending_seq, _ = metadata

            # fetch chunk from Band
            result, log = self.get_chunk_range_data(metadata)

            # write to sensor log dict
            sensor_log[f'{starting_seq}-{ending_seq}'] = b''.join(log)
            remaining_chunks -= chunks_to_fetch

            # remove chunk from device
            self.delete_chunk_range(metadata)
        return sensor_log

    def sync(self):
        """
        Fetches sensor log from device and saves it in specified
        path (self.log_path) under `{starting_seq}-{ending_seq}.log`
        filename
        """
        # create path for sensor log if doesn't exist
        if not os.path.exists(self.log_path):
            os.mkdir(self.log_path)

        sensor_log = self.fetch_sensor_log()
        for metadata, log in sensor_log.items():
            log_path = f'{self.log_path}/{metadata}.log'
            f = open(log_path, 'wb')
            f.write(log)
            f.close()
        return True
