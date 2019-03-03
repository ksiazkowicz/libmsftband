import struct
from datetime import timedelta
from libband.commands import GET_STATISTICS_RUN, GET_STATISTICS_WORKOUT, \
    GET_STATISTICS_SLEEP, GET_STATISTICS_GUIDED_WORKOUT
from libband.parser import MsftBandParser
from .app import App


class MetricsService(App):
    app_name = "Metrics Service"
    guid = None

    # Cached Metrics
    workout = None
    run = None
    sleep = None
    guided_workout = None

    def sync(self):
        # Fetch all metrics from Band
        try:
            self.get_guided_workout()
            self.get_sleep()
            self.get_workout()
            self.get_run()
            return True
        except Exception as error:
            self.band.wrapper.print(error)

    def format_duration(self, duration):
        hours = float(duration)/float(3600000)
        hours_int = int(hours)
        minutes = int((hours - hours_int)*60)
        return "%d:%02d" % (hours_int, minutes)

    def get_run(self):
        result, metrics = self.band.cargo.cargo_read(
            GET_STATISTICS_RUN, 50)

        if not result:
            self.band.wrapper.print("Error occurred")
            return

        data = b"".join(metrics)

        timestamp = MsftBandParser.deserialize_time(struct.unpack("Q", data[:8])[0])
        version = struct.unpack("H", data[8:10])[0]
        duration = struct.unpack("L", data[10:14])[0]
        distance = struct.unpack("L", data[14:18])[0]
        average_pace = struct.unpack("L", data[18:22])[0]
        best_split = struct.unpack("L", data[22:26])[0]
        calories_burned = struct.unpack("L", data[26:30])[0]
        avg_heartrate = struct.unpack("L", data[30:34])[0]
        max_heartrate = struct.unpack("L", data[34:38])[0]
        end_time = MsftBandParser.deserialize_time(struct.unpack("Q", data[38:46])[0])
        feeling = struct.unpack("L", data[46:50])[0]

        self.run = {
            "timestamp": timestamp,
            "version": version,
            "duration": self.format_duration(duration),
            "distance": distance,
            "average_pace": average_pace,
            "best_split": best_split,
            "calories_burned": calories_burned,
            "avg_heartrate": avg_heartrate,
            "max_heartrate": max_heartrate,
            "start_time": end_time - timedelta(milliseconds=duration),
            "end_time": end_time,
            "feeling": feeling,
        }
        return self.run

    def get_workout(self):
        result, metrics = self.band.cargo.cargo_read(
            GET_STATISTICS_WORKOUT, 38)

        if not result:
            self.band.wrapper.print("Error occurred")
            return

        data = b"".join(metrics)

        timestamp = MsftBandParser.deserialize_time(struct.unpack("Q", data[:8])[0])
        version = struct.unpack("H", data[8:10])[0]
        duration = struct.unpack("L", data[10:14])[0]
        calories_burned = struct.unpack("L", data[14:18])[0]
        avg_heartrate = struct.unpack("L", data[18:22])[0]
        max_heartrate = struct.unpack("L", data[22:26])[0]
        end_time = MsftBandParser.deserialize_time(struct.unpack("Q", data[26:34])[0])
        feeling = struct.unpack("L", data[34:38])[0]

        self.workout = {
            "timestamp": timestamp,
            "version": version,
            "duration": self.format_duration(duration),
            "calories_burned": calories_burned,
            "avg_heartrate": avg_heartrate,
            "max_heartrate": max_heartrate,
            "start_time": end_time - timedelta(milliseconds=duration),
            "end_time": end_time,
            "feeling": feeling,
        }
        return self.workout

    def get_guided_workout(self):
        result, metrics = self.band.cargo.cargo_read(
            GET_STATISTICS_GUIDED_WORKOUT, 38)

        if not result:
            self.band.wrapper.print("Error occurred")
            return

        data = b"".join(metrics)

        timestamp = MsftBandParser.deserialize_time(struct.unpack("Q", data[:8])[0])
        version = struct.unpack("H", data[8:10])[0]
        duration = struct.unpack("L", data[10:14])[0]
        calories_burned = struct.unpack("L", data[14:18])[0]
        avg_heartrate = struct.unpack("L", data[18:22])[0]
        max_heartrate = struct.unpack("L", data[22:26])[0]
        end_time = MsftBandParser.deserialize_time(struct.unpack("Q", data[26:34])[0])
        rounds_completed = struct.unpack("L", data[34:38])[0]

        self.guided_workout = {
            "timestamp": timestamp,
            "version": version,
            "duration": self.format_duration(duration),
            "calories_burned": calories_burned,
            "avg_heartrate": avg_heartrate,
            "max_heartrate": max_heartrate,
            "start_time": end_time - timedelta(milliseconds=duration),
            "end_time": end_time,
            "rounds_completed": rounds_completed,
        }
        return self.guided_workout

    def get_sleep(self):
        result, metrics = self.band.cargo.cargo_read(GET_STATISTICS_SLEEP, 54)

        if not result:
            self.band.wrapper.print("Error occurred")
            return

        data = b"".join(metrics)

        timestamp = MsftBandParser.deserialize_time(struct.unpack("Q", data[:8])[0])
        version = struct.unpack("H", data[8:10])[0]
        duration = struct.unpack("L", data[10:14])[0]
        times_woke_up = struct.unpack("L", data[14:18])[0]
        time_awake = struct.unpack("L", data[18:22])[0]
        time_asleep = struct.unpack("L", data[22:26])[0]
        calories_burned = struct.unpack("L", data[26:30])[0]
        resting_heart_rate = struct.unpack("L", data[30:34])[0]
        end_time = MsftBandParser.deserialize_time(struct.unpack("Q", data[38:46])[0])
        time_to_fall_asleep = struct.unpack("L", data[46:50])[0]
        feeling = struct.unpack("L", data[50:54])[0]

        self.sleep = {
            "timestamp": timestamp,
            "version": version,
            "duration": self.format_duration(duration),
            "times_woke_up": times_woke_up,
            "time_awake": self.format_duration(time_awake),
            "time_asleep": self.format_duration(time_asleep),
            "calories_burned": calories_burned,
            "resting_heart_rate": resting_heart_rate,
            "start_time": end_time - timedelta(milliseconds=duration),
            "end_time": end_time,
            "time_to_fall_asleep": self.format_duration(time_to_fall_asleep),
            "feeling": feeling,
        }
        return self.sleep
