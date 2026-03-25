import csv
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

ROOT = Path(__file__).parent.parent


def read_csv(filename):
    with open(ROOT / filename, newline="") as f:
        return [
            (datetime.fromisoformat(row[0].strip().replace("Z", "+00:00")), int(row[1].strip()))
            for row in csv.reader(f)
        ]


def show():
    schedule = read_csv("schedule.csv")
    output = read_csv("output/output.csv")

    out_times, out_heights = zip(*output)
    sched_times, sched_heights = zip(*schedule)

    fig, ax = plt.subplots(figsize=(12, 5))

    # Output curve — piecewise linear motion the chandelier actually follows
    ax.plot(out_times, out_heights, color="steelblue", linewidth=2, label="Output curve (actual motion)")

    # Input schedule — step-wise to show each target level held until the next
    ax.step(sched_times, sched_heights, color="tomato", linewidth=1.5, linestyle="--", where="post", label="Input schedule (target heights)")

    ax.set_title("Chandelier Height Schedule vs Output Motion Curve")
    ax.set_xlabel("Time")
    ax.set_ylabel("Height")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b\n%H:%M"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.4)

    plt.tight_layout()
    plt.savefig(ROOT / "output/curve.png", dpi=150)
    plt.show()
