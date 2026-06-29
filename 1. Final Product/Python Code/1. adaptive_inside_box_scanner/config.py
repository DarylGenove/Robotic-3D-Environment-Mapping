from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Config:
    RUN_ON_REAL_ROBOT: bool = True

    HOME_JOINTS: list[float] = field(
        default_factory=lambda: [270.00, 0.00, 90.00, 180.00, 0.00, 0.00]
    )
    CENTER_REFERENCE_JOINTS: list[float] = field(
        default_factory=lambda: [270.01, 0.21, 98.95, 180.00, 6.92, 0.00]
    )

    TCP_TO_CAMERA_MOUNT: list[float] = field(
        default_factory=lambda: [0, 0, 55, 0, 0, 0]
    )
    CAMERA_MOUNT_TO_OPTICAL: list[float] = field(
        default_factory=lambda: [0, 0, 0, 0, 0, 90]
    )

    MIN_SAFE_TCP_Z_MM: float = 120.0
    MIN_SAFE_CAMERA_Z_MM: float = 120.0

    RS_WIDTH: int = 848
    RS_HEIGHT: int = 480
    RS_FPS: int = 30

    WARMUP_FRAMES: int = 30
    CAPTURE_FRAMES_PER_POSITION: int = 30

    DEPTH_TRUNC_MAX: float = 1.0

    SETTLE_TIME: float = 1.5
    MOVE_TIMEOUT_SEC: float = 30.0
    POLL_INTERVAL_SEC: float = 0.1

    SURFACE_VOXEL_SIZE: float = 0.003

    OUTLIER_NB_NEIGHBORS: int = 20
    OUTLIER_STD_RATIO: float = 2.0

    NORMAL_RADIUS: float = 0.02
    NORMAL_MAX_NN: int = 30

    SHOW_FINAL_CLOUD: bool = True
    SHOW_DEBUG_EACH_SCAN: bool = False

    MIN_SIDE_OFFSET_M: float = 0.08
    MAX_SIDE_OFFSET_M: float = 0.32

    MIN_VERTICAL_OFFSET_M: float = 0.06
    MAX_VERTICAL_OFFSET_M: float = 0.24

    MIN_FORWARD_OFFSET_M: float = 0.03
    MAX_FORWARD_OFFSET_M: float = 0.14

    ADAPTIVE_CROP_MARGIN_X_M: float = 0.12
    ADAPTIVE_CROP_MARGIN_Y_M: float = 0.12
    ADAPTIVE_CROP_MARGIN_Z_M: float = 0.20

    BOUNDS_LOW_PERCENTILE: float = 2.0
    BOUNDS_HIGH_PERCENTILE: float = 98.0

    MIN_REFERENCE_POINTS: int = 1000

    PROJECT_FOLDER: Path = field(
        default_factory=lambda: Path(__file__).resolve().parent
    )

    OUTPUT_FOLDER_NAME: str = "output"
    OUTPUT_CLEAN_FILE_NAME: str = "adaptive_inside_box_pointcloud_clean.pcd"

    AUTO_CENTER_BEFORE_SCAN: bool = True
    AUTO_CENTER_TARGET_DISTANCE_M: float = 0.80
    AUTO_CENTER_MIN_DEPTH_M: float = 0.20
    AUTO_CENTER_MAX_DEPTH_M: float = 3.00

    AUTO_CENTER_MAX_TRANSLATION_STEP_M: float = 0.025
    AUTO_CENTERING_GAIN: float = 0.60
    AUTO_DEPTH_GAIN: float = 0.60

    AUTO_CENTER_TOLERANCE_PX: int = 25
    AUTO_DISTANCE_TOLERANCE_M: float = 0.05

    AUTO_REQUIRED_STABLE_FRAMES: int = 8
    AUTO_STABLE_CENTER_TOLERANCE_PX: int = 12
    AUTO_STABLE_DISTANCE_TOLERANCE_M: float = 0.04
    AUTO_MOVE_COOLDOWN_SECONDS: float = 1.25
    AUTO_MAX_FAILED_MOVES: int = 5
    AUTO_MAX_TOTAL_MOVES: int = 30
    AUTO_CENTER_TIMEOUT_SECONDS: float = 180.0

    AUTO_MIN_BOX_AREA: int = 1200
    AUTO_MIN_BOX_WIDTH: int = 80
    AUTO_MIN_BOX_HEIGHT: int = 80

    AUTO_DEPTH_PERCENTILE: int = 10
    AUTO_DEPTH_FRONT_MARGIN: float = 0.05
    AUTO_DEPTH_BACK_MARGIN: float = 0.45

    AUTO_DETECTION_ROI_TOP_RATIO: float = 0.05
    AUTO_DETECTION_ROI_BOTTOM_RATIO: float = 0.82
    AUTO_DETECTION_ROI_LEFT_RATIO: float = 0.02
    AUTO_DETECTION_ROI_RIGHT_RATIO: float = 0.98

    AUTO_WINDOW_NAME: str = "Automatic Box Centering"
    AUTO_MASK_WINDOW_NAME: str = "Automatic Depth Mask"

    def __post_init__(self):
        self.OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    @property
    def OUTPUT_FOLDER(self) -> Path:
        return self.PROJECT_FOLDER / self.OUTPUT_FOLDER_NAME

    @property
    def OUTPUT_CLEAN_FILE(self) -> Path:
        return self.OUTPUT_FOLDER / self.OUTPUT_CLEAN_FILE_NAME