# Create the Config object that groups related actions together.
class Config:
    # Save RUN ON REAL ROBOT so the program can use it later.
    RUN_ON_REAL_ROBOT = True

    # Save HOME JOINTS so the program can use it later.
    HOME_JOINTS = [270.00, 0.00, 90.00, 180.00, 0.00, 0.00]

    # Save CENTER REFERENCE JOINTS so the program can use it later.
    CENTER_REFERENCE_JOINTS = [270.01, 0.21, 98.95, 180.00, 6.92, 0.00]

    # Save TCP TO CAMERA MOUNT so the program can use it later.
    TCP_TO_CAMERA_MOUNT = [0, 0, 55, 0, 0, 0]
    # Save CAMERA MOUNT TO OPTICAL so the program can use it later.
    CAMERA_MOUNT_TO_OPTICAL = [0, 0, 0, 0, 0, 90]

    # Save MIN SAFE TCP Z MM so the program can use it later.
    MIN_SAFE_TCP_Z_MM = 120.0

    # Save SETTLE TIME so the program can use it later.
    SETTLE_TIME = 1.5
    # Save MOVE TIMEOUT SEC so the program can use it later.
    MOVE_TIMEOUT_SEC = 30.0
    # Save POLL INTERVAL SEC so the program can use it later.
    POLL_INTERVAL_SEC = 0.1

    # Save SEAM HALF WIDTH M so the program can use it later.
    SEAM_HALF_WIDTH_M = 0.08
    # Save SEAM Y M so the program can use it later.
    SEAM_Y_M = 0.06
    # Save SEAM Z M so the program can use it later.
    SEAM_Z_M = 0.18

    # Save DRY RUN HEIGHT OFFSET M so the program can use it later.
    DRY_RUN_HEIGHT_OFFSET_M = 0.03
    # Save TIP STANDOFF M so the program can use it later.
    TIP_STANDOFF_M = 0.02

    # Save NUM PATH POINTS so the program can use it later.
    NUM_PATH_POINTS = 5

    # Save LOCK J6 WITH SEED so the program can use it later.
    LOCK_J6_WITH_SEED = True
    # Save MAX J6 WARNING DEGREES so the program can use it later.
    MAX_J6_WARNING_DEGREES = 5.0

    # Save CREATE DEBUG TARGETS so the program can use it later.
    CREATE_DEBUG_TARGETS = True
