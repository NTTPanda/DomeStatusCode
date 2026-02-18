import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ---------------------------------------------------
# STEP 1: Paste ALL your JSON lines here
# ---------------------------------------------------

raw_text = """
{"binning": "4x4", "exposure": 1.264717, "extra_headers": {"TANGLE0": [110.20126952095305, ""], "TANGLE1": [-21.061513318370327, ""], "TSTRKLEN": [30, ""]}}
{"binning": "4x4", "exposure": 1.264504, "extra_headers": {"TANGLE0": [110.48395692575907, ""], "TANGLE1": [-21.475876364295015, ""], "TSTRKLEN": [30, ""]}}
{"binning": "4x4", "exposure": 1.264305, "extra_headers": {"TANGLE0": [110.76815462267832, ""], "TANGLE1": [-21.889829724408415, ""], "TSTRKLEN": [29, ""]}}
{"binning": "4x4", "exposure": 1.264122, "extra_headers": {"TANGLE0": [111.05390224141341, ""], "TANGLE1": [-22.303361144898417, ""], "TSTRKLEN": [29, ""]}}
{"binning": "4x4", "exposure": 1.263954, "extra_headers": {"TANGLE0": [111.3067210571545, ""], "TANGLE1": [-22.666977078772938, ""], "TSTRKLEN": [29, ""]}}
"""

# ---------------------------------------------------
# STEP 2: Parse + Clean + Sort
# ---------------------------------------------------

frames = []
seen = set()

for line in raw_text.strip().split("\n"):
    data = json.loads(line)

    exposure = data["exposure"]
    headers = data["extra_headers"]

    t0 = headers["TANGLE0"][0]
    t1 = headers["TANGLE1"][0]
    streak = headers["TSTRKLEN"][0]

    # Convert negative angle
    if t1 < 0:
        t1 = 360 + t1

    key = (exposure, t0, t1, streak)

    if key not in seen:
        seen.add(key)
        frames.append(key)

# Sort by exposure (time order)
frames.sort(reverse=True)

# Convert to radians
frames = [
    (np.deg2rad(t0), np.deg2rad(t1), streak)
    for _, t0, t1, streak in frames
]

# ---------------------------------------------------
# STEP 3: Setup Plot
# ---------------------------------------------------

fig = plt.figure()
ax = plt.subplot(111, polar=True)
ax.set_ylim(0, 35)
ax.set_title("Multi-Frame Polar Motion (With Trail)")

point0, = ax.plot([], [], 'o')
point1, = ax.plot([], [], 'o')

trail0, = ax.plot([], [])
trail1, = ax.plot([], [])

angles0_history = []
angles1_history = []
radius_history = []

# ---------------------------------------------------
# STEP 4: Animation Function
# ---------------------------------------------------

def update(frame):
    t0, t1, streak = frames[frame]

    # Current points
    point0.set_data([t0], [streak])
    point1.set_data([t1], [streak])

    # Store history
    angles0_history.append(t0)
    angles1_history.append(t1)
    radius_history.append(streak)

    # Draw motion trail
    trail0.set_data(angles0_history, radius_history)
    trail1.set_data(angles1_history, radius_history)

    return point0, point1, trail0, trail1

ani = FuncAnimation(fig, update, frames=len(frames), interval=700)

plt.show()
