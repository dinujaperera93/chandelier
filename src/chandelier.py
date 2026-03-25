import csv
import os
from datetime import datetime, timedelta, timezone
from typing import List, Tuple
from utils import HOUR

# A single point in the motion curve: (timestamp, height)
Point = Tuple[datetime, int]

def parse_schedule(filename: str) -> List[Point]:
    """Return the hourly schedule sorted by timestamp."""
    with open(filename, newline="") as handle:
        entries = [
            (datetime.fromisoformat(row[0].strip().replace("Z", "+00:00")), int(row[1].strip()))
            for row in csv.reader(handle)
        ]
    return sorted(entries, key=lambda item: item[0])


def compute_output_points(schedule: List[Point]) -> List[Point]:
    """
    Expand an hourly schedule into the minimal set of points that describe the
    chandelier's actual motion once the motor's speed limit is applied.
    """
    points: List[Point] = [schedule[0]]

    for current, upcoming in zip(schedule, schedule[1:]):
        current_height = current[1]
        next_time, next_height = upcoming
        height_change = next_height - current_height

        # If the height doesn't change, no movement is needed
        if height_change == 0:
            continue

        # Each unit of height takes 1 minute to travel, so a change of N units
        # takes N minutes total, split evenly before and after the target time
        half_move = timedelta(minutes=abs(height_change) / 2)
        # Hold at the current height until the ramp begins
        points.append((next_time - half_move, current_height))
        # Arrive at the new height after the ramp ends
        points.append((next_time + half_move, next_height))

    last_time, last_height = schedule[-1]
    # Hold the final height for one hour after the last scheduled entry
    points.append((last_time + HOUR, last_height))

    return _remove_redundant_points(points)


def _remove_redundant_points(points: List[Point]) -> List[Point]:
    """ 
    Walk through triples; drop the middle point if it lies on the same
    straight line as its neighbours as it adds no information to the curve 
    """
    simplified: List[Point] = [points[0]]

    for middle, following in zip(points[1:-1], points[2:]):
        previous = simplified[-1]
        if not _on_same_line(previous, middle, following):
            simplified.append(middle)

    simplified.append(points[-1])
    return simplified


def _on_same_line(p1: Point, p2: Point, p3: Point) -> bool:
    # Check collinearity via cross-multiplication:
    seconds_12 = int((p2[0] - p1[0]).total_seconds())
    seconds_23 = int((p3[0] - p2[0]).total_seconds())
    return (p2[1] - p1[1]) * seconds_23 == (p3[1] - p2[1]) * seconds_12


def write_output(filename: str, points: List[Point]) -> None:
    # Write the computed points as ISO timestamps.
    directory = os.path.dirname(filename)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(filename, "w", newline="") as handle:
        for timestamp, height in points:
            ts = timestamp.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            handle.write(f"{ts}, {height}\n")