from datetime import datetime
from pathlib import Path
import pytest
from chandelier import parse_schedule, compute_output_points, write_output

# Create timezone-aware datetimes from ISO strings concisely
def dt(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))

def test_single_entry():
    # A single entry should produce itself plus a hold point 1 hour later
    result = compute_output_points([(dt("2025-01-01T01:00:00Z"), 10)])
    assert result == [
        (dt("2025-01-01T01:00:00Z"), 10),
        (dt("2025-01-01T02:00:00Z"), 10),
    ]

def test_same_height_no_transition():
    # When height doesn't change, no ramp points are inserted
    schedule = [
        (dt("2025-01-01T01:00:00Z"), 10),
        (dt("2025-01-01T02:00:00Z"), 10),
    ]
    result = compute_output_points(schedule)
    assert result == [
        (dt("2025-01-01T01:00:00Z"), 10),
        (dt("2025-01-01T03:00:00Z"), 10),
    ]

def test_rise_by_five():
    # diff=5 --- half_move=2.5 min; ramp centred on 02:00 -- 01:57:30 to 02:02:30
    schedule = [
        (dt("2025-01-01T01:00:00Z"), 10),
        (dt("2025-01-01T02:00:00Z"), 15),
    ]
    result = compute_output_points(schedule)
    assert result == [
        (dt("2025-01-01T01:00:00Z"), 10),
        (dt("2025-01-01T01:57:30Z"), 10),
        (dt("2025-01-01T02:02:30Z"), 15),
        (dt("2025-01-01T03:00:00Z"), 15),
    ]

def test_fall_by_two():
    # diff=2 --- half_move=1 min; ramp centred on 04:00 -- 03:59 to 04:01
    schedule = [
        (dt("2025-01-01T03:00:00Z"), 15),
        (dt("2025-01-01T04:00:00Z"), 13),
    ]
    result = compute_output_points(schedule)
    assert result == [
        (dt("2025-01-01T03:00:00Z"), 15),
        (dt("2025-01-01T03:59:00Z"), 15),
        (dt("2025-01-01T04:01:00Z"), 13),
        (dt("2025-01-01T05:00:00Z"), 13),
    ]

def test_problem_example():
    # Full four-entry schedule: rise then hold then fall
    schedule = [
        (dt("2025-01-01T01:00:00Z"), 10),
        (dt("2025-01-01T02:00:00Z"), 15),
        (dt("2025-01-01T03:00:00Z"), 15),
        (dt("2025-01-01T04:00:00Z"), 13),
    ]
    result = compute_output_points(schedule)
    assert result == [
        (dt("2025-01-01T01:00:00Z"), 10),
        (dt("2025-01-01T01:57:30Z"), 10),
        (dt("2025-01-01T02:02:30Z"), 15),
        (dt("2025-01-01T03:59:00Z"), 15),
        (dt("2025-01-01T04:01:00Z"), 13),
        (dt("2025-01-01T05:00:00Z"), 13),
    ]

def test_touching_transitions_simplified():
    # Two back-to-back ramps of diff=60 each produce a single straight line,
    # so the middle join point is removed by the simplification step
    schedule = [
        (dt("2025-01-01T01:00:00Z"), 0),
        (dt("2025-01-01T02:00:00Z"), 60),
        (dt("2025-01-01T03:00:00Z"), 120),
    ]
    result = compute_output_points(schedule)
    assert result == [
        (dt("2025-01-01T01:00:00Z"), 0),
        (dt("2025-01-01T01:30:00Z"), 0),
        (dt("2025-01-01T03:30:00Z"), 120),
        (dt("2025-01-01T04:00:00Z"), 120),
    ]

def test_write_output_creates_directory(tmp_path):
    # write_output must create any missing parent directories automatically
    points = [(dt("2025-01-01T01:00:00Z"), 10)]
    out = str(tmp_path / "output" / "output.csv")
    write_output(out, points)
    with open(out) as f:
        assert f.read().strip() == "2025-01-01T01:00:00Z, 10"

def test_parse_schedule(tmp_path):
    # parse_schedule must read the CSV and return entries sorted by timestamp
    csv_file = tmp_path / "schedule.csv"
    csv_file.write_text("2025-01-01T01:00:00Z, 10\n2025-01-01T02:00:00Z, 15\n")
    result = parse_schedule(str(csv_file))
    assert result == [
        (dt("2025-01-01T01:00:00Z"), 10),
        (dt("2025-01-01T02:00:00Z"), 15),
    ]
