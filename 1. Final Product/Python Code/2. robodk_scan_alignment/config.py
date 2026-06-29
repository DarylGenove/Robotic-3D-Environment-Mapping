from pathlib import Path


REPOSITORY_FOLDER_NAME = "Robotic-3D-Environment-Mapping"


def folder_has_required_repository_folders(folder: Path) -> bool:
    """
    Checks if a folder is the repository/root folder by checking
    if it contains the required project data folders.
    """

    has_point_cloud_folder = (folder / "Point Cloud Testing Folder").is_dir()
    has_cad_model_folder = (folder / "CAD Model").is_dir()

    return has_point_cloud_folder and has_cad_model_folder


def find_repository_folder() -> Path:
    """
    Finds the repository/root folder.

    Expected structure:

    Robotic-3D-Environment-Mapping
    |
    |-- Point Cloud Testing Folder
    |   |-- adaptive_inside_box_pointcloud_clean.pcd
    |
    |-- CAD Model
    |   |-- 7. Cabinet Correct Measurements.STL
    |
    |-- 1. Final Product
        |-- Python Code
            |-- 2. robodk_scan_alignment
                |-- config.py
                |-- main.py

    This allows the project to work on different computers,
    even if the user folder path is different.
    """

    current_file = Path(__file__).resolve()
    current_folder = current_file.parent

    # ------------------------------------------------------------
    # 1. Search from config.py folder upward through all parents
    # ------------------------------------------------------------
    for folder in [current_folder, *current_folder.parents]:
        correct_folder_name = folder.name == REPOSITORY_FOLDER_NAME

        if correct_folder_name and folder_has_required_repository_folders(folder):
            return folder.resolve()

    # ------------------------------------------------------------
    # 2. If the repository folder was renamed, still allow it
    # as long as both important folders exist in the same folder.
    # ------------------------------------------------------------
    for folder in [current_folder, *current_folder.parents]:
        if folder_has_required_repository_folders(folder):
            return folder.resolve()

    # ------------------------------------------------------------
    # 3. Fallback search in common Windows user locations.
    # This helps if RoboDK runs from Temp or if the project is cloned
    # in Desktop/Documents/Downloads.
    # ------------------------------------------------------------
    home_folder = Path.home()

    search_locations = [
        home_folder / "Desktop",
        home_folder / "OneDrive" / "Desktop",
        home_folder / "Documents",
        home_folder / "Downloads",
        home_folder,
    ]

    for search_location in search_locations:
        if not search_location.exists():
            continue

        direct_candidate = search_location / REPOSITORY_FOLDER_NAME

        if folder_has_required_repository_folders(direct_candidate):
            return direct_candidate.resolve()

        try:
            for candidate_folder in search_location.rglob(REPOSITORY_FOLDER_NAME):
                if folder_has_required_repository_folders(candidate_folder):
                    return candidate_folder.resolve()

        except PermissionError:
            continue

    # ------------------------------------------------------------
    # 4. Stop here if not found. Do not guess parents[3].
    # ------------------------------------------------------------
    checked_parent_folders = "\n".join(
        str(folder) for folder in [current_folder, *current_folder.parents]
    )

    raise FileNotFoundError(
        "Could not find the repository folder.\n\n"
        "Expected folder structure:\n"
        f"{REPOSITORY_FOLDER_NAME}\\Point Cloud Testing Folder\n"
        f"{REPOSITORY_FOLDER_NAME}\\CAD Model\n\n"
        "Example correct path:\n"
        "C:\\Users\\daryl\\Desktop\\Robotic D Environment Mapping\\"
        "Robotic-3D-Environment-Mapping\\Point Cloud Testing Folder\n\n"
        "Starting from config.py:\n"
        f"{current_file}\n\n"
        "Checked parent folders:\n"
        f"{checked_parent_folders}\n\n"
        "Fix:\n"
        "Make sure 'Point Cloud Testing Folder' and 'CAD Model' are both inside "
        "the same root folder as the repository."
    )


class Config:
    """
    Stores all configurable values for the scan-to-CAD alignment process.
    """

    # ------------------------------------------------------------
    # Main folders
    # ------------------------------------------------------------
    REPOSITORY_FOLDER = find_repository_folder()

    POINT_CLOUD_TESTING_FOLDER = REPOSITORY_FOLDER / "Point Cloud Testing Folder"
    CAD_MODEL_FOLDER = REPOSITORY_FOLDER / "CAD Model"

    SCRIPT_FOLDER = Path(__file__).resolve().parent
    OUTPUT_FOLDER = SCRIPT_FOLDER / "RoboDK Export"
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------
    # Input files
    # ------------------------------------------------------------
    SCAN_FILE = (
        POINT_CLOUD_TESTING_FOLDER
        / "adaptive_inside_box_pointcloud_clean.pcd"
    )

    CAD_FILE = (
        CAD_MODEL_FOLDER
        / "7. Cabinet Correct Measurements.STL"
    )

    # ------------------------------------------------------------
    # CAD settings
    # ------------------------------------------------------------
    CAD_SCALE = 0.001

    CAD_EXTRA_RX_DEG = 0.0
    CAD_EXTRA_RY_DEG = 0.0
    CAD_EXTRA_RZ_DEG = 0.0

    # ------------------------------------------------------------
    # Point cloud processing settings
    # ------------------------------------------------------------
    VOXEL_SIZE = 0.01
    CAD_SAMPLE_POINTS = 80000
    ICP_DISTANCE = 0.20

    # ------------------------------------------------------------
    # CAD bound filtering
    # ------------------------------------------------------------
    USE_CAD_BOUND_FILTER = True
    OUTER_CAD_MARGIN = 0.05

    # ------------------------------------------------------------
    # Outlier removal before alignment
    # ------------------------------------------------------------
    REMOVE_OUTLIERS = False
    OUTLIER_NB = 20
    OUTLIER_STD = 2.0

    # ------------------------------------------------------------
    # Outlier removal after filtering
    # ------------------------------------------------------------
    POST_FILTER_REMOVE_OUTLIERS = True
    POST_FILTER_OUTLIER_NB = 20
    POST_FILTER_OUTLIER_STD = 1.5

    # ------------------------------------------------------------
    # Manual crop settings
    # ------------------------------------------------------------
    USE_CROP = False
    CROP_MIN = [-2.0, -2.0, -0.5]
    CROP_MAX = [10.0, 8.0, 4.0]

    # ------------------------------------------------------------
    # Plane detection settings
    # ------------------------------------------------------------
    PLANE_DISTANCE_THRESHOLD = 0.03
    PLANE_RANSAC_N = 3
    PLANE_NUM_ITERATIONS = 3000
    MIN_PLANE_POINTS = 300
    MAX_PLANES_TO_CHECK = 12

    SHOW_DEBUG_PLANES = False

    # ------------------------------------------------------------
    # Manual translation correction
    # ------------------------------------------------------------
    MANUAL_TX = 0.0
    MANUAL_TY = 0.0
    MANUAL_TZ = 0.0

    # ------------------------------------------------------------
    # Output files
    # ------------------------------------------------------------
    SAVE_CLEANED_SCAN = True
    CLEANED_SCAN_FILE = OUTPUT_FOLDER / "scan_cleaned_inside_stl_range.pcd"

    SAVE_REMOVED_NOISE = True
    REMOVED_NOISE_FILE = OUTPUT_FOLDER / "removed_pcd_noise_outside_stl_range.pcd"

    # ------------------------------------------------------------
    # Debug path printer
    # ------------------------------------------------------------
    def print_paths(self):
        print("")
        print("=" * 70)
        print("CONFIG PATH CHECK")
        print("=" * 70)

        print("Repository folder:")
        print(self.REPOSITORY_FOLDER)
        print("Exists:", self.REPOSITORY_FOLDER.exists())

        print("")
        print("Point cloud testing folder:")
        print(self.POINT_CLOUD_TESTING_FOLDER)
        print("Exists:", self.POINT_CLOUD_TESTING_FOLDER.exists())

        print("")
        print("CAD model folder:")
        print(self.CAD_MODEL_FOLDER)
        print("Exists:", self.CAD_MODEL_FOLDER.exists())

        print("")
        print("Scan file:")
        print(self.SCAN_FILE)
        print("Exists:", self.SCAN_FILE.exists())

        print("")
        print("CAD file:")
        print(self.CAD_FILE)
        print("Exists:", self.CAD_FILE.exists())

        print("")
        print("Output folder:")
        print(self.OUTPUT_FOLDER)
        print("Exists:", self.OUTPUT_FOLDER.exists())

        print("=" * 70)
        print("")