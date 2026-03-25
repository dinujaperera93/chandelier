import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))
from chandelier import parse_schedule, compute_output_points, write_output
from utils import DEFAULT_INPUT, DEFAULT_OUTPUT
from plot import show

def main():
    schedule = parse_schedule(DEFAULT_INPUT)
    points = compute_output_points(schedule)
    write_output(DEFAULT_OUTPUT, points)
    show()

if __name__ == "__main__":
    main()
