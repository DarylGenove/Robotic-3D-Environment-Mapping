from dataclasses import dataclass, field  # Loads dataclass tools so settings can be written cleanly.
from pathlib import Path  # Loads Path so file and folder paths are easier to handle.


@dataclass  # Turns this class into a simple settings container.
class Config:  # Makes one place for all scanner settings.
    RUN_ON_REAL_ROBOT: bool = True  # Chooses real robot mode when True, and simulation mode when False.

    HOME_JOINTS: list[float] = field(  # Stores the safe home joint angles for the robot arm.
        default_factory=lambda: [270.00, 0.00, 90.00, 180.00, 0.00, 0.00]  # Stores default factory for use in the next steps.
    )  # Closes the multi-line code started above.
    CENTER_REFERENCE_JOINTS: list[float] = field(  # Stores the starting joint angles where the camera looks at the cabinet center.
        default_factory=lambda: [270.01, 0.21, 98.95, 180.00, 6.92, 0.00]  # Stores default factory for use in the next steps.
    )  # Closes the multi-line code started above.

    TCP_TO_CAMERA_MOUNT: list[float] = field(  # Stores where the camera mount sits compared with the robot tool point.
        default_factory=lambda: [0, 0, 55, 0, 0, 0]  # Stores default factory for use in the next steps.
    )  # Closes the multi-line code started above.
    CAMERA_MOUNT_TO_OPTICAL: list[float] = field(  # Stores how the RealSense optical camera frame is rotated.
        default_factory=lambda: [0, 0, 0, 0, 0, 90]  # Stores default factory for use in the next steps.
    )  # Closes the multi-line code started above.

    MIN_SAFE_TCP_Z_MM: float = 120.0  # Sets the lowest safe height for the robot tool point.
    MIN_SAFE_CAMERA_Z_MM: float = 120.0  # Sets the lowest safe height for the camera.

    RS_WIDTH: int = 848  # Sets the camera image width in pixels.
    RS_HEIGHT: int = 480  # Sets the camera image height in pixels.
    RS_FPS: int = 30  # Sets how many camera frames are read each second.

    WARMUP_FRAMES: int = 30  # Lets the camera throw away early frames while it stabilizes.
    CAPTURE_FRAMES_PER_POSITION: int = 30  # Sets how many frames are combined for one scan position.

    DEPTH_TRUNC_MAX: float = 1.0  # Ignores depth points farther away than this distance.

    SETTLE_TIME: float = 1.5  # Waits this many seconds after a robot move.
    MOVE_TIMEOUT_SEC: float = 30.0  # Sets the maximum time allowed for one robot movement.
    POLL_INTERVAL_SEC: float = 0.1  # Sets how often the code checks if the robot has stopped.

    SURFACE_VOXEL_SIZE: float = 0.003  # Sets the point-cloud simplification size.

    OUTLIER_NB_NEIGHBORS: int = 20  # Sets how many nearby points are checked when removing noise.
    OUTLIER_STD_RATIO: float = 2.0  # Sets how strict the noise removal is.

    NORMAL_RADIUS: float = 0.02  # Sets the search distance used for estimating surface direction.
    NORMAL_MAX_NN: int = 30  # Sets the maximum nearby points used for normal calculation.

    SHOW_FINAL_CLOUD: bool = True  # Chooses whether to show the final 3D scan window.
    SHOW_DEBUG_EACH_SCAN: bool = False  # Chooses whether to show every separate scan for debugging.

    MIN_SIDE_OFFSET_M: float = 0.08  # Sets the smallest left-right camera movement.
    MAX_SIDE_OFFSET_M: float = 0.32  # Sets the biggest left-right camera movement.

    MIN_VERTICAL_OFFSET_M: float = 0.06  # Sets the smallest up-down camera movement.
    MAX_VERTICAL_OFFSET_M: float = 0.24  # Sets the biggest up-down camera movement.

    MIN_FORWARD_OFFSET_M: float = 0.03  # Sets the smallest move closer to the cabinet.
    MAX_FORWARD_OFFSET_M: float = 0.14  # Sets the biggest move closer to the cabinet.

    ADAPTIVE_CROP_MARGIN_X_M: float = 0.12  # Adds extra space on the left and right when cropping points.
    ADAPTIVE_CROP_MARGIN_Y_M: float = 0.12  # Adds extra space up and down when cropping points.
    ADAPTIVE_CROP_MARGIN_Z_M: float = 0.20  # Adds extra space forward and backward when cropping points.

    BOUNDS_LOW_PERCENTILE: float = 2.0  # Uses the low edge of the point group while ignoring extreme bad points.
    BOUNDS_HIGH_PERCENTILE: float = 98.0  # Uses the high edge of the point group while ignoring extreme bad points.

    MIN_REFERENCE_POINTS: int = 1000  # Requires this many points before trusting the reference scan.

    PROJECT_FOLDER: Path = field(  # Stores the folder where this Python project is saved.
        default_factory=lambda: Path(__file__).resolve().parent  # Stores default factory for use in the next steps.
    )  # Closes the multi-line code started above.

    OUTPUT_FOLDER_NAME: str = "output"  # Stores the name of the folder for saved scan files.
    OUTPUT_CLEAN_FILE_NAME: str = "adaptive_inside_box_pointcloud_clean.pcd"  # Stores the name of the final cleaned point-cloud file.

    AUTO_CENTER_BEFORE_SCAN: bool = True  # Chooses whether the robot centers the camera before scanning.
    AUTO_CENTER_TARGET_DISTANCE_M: float = 0.80  # Sets the wanted camera distance from the box.
    AUTO_CENTER_MIN_DEPTH_M: float = 0.20  # Ignores detected objects that are too close.
    AUTO_CENTER_MAX_DEPTH_M: float = 3.00  # Ignores detected objects that are too far.

    AUTO_CENTER_MAX_TRANSLATION_STEP_M: float = 0.025  # Limits how far the camera can move in one auto-centering step.
    AUTO_CENTERING_GAIN: float = 0.60  # Controls how strongly the camera moves left, right, up, and down.
    AUTO_DEPTH_GAIN: float = 0.60  # Controls how strongly the camera moves forward and backward.

    AUTO_CENTER_TOLERANCE_PX: int = 25  # Allows this many pixels of center error before it still counts as centered.
    AUTO_DISTANCE_TOLERANCE_M: float = 0.05  # Allows this much distance error before it still counts as centered.

    AUTO_REQUIRED_STABLE_FRAMES: int = 8  # Requires the box to stay stable for this many frames.
    AUTO_STABLE_CENTER_TOLERANCE_PX: int = 12  # Allows small pixel changes while checking if the box is stable.
    AUTO_STABLE_DISTANCE_TOLERANCE_M: float = 0.04  # Allows small distance changes while checking if the box is stable.
    AUTO_MOVE_COOLDOWN_SECONDS: float = 1.25  # Waits this long between automatic robot moves.
    AUTO_MAX_FAILED_MOVES: int = 5  # Stops auto-centering after too many failed moves.
    AUTO_MAX_TOTAL_MOVES: int = 30  # Stops auto-centering after too many total moves.
    AUTO_CENTER_TIMEOUT_SECONDS: float = 180.0  # Stops auto-centering if it takes too long.

    AUTO_MIN_BOX_AREA: int = 1200  # Ignores detected shapes that are too small.
    AUTO_MIN_BOX_WIDTH: int = 80  # Ignores detected boxes that are too narrow.
    AUTO_MIN_BOX_HEIGHT: int = 80  # Ignores detected boxes that are too short.

    AUTO_DEPTH_PERCENTILE: int = 10  # Chooses a front depth value from the closest useful pixels.
    AUTO_DEPTH_FRONT_MARGIN: float = 0.05  # Keeps pixels slightly in front of the detected front depth.
    AUTO_DEPTH_BACK_MARGIN: float = 0.45  # Keeps pixels behind the detected front depth.

    AUTO_DETECTION_ROI_TOP_RATIO: float = 0.05  # Sets the top edge of the camera area used for box detection.
    AUTO_DETECTION_ROI_BOTTOM_RATIO: float = 0.82  # Sets the bottom edge of the camera area used for box detection.
    AUTO_DETECTION_ROI_LEFT_RATIO: float = 0.02  # Sets the left edge of the camera area used for box detection.
    AUTO_DETECTION_ROI_RIGHT_RATIO: float = 0.98  # Sets the right edge of the camera area used for box detection.

    AUTO_WINDOW_NAME: str = "Automatic Box Centering"  # Stores the name of the auto-centering camera window.
    AUTO_MASK_WINDOW_NAME: str = "Automatic Depth Mask"  # Stores the name of the depth mask window.

    def __post_init__(self):  # Runs after Config is created and prepares needed folders.
        self.OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)  # Makes the folder if it does not exist yet.

    @property  # Lets this method be used like a normal value.
    def OUTPUT_FOLDER(self) -> Path:  # Builds the full folder path where output files are saved.
        return self.PROJECT_FOLDER / self.OUTPUT_FOLDER_NAME  # Gives this result back to the part of the code that called it.

    @property  # Lets this method be used like a normal value.
    def OUTPUT_CLEAN_FILE(self) -> Path:  # Builds the full path for the final cleaned scan file.
        return self.OUTPUT_FOLDER / self.OUTPUT_CLEAN_FILE_NAME  # Gives this result back to the part of the code that called it.
