from enum import Enum
import json

CONFIG = None

class ConfigKey(str, Enum):
	REP_EXERCISES = "rep_exercises"

def refresh_config():
	global CONFIG
	if CONFIG:
		return None

	with open("config.json", "r") as f:
	    CONFIG = json.load(f)

def get_config(key):
	global CONFIG
	return CONFIG.get(key)