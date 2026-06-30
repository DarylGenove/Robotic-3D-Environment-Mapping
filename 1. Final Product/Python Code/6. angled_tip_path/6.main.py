# Bring in the sys toolbox so this file can use it.
import sys
# Bring in Path from pathlib so we can use it here.
from pathlib import Path


# Make a folder or file path object.
ROBODK_PYTHON_FOLDER = Path("C:/RoboDK/Python")

# Check if this condition is true.
if ROBODK_PYTHON_FOLDER.exists():
    # Tell Python to look in this folder first when importing code.
    sys.path.insert(0, str(ROBODK_PYTHON_FOLDER))

# Bring in Robolink, ITEM_TYPE_ROBOT from robodk.robolink so we can use it here.
from robodk.robolink import Robolink, ITEM_TYPE_ROBOT


# Save PROJECT FOLDER NAME so the program can use it later.
PROJECT_FOLDER_NAME = "6. angled_tip_path"

# Save REQUIRED PROJECT FILES so the program can use it later.
REQUIRED_PROJECT_FILES = [
    # This line helps the program do the next small step.
    "config.py",
    # This line helps the program do the next small step.
    "angled_tcp_pose_builder.py",
    # This line helps the program do the next small step.
    "angled_tip_path_service.py",
    # This line helps the program do the next small step.
    "camera_calibration.py",
    # This line helps the program do the next small step.
    "debug_target_service.py",
    # This line helps the program do the next small step.
    "robot_controller.py",
    # This line helps the program do the next small step.
    "seam_path_generator.py",
# Close this group of values.
]


# Start the is correct project folder function.
def is_correct_project_folder(folder: Path) -> bool:
    # Send this result back to the place that called the function.
    return folder.exists() and folder.is_dir() and all(
        # Check whether this file or folder really exists.
        (folder / file_name).exists()
        # Repeat this step for every item in the group.
        for file_name in REQUIRED_PROJECT_FILES
    # Close this group of values.
    )


# Start the find project folder function.
def find_project_folder() -> Path:
    # Make a folder or file path object.
    current_folder = Path(__file__).resolve().parent
    # Save working folder so the program can use it later.
    working_folder = Path.cwd().resolve()
    # Save home folder so the program can use it later.
    home_folder = Path.home()

    # Save possible folders so the program can use it later.
    possible_folders = [
        # This line helps the program do the next small step.
        current_folder,
        # This line helps the program do the next small step.
        working_folder,
        # This line helps the program do the next small step.
        home_folder / "Desktop" / PROJECT_FOLDER_NAME,
        # This line helps the program do the next small step.
        home_folder / "OneDrive" / "Desktop" / PROJECT_FOLDER_NAME,
        # This line helps the program do the next small step.
        home_folder / "Documents" / PROJECT_FOLDER_NAME,
        # This line helps the program do the next small step.
        home_folder / "Downloads" / PROJECT_FOLDER_NAME,
    # Close this group of values.
    ]

    # This line helps the program do the next small step.
    possible_folders.extend(current_folder.parents)
    # This line helps the program do the next small step.
    possible_folders.extend(working_folder.parents)

    # Repeat this step for every item in the group.
    for folder in possible_folders:
        # Check if this condition is true.
        if is_correct_project_folder(folder):
            # Send this result back to the place that called the function.
            return folder.resolve()

    # Save search locations so the program can use it later.
    search_locations = [
        # This line helps the program do the next small step.
        home_folder / "Desktop",
        # This line helps the program do the next small step.
        home_folder / "OneDrive" / "Desktop",
        # This line helps the program do the next small step.
        home_folder / "Documents",
        # This line helps the program do the next small step.
        home_folder / "Downloads",
        # This line helps the program do the next small step.
        home_folder,
    # Close this group of values.
    ]

    # Repeat this step for every item in the group.
    for search_location in search_locations:
        # Check if this condition is true.
        if not search_location.exists():
            # Skip the rest of this loop and go to the next item.
            continue

        # Try this risky step safely.
        try:
            # Repeat this step for every item in the group.
            for folder in search_location.rglob(PROJECT_FOLDER_NAME):
                # Check if this condition is true.
                if is_correct_project_folder(folder):
                    # Send this result back to the place that called the function.
                    return folder.resolve()
        # Handle the problem if the try step fails.
        except PermissionError:
            # Skip the rest of this loop and go to the next item.
            continue

    # Stop the program and show this problem message.
    raise FileNotFoundError(
        # This line helps the program do the next small step.
        "Could not find the project folder automatically.\n\n"
        # This line helps the program do the next small step.
        f"Expected folder name:\n{PROJECT_FOLDER_NAME}\n\n"
        # This line helps the program do the next small step.
        "The folder must contain:\n"
        # This line helps the program do the next small step.
        + "\n".join(f"- {file_name}" for file_name in REQUIRED_PROJECT_FILES)
        # This line helps the program do the next small step.
        + "\n\n"
        # This line helps the program do the next small step.
        "Place the full project folder inside Desktop, OneDrive/Desktop, "
        # This line helps the program do the next small step.
        "Documents, Downloads, or your user folder."
    # Close this group of values.
    )


# Save PROJECT FOLDER so the program can use it later.
PROJECT_FOLDER = find_project_folder()

# Save project folder string so the program can use it later.
project_folder_string = str(PROJECT_FOLDER)

# Check if this condition is true.
if project_folder_string in sys.path:
    # This line helps the program do the next small step.
    sys.path.remove(project_folder_string)

# Tell Python to look in this folder first when importing code.
sys.path.insert(0, project_folder_string)

# Repeat this step for every item in the group.
for module_name in [
    # This line helps the program do the next small step.
    "config",
    # This line helps the program do the next small step.
    "angled_tcp_pose_builder",
    # This line helps the program do the next small step.
    "angled_tip_path_service",
    # This line helps the program do the next small step.
    "camera_calibration",
    # This line helps the program do the next small step.
    "debug_target_service",
    # This line helps the program do the next small step.
    "robot_controller",
    # This line helps the program do the next small step.
    "seam_path_generator",
# This line helps the program do the next small step.
]:
    # Forget an old imported file so Python loads the fresh one.
    sys.modules.pop(module_name, None)

# Show a message on the screen.
print("Using project folder:")
# Show a message on the screen.
print(PROJECT_FOLDER)

# Bring in AngledTcpPoseBuilder from angled_tcp_pose_builder so we can use it here.
from angled_tcp_pose_builder import AngledTcpPoseBuilder
# Bring in AngledTipPathService from angled_tip_path_service so we can use it here.
from angled_tip_path_service import AngledTipPathService
# Bring in CameraCalibration from camera_calibration so we can use it here.
from camera_calibration import CameraCalibration
# Bring in Config from config so we can use it here.
from config import Config
# Bring in DebugTargetService from debug_target_service so we can use it here.
from debug_target_service import DebugTargetService
# Bring in RobotController from robot_controller so we can use it here.
from robot_controller import RobotController
# Bring in SeamPathGenerator from seam_path_generator so we can use it here.
from seam_path_generator import SeamPathGenerator


# Start the main function.
def main():
    # Save config so the program can use it later.
    config = Config()

    # Open the connection to RoboDK.
    rdk = Robolink()

    # Ask the user to select the robot inside RoboDK.
    robot = rdk.ItemUserPick(
        # This line helps the program do the next small step.
        "Select your Doosan M0609 robot",
        # This line helps the program do the next small step.
        ITEM_TYPE_ROBOT
    # Close this group of values.
    )

    # Check if this condition is true.
    if not robot.Valid():
        # Stop the program and show this problem message.
        raise Exception("No valid robot selected.")

    # Show a message on the screen.
    print("Selected robot:", robot.Name())

    # Save robot controller so the program can use it later.
    robot_controller = RobotController(
        # This line helps the program do the next small step.
        config,
        # This line helps the program do the next small step.
        rdk,
        # This line helps the program do the next small step.
        robot
    # Close this group of values.
    )

    # This line helps the program do the next small step.
    robot_controller.connect()

    # Save camera calibration so the program can use it later.
    camera_calibration = CameraCalibration(config)
    # Save seam path generator so the program can use it later.
    seam_path_generator = SeamPathGenerator(config)
    # Save angled tcp pose builder so the program can use it later.
    angled_tcp_pose_builder = AngledTcpPoseBuilder(config)
    # Save debug target service so the program can use it later.
    debug_target_service = DebugTargetService(config, rdk)

    # Save angled tip path service so the program can use it later.
    angled_tip_path_service = AngledTipPathService(
        # This line helps the program do the next small step.
        config,
        # This line helps the program do the next small step.
        robot_controller,
        # This line helps the program do the next small step.
        camera_calibration,
        # This line helps the program do the next small step.
        seam_path_generator,
        # This line helps the program do the next small step.
        angled_tcp_pose_builder,
        # This line helps the program do the next small step.
        debug_target_service
    # Close this group of values.
    )

    # This line helps the program do the next small step.
    angled_tip_path_service.run()


# Run the main function only when this file is started directly.
if __name__ == "__main__":
    # Start the program.
    main()
