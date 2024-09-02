import json
from datetime import datetime

import os

import numpy as np

from Oanda.settings import BASE_DIR, STATS_DUMP_PATH

durations = {

}
call_timestamps = {

}

possible_state_visits = []
valid_actions = []
prediction_inputs = []

stat_dump_path = STATS_DUMP_PATH

if not os.path.exists(stat_dump_path):
	print("Creating stats dump...")
	os.makedirs(stat_dump_path)


def track_stats(key, func):
	start_time = datetime.now()
	rv = func()
	call_timestamps[key] = call_timestamps.get(key, []) + [datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")]
	durations[key] = durations.get(key, []) + [(datetime.now() - start_time).total_seconds()]

	with open(stat_dump_path, "w") as f:
		json.dump({
			"durations": {
				key: {
					"total": sum(durations[key]),
					"avg": float(np.mean(durations[key])),
					"iterations": len(durations[key]),
					"values": durations[key],
					"timestamps": call_timestamps[key]
				}
				for key in durations
			},

		}, f)

	return rv


def track_func(key):
	def decorator(func):
		def wrapper(*args, **kwargs):
			return track_stats(key, lambda: func(*args, **kwargs))
		return wrapper
	return decorator
