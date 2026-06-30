# Create the Config class so related code stays together.
class Config:
    # Choose whether the code moves the real robot or only simulates it.
    RUN_ON_REAL_ROBOT = True

    # Store the safe home joint position for the robot.
    HOME_JOINTS = [270.00, 0.00, 90.00, 180.00, 0.00, 0.00]

    # Store the joint position where the camera starts looking at the cabinet.
    CENTER_REFERENCE_JOINTS = [270.01, 0.21, 98.95, 180.00, 6.92, 0.00]

    # Store where the camera mount is compared to the robot TCP.
    TCP_TO_CAMERA_MOUNT = [0, 0, 55, 0, 0, 0]
    # Store the rotation from the mount frame to the camera optical frame.
    CAMERA_MOUNT_TO_OPTICAL = [0, 0, 0, 0, 0, 90]

    # Set the lowest safe height for the robot TCP.
    MIN_SAFE_TCP_Z_MM = 120.0
    # Set the lowest safe height for the camera.
    MIN_SAFE_CAMERA_Z_MM = 120.0

    # Set how long the robot waits after moving.
    SETTLE_TIME = 1.5
    # Set the maximum time allowed for one robot move.
    MOVE_TIMEOUT_SEC = 30.0
    # Set how often the code checks if the robot stopped.
    POLL_INTERVAL_SEC = 0.1

    # Set half of the left-to-right look line width in meters.
    LINE_HALF_WIDTH_M = 0.22
    # Set the forward/back position of the look line in camera space.
    LINE_Y_M = 0.06
    # Set the height of the look line in camera space.
    LINE_Z_M = 0.55

    # Set how many points the camera should look at along the line.
    NUM_LOOK_POINTS = 7

    # Set the extra X shift for the fixed camera position.
    CAMERA_FIXED_X_OFFSET_M = 0.0
    # Set the extra Y shift for the fixed camera position.
    CAMERA_FIXED_Y_OFFSET_M = 0.0
    # Set the extra Z shift for the fixed camera position.
    CAMERA_FIXED_Z_OFFSET_M = 0.0

    # Choose whether to create helper targets in RoboDK.
    CREATE_DEBUG_TARGETS = True
