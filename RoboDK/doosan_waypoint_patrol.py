from robodk.robolink import Robolink, ITEM_TYPE_ROBOT, ITEM_TYPE_TARGET, RUNMODE_SIMULATE, StoppedError
import time

# -----------------------------
# Config
# -----------------------------
ROBOT_NAME = "Doosan M1013"
TARGET_PREFIX = "Target "
PAUSE_SECONDS = 1.5

# Keep running forever
LOOP_FOREVER = True

# Simulation/debug only (set False if you want collision checking ON)
DISABLE_COLLISION_CHECK = True

# -----------------------------
# Connect
# -----------------------------
RDK = Robolink()
RDK.setRunMode(RUNMODE_SIMULATE)

robot = RDK.Item(ROBOT_NAME, ITEM_TYPE_ROBOT)
if not robot.Valid():
    raise Exception(f"Robot '{ROBOT_NAME}' not found")

robot.setSpeedJoints(10)
robot.setAccelerationJoints(20)

# Try to disable collision checking (API differs by RoboDK version)
if DISABLE_COLLISION_CHECK:
    try:
        RDK.setCollisionActive(0)  # 0 = OFF, 1 = ON
        print("Collision checking disabled.")
    except Exception:
        try:
            RDK.Command("CollisionDetection", "Off")
            print("Collision checking disabled.")
        except Exception:
            print("Warning: Could not disable collision checking via API.")

# -----------------------------
# Build target list automatically: Target 1, Target 2, ...
# -----------------------------
targets = []
i = 1
while True:
    t = RDK.Item(f"{TARGET_PREFIX}{i}", ITEM_TYPE_TARGET)
    if not t.Valid():
        break
    targets.append(t)
    i += 1

if not targets:
    raise Exception("No targets found (expected names like 'Target 1', 'Target 2', ...)")

print(f"Robot '{ROBOT_NAME}' found. Moving through {len(targets)} targets in a loop...")

# -----------------------------
# Motion sequence
# -----------------------------
def run_sequence():
    for idx, target in enumerate(targets, start=1):
        print(f"Moving to {TARGET_PREFIX}{idx}")
        try:
            robot.MoveJ(target)  # or robot.MoveL(target)
            time.sleep(PAUSE_SECONDS)
        except StoppedError as e:
            print(f"Skipped {TARGET_PREFIX}{idx}: {e}")
        except Exception as e:
            print(f"Error on {TARGET_PREFIX}{idx}: {e}")

# Infinite loop
while LOOP_FOREVER:
    run_sequence()
