class Config:
    """
    Stores all configurable values for the scan-to-CAD alignment process.
    """

    SCAN_FILE = (
        r"C:/Users/daryl/Desktop/Robotic D Environment Mapping/"
        r"Robotic-3D-Environment-Mapping/Point Cloud Testing Folder/"
        r"adaptive_inside_box_pointcloud_clean.pcd"
    )

    CAD_FILE = r"C:/Users/daryl/Desktop/Robotic D Environment Mapping/Robotic-3D-Environment-Mapping/CAD Model/7. Cabinet Correct Measurements.STL"

    CAD_SCALE = 0.001

    CAD_EXTRA_RX_DEG = 0.0
    CAD_EXTRA_RY_DEG = 0.0
    CAD_EXTRA_RZ_DEG = 0.0

    VOXEL_SIZE = 0.01
    CAD_SAMPLE_POINTS = 80000
    ICP_DISTANCE = 0.20

    # This is now enabled because the front alignment is correct.
    USE_CAD_BOUND_FILTER = True

    # Margin around the aligned CAD bounding box.
    # Unit is meters.
    # 0.05 means 5 cm extra tolerance around the STL/CAD model.
    OUTER_CAD_MARGIN = 0.05

    # First preprocessing stage.
    # Keep False while debugging so the raw scan is not damaged too early.
    REMOVE_OUTLIERS = False
    OUTLIER_NB = 20
    OUTLIER_STD = 2.0

    # Second cleanup stage after CAD-bound filtering.
    # This removes small noisy floating clusters after the STL range crop.
    POST_FILTER_REMOVE_OUTLIERS = True
    POST_FILTER_OUTLIER_NB = 20
    POST_FILTER_OUTLIER_STD = 1.5

    USE_CROP = False
    CROP_MIN = [-2.0, -2.0, -0.5]
    CROP_MAX = [10.0, 8.0, 4.0]

    PLANE_DISTANCE_THRESHOLD = 0.03
    PLANE_RANSAC_N = 3
    PLANE_NUM_ITERATIONS = 3000
    MIN_PLANE_POINTS = 300
    MAX_PLANES_TO_CHECK = 12

    SHOW_DEBUG_PLANES = False

    MANUAL_TX = 0.0
    MANUAL_TY = 0.0
    MANUAL_TZ = 0.0

    SAVE_CLEANED_SCAN = True
    CLEANED_SCAN_FILE = r"C:/Users/daryl/Desktop/scan_cleaned_inside_stl_range.pcd"

    SAVE_REMOVED_NOISE = True
    REMOVED_NOISE_FILE = r"C:/Users/daryl/Desktop/removed_pcd_noise_outside_stl_range.pcd"