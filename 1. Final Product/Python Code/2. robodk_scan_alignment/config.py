# Bring in needed tools from pathlib.
from pathlib import Path


# Set the REPOSITORY_FOLDER_NAME setting.
REPOSITORY_FOLDER_NAME = "Robotic-3D-Environment-Mapping"


# Create the folder has required repository folders function.
def folder_has_required_repository_folders(folder: Path) -> bool:


    # Save a value in has point cloud folder.
    has_point_cloud_folder = (folder / "Point Cloud Testing Folder").is_dir()
    # Save a value in has cad model folder.
    has_cad_model_folder = (folder / "CAD Model").is_dir()

    # Send this result back to the part of the code that asked for it.
    return has_point_cloud_folder and has_cad_model_folder


# Create the find repository folder function.
def find_repository_folder() -> Path:


    # Find the folder where this Python file is stored.
    current_file = Path(__file__).resolve()
    # Save a value in current folder.
    current_folder = current_file.parent


    # Repeat this code for every item in the group.
    for folder in [current_folder, *current_folder.parents]:
        # Run this line as one small step in the program.
        correct_folder_name = folder.name == REPOSITORY_FOLDER_NAME

        # Check this condition before choosing what happens next.
        if correct_folder_name and folder_has_required_repository_folders(folder):
            # Send this result back to the part of the code that asked for it.
            return folder.resolve()


    # Repeat this code for every item in the group.
    for folder in [current_folder, *current_folder.parents]:
        # Check this condition before choosing what happens next.
        if folder_has_required_repository_folders(folder):
            # Send this result back to the part of the code that asked for it.
            return folder.resolve()


    # Find the current user's home folder.
    home_folder = Path.home()

    # Save a value in search locations.
    search_locations = [
        # Add this value to the current group.
        home_folder / "Desktop",
        # Add this value to the current group.
        home_folder / "OneDrive" / "Desktop",
        # Add this value to the current group.
        home_folder / "Documents",
        # Add this value to the current group.
        home_folder / "Downloads",
        # Add this value to the current group.
        home_folder,
    ]

    # Repeat this code for every item in the group.
    for search_location in search_locations:
        # Check this condition before choosing what happens next.
        if not search_location.exists():
            # Skip the rest of this loop and go to the next item.
            continue

        # Save a value in direct candidate.
        direct_candidate = search_location / REPOSITORY_FOLDER_NAME

        # Check this condition before choosing what happens next.
        if folder_has_required_repository_folders(direct_candidate):
            # Send this result back to the part of the code that asked for it.
            return direct_candidate.resolve()

        # Try this code, but be ready if something goes wrong.
        try:
            # Search inside folders to find the project folder.
            for candidate_folder in search_location.rglob(REPOSITORY_FOLDER_NAME):
                # Check this condition before choosing what happens next.
                if folder_has_required_repository_folders(candidate_folder):
                    # Send this result back to the part of the code that asked for it.
                    return candidate_folder.resolve()

        # Handle the error so the program can continue or explain it.
        except PermissionError:
            # Skip the rest of this loop and go to the next item.
            continue


    # Save a value in checked parent folders.
    checked_parent_folders = "\n".join(
        # Run this line as one small step in the program.
        str(folder) for folder in [current_folder, *current_folder.parents]
    )

    # Stop the program because an important file or folder is missing.
    raise FileNotFoundError(
        # Run this line as one small step in the program.
        "Could not find the repository folder.\n\n"
        # Run this line as one small step in the program.
        "Expected folder structure:\n"
        # Run this line as one small step in the program.
        f"{REPOSITORY_FOLDER_NAME}\\Point Cloud Testing Folder\n"
        # Run this line as one small step in the program.
        f"{REPOSITORY_FOLDER_NAME}\\CAD Model\n\n"
        # Run this line as one small step in the program.
        "Example correct path:\n"
        # Run this line as one small step in the program.
        "C:\\Users\\daryl\\Desktop\\Robotic D Environment Mapping\\"
        # Run this line as one small step in the program.
        "Robotic-3D-Environment-Mapping\\Point Cloud Testing Folder\n\n"
        # Run this line as one small step in the program.
        "Starting from config.py:\n"
        # Run this line as one small step in the program.
        f"{current_file}\n\n"
        # Run this line as one small step in the program.
        "Checked parent folders:\n"
        # Run this line as one small step in the program.
        f"{checked_parent_folders}\n\n"
        # Run this line as one small step in the program.
        "Fix:\n"
        # Run this line as one small step in the program.
        "Make sure 'Point Cloud Testing Folder' and 'CAD Model' are both inside "
        # Run this line as one small step in the program.
        "the same root folder as the repository."
    )


# Create the Config class, which groups related code together.
class Config:


    # Set the REPOSITORY_FOLDER setting.
    REPOSITORY_FOLDER = find_repository_folder()

    # Set the POINT_CLOUD_TESTING_FOLDER setting.
    POINT_CLOUD_TESTING_FOLDER = REPOSITORY_FOLDER / "Point Cloud Testing Folder"
    # Set the CAD_MODEL_FOLDER setting.
    CAD_MODEL_FOLDER = REPOSITORY_FOLDER / "CAD Model"

    # Find the folder where this Python file is stored.
    SCRIPT_FOLDER = Path(__file__).resolve().parent
    # Set the OUTPUT_FOLDER setting.
    OUTPUT_FOLDER = SCRIPT_FOLDER / "RoboDK Export"
    # Create this folder if it is missing.
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)


    # Set the SCAN_FILE setting.
    SCAN_FILE = (
        # Run this line as one small step in the program.
        POINT_CLOUD_TESTING_FOLDER
        # Run this line as one small step in the program.
        / "adaptive_inside_box_pointcloud_clean.pcd"
    )

    # Set the CAD_FILE setting.
    CAD_FILE = (
        # Run this line as one small step in the program.
        CAD_MODEL_FOLDER
        # Run this line as one small step in the program.
        / "7. Cabinet Correct Measurements.STL"
    )


    # Set the CAD_SCALE setting.
    CAD_SCALE = 0.001

    # Set the CAD_EXTRA_RX_DEG setting.
    CAD_EXTRA_RX_DEG = 0.0
    # Set the CAD_EXTRA_RY_DEG setting.
    CAD_EXTRA_RY_DEG = 0.0
    # Set the CAD_EXTRA_RZ_DEG setting.
    CAD_EXTRA_RZ_DEG = 0.0


    # Set the VOXEL_SIZE setting.
    VOXEL_SIZE = 0.01
    # Set the CAD_SAMPLE_POINTS setting.
    CAD_SAMPLE_POINTS = 80000
    # Set the ICP_DISTANCE setting.
    ICP_DISTANCE = 0.20


    # Set the USE_CAD_BOUND_FILTER setting.
    USE_CAD_BOUND_FILTER = True
    # Set the OUTER_CAD_MARGIN setting.
    OUTER_CAD_MARGIN = 0.05


    # Set the REMOVE_OUTLIERS setting.
    REMOVE_OUTLIERS = False
    # Set the OUTLIER_NB setting.
    OUTLIER_NB = 20
    # Set the OUTLIER_STD setting.
    OUTLIER_STD = 2.0


    # Set the POST_FILTER_REMOVE_OUTLIERS setting.
    POST_FILTER_REMOVE_OUTLIERS = True
    # Set the POST_FILTER_OUTLIER_NB setting.
    POST_FILTER_OUTLIER_NB = 20
    # Set the POST_FILTER_OUTLIER_STD setting.
    POST_FILTER_OUTLIER_STD = 1.5


    # Set the USE_CROP setting.
    USE_CROP = False
    # Set the CROP_MIN setting.
    CROP_MIN = [-2.0, -2.0, -0.5]
    # Set the CROP_MAX setting.
    CROP_MAX = [10.0, 8.0, 4.0]


    # Set the PLANE_DISTANCE_THRESHOLD setting.
    PLANE_DISTANCE_THRESHOLD = 0.03
    # Set the PLANE_RANSAC_N setting.
    PLANE_RANSAC_N = 3
    # Set the PLANE_NUM_ITERATIONS setting.
    PLANE_NUM_ITERATIONS = 3000
    # Set the MIN_PLANE_POINTS setting.
    MIN_PLANE_POINTS = 300
    # Set the MAX_PLANES_TO_CHECK setting.
    MAX_PLANES_TO_CHECK = 12

    # Set the SHOW_DEBUG_PLANES setting.
    SHOW_DEBUG_PLANES = False


    # Set the MANUAL_TX setting.
    MANUAL_TX = 0.0
    # Set the MANUAL_TY setting.
    MANUAL_TY = 0.0
    # Set the MANUAL_TZ setting.
    MANUAL_TZ = 0.0


    # Set the SAVE_CLEANED_SCAN setting.
    SAVE_CLEANED_SCAN = True
    # Set the CLEANED_SCAN_FILE setting.
    CLEANED_SCAN_FILE = OUTPUT_FOLDER / "scan_cleaned_inside_stl_range.pcd"

    # Set the SAVE_REMOVED_NOISE setting.
    SAVE_REMOVED_NOISE = True
    # Set the REMOVED_NOISE_FILE setting.
    REMOVED_NOISE_FILE = OUTPUT_FOLDER / "removed_pcd_noise_outside_stl_range.pcd"


    # Create the print paths function.
    def print_paths(self):
        # Show helpful information on the screen.
        print("")
        # Show helpful information on the screen.
        print("=" * 70)
        # Show helpful information on the screen.
        print("CONFIG PATH CHECK")
        # Show helpful information on the screen.
        print("=" * 70)

        # Show helpful information on the screen.
        print("Repository folder:")
        # Show helpful information on the screen.
        print(self.REPOSITORY_FOLDER)
        # Show helpful information on the screen.
        print("Exists:", self.REPOSITORY_FOLDER.exists())

        # Show helpful information on the screen.
        print("")
        # Show helpful information on the screen.
        print("Point cloud testing folder:")
        # Show helpful information on the screen.
        print(self.POINT_CLOUD_TESTING_FOLDER)
        # Show helpful information on the screen.
        print("Exists:", self.POINT_CLOUD_TESTING_FOLDER.exists())

        # Show helpful information on the screen.
        print("")
        # Show helpful information on the screen.
        print("CAD model folder:")
        # Show helpful information on the screen.
        print(self.CAD_MODEL_FOLDER)
        # Show helpful information on the screen.
        print("Exists:", self.CAD_MODEL_FOLDER.exists())

        # Show helpful information on the screen.
        print("")
        # Show helpful information on the screen.
        print("Scan file:")
        # Show helpful information on the screen.
        print(self.SCAN_FILE)
        # Show helpful information on the screen.
        print("Exists:", self.SCAN_FILE.exists())

        # Show helpful information on the screen.
        print("")
        # Show helpful information on the screen.
        print("CAD file:")
        # Show helpful information on the screen.
        print(self.CAD_FILE)
        # Show helpful information on the screen.
        print("Exists:", self.CAD_FILE.exists())

        # Show helpful information on the screen.
        print("")
        # Show helpful information on the screen.
        print("Output folder:")
        # Show helpful information on the screen.
        print(self.OUTPUT_FOLDER)
        # Show helpful information on the screen.
        print("Exists:", self.OUTPUT_FOLDER.exists())

        # Show helpful information on the screen.
        print("=" * 70)
        # Show helpful information on the screen.
        print("")
