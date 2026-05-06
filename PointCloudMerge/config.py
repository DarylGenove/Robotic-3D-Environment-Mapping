class Config:
    """
    Stores all configurable values for the scan-to-CAD alignment process.
    """

    SCAN_FILE = r"C:/Users/daryl/Desktop/combined_pointcloud_raw.pcd"
    CAD_FILE = r"C:/Users/daryl/Desktop/simple_room_environment_4walls.stl"

    VOXEL_SIZE = 0.05
    CAD_SAMPLE_POINTS = 80000
    ICP_DISTANCE = 0.20

    OUTER_CAD_MARGIN = 0.50

    REMOVE_OUTLIERS = True
    OUTLIER_NB = 20
    OUTLIER_STD = 2.0

    USE_CROP = False
    CROP_MIN = [-2.0, -2.0, -0.5]
    CROP_MAX = [10.0, 8.0, 4.0]

    PLANE_DISTANCE_THRESHOLD = 0.02
    PLANE_RANSAC_N = 3
    PLANE_NUM_ITERATIONS = 3000
    MIN_PLANE_POINTS = 1500
    MAX_PLANES_TO_CHECK = 8

    SHOW_DEBUG_PLANES = False

    MANUAL_TX = 0.0
    MANUAL_TY = 0.0
    MANUAL_TZ = 0.0

    SAVE_CLEANED_SCAN = True
    CLEANED_SCAN_FILE = r"C:/Users/daryl/Desktop/cleaned_scan_inside_cad_bounds.pcd"