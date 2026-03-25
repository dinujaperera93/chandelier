import os
from datetime import timedelta

HOUR = timedelta(hours=1)
DEFAULT_INPUT = "schedule.csv"
DEFAULT_OUTPUT = os.path.join("output", "output.csv")