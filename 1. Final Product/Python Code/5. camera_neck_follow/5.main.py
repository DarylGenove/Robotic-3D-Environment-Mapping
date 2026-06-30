# Bring in sys so Python can change where it searches for files.
import sys
# Bring in Path so the code can work with folders and files.
from pathlib import Path


# Store the RoboDK Python folder path.
ROBODK_PYTHON_FOLDER = Path("C:/RoboDK/Python")

# Check if the RoboDK Python folder exists on this computer.
if ROBODK_PYTHON_FOLDER.exists():
    # Add this folder so Python can import the needed RoboDK or project files.
    sys.path.insert(0, str(ROBODK_PYTHON_FOLDER))

# Bring in RoboDK tools so the script can talk to RoboDK.
from robodk.robolink import Robolink, ITEM_TYPE_ROBOT


# Store the name of this project folder.
PROJECT_FOLDER_NAME = "5. camera_neck_follow"

# List the files that must exist in the correct project folder.
REQUIRED_PROJECT_FILES = [
    # Add this value to the current list or function call.
    "config.py",
    # Add this value to the current list or function call.
    "camera_calibration.py",
    # Add this value to the current list or function call.
    "camera_neck_follow_service.py",
    # Add this value to the current list or function call.
    "camera_pose_builder.py",
    # Add this value to the current list or function call.
    "debug_target_service.py",
    # Add this value to the current list or function call.
    "look_line_generator.py",
    # Add this value to the current list or function call.
    "robot_controller.py",
]


# Create the is correct project folder function.
def is_correct_project_folder(folder: Path) -> bool:
    # Say yes only if this folder exists and has all required files.
    return folder.exists() and folder.is_dir() and all(
        # Run this line as one small step in the program.
        (folder / file_name).exists()
        # Repeat this block for each item in the group.
        for file_name in REQUIRED_PROJECT_FILES
    )


# Create the find project folder function.
def find_project_folder() -> Path:
    # Save a value in current folder.
    current_folder = Path(__file__).resolve().parent
    # Save a value in working folder.
    working_folder = Path.cwd().resolve()
    # Save a value in home folder.
    home_folder = Path.home()

    # Save a value in possible folders.
    possible_folders = [
        # Add this value to the current list or function call.
        current_folder,
        # Add this value to the current list or function call.
        working_folder,
        # Add this value to the current list or function call.
        home_folder / "Desktop" / PROJECT_FOLDER_NAME,
        # Add this value to the current list or function call.
        home_folder / "OneDrive" / "Desktop" / PROJECT_FOLDER_NAME,
        # Add this value to the current list or function call.
        home_folder / "Documents" / PROJECT_FOLDER_NAME,
        # Add this value to the current list or function call.
        home_folder / "Downloads" / PROJECT_FOLDER_NAME,
    ]

    # Run this line as one small step in the program.
    possible_folders.extend(current_folder.parents)
    # Run this line as one small step in the program.
    possible_folders.extend(working_folder.parents)

    # Try every folder that might be the project folder.
    for folder in possible_folders:
        # Check if this folder has all the project files.
        if is_correct_project_folder(folder):
            # Return the full clean path to this folder.
            return folder.resolve()

    # Save a value in search locations.
    search_locations = [
        # Add this value to the current list or function call.
        home_folder / "Desktop",
        # Add this value to the current list or function call.
        home_folder / "OneDrive" / "Desktop",
        # Add this value to the current list or function call.
        home_folder / "Documents",
        # Add this value to the current list or function call.
        home_folder / "Downloads",
        # Add this value to the current list or function call.
        home_folder,
    ]

    # Try each common Windows place where the project may be stored.
    for search_location in search_locations:
        # Skip this search place if it does not exist.
        if not search_location.exists():
            # Skip this item and move to the next one.
            continue

        # Try this block because it may fail safely.
        try:
            # Search inside this place for the project folder name.
            for folder in search_location.rglob(PROJECT_FOLDER_NAME):
                # Check if this folder has all the project files.
                if is_correct_project_folder(folder):
                    # Return the full clean path to this folder.
                    return folder.resolve()
        # Ignore folders that Windows does not allow the code to read.
        except PermissionError:
            # Skip this item and move to the next one.
            continue

    # Stop the program because the project folder could not be found.
    raise FileNotFoundError(
        # Run this line as one small step in the program.
        "Could not find the project folder automatically.\n\n"
        # Run this line as one small step in the program.
        f"Expected folder name:\n{PROJECT_FOLDER_NAME}\n\n"
        # Run this line as one small step in the program.
        "The folder must contain:\n"
        # Add this text to the message.
        + "\n".join(f"- {file_name}" for file_name in REQUIRED_PROJECT_FILES)
        # Add this text to the message.
        + "\n\n"
        # Run this line as one small step in the program.
        "Place the full project folder inside Desktop, OneDrive/Desktop, "
        # Run this line as one small step in the program.
        "Documents, Downloads, or your user folder."
    )


# Find and save the correct project folder.
PROJECT_FOLDER = find_project_folder()

# Save a value in project folder string.
project_folder_string = str(PROJECT_FOLDER)

# Check this condition before continuing.
if project_folder_string in sys.path:
    # Run this line as one small step in the program.
    sys.path.remove(project_folder_string)

# Add this folder so Python can import the needed RoboDK or project files.
sys.path.insert(0, project_folder_string)

# Go through each module that should be freshly imported.
for module_name in [
    # Add this value to the current list or function call.
    "config",
    # Add this value to the current list or function call.
    "camera_calibration",
    # Add this value to the current list or function call.
    "camera_neck_follow_service",
    # Add this value to the current list or function call.
    "camera_pose_builder",
    # Add this value to the current list or function call.
    "debug_target_service",
    # Add this value to the current list or function call.
    "look_line_generator",
    # Add this value to the current list or function call.
    "robot_controller",
# Run this line as one small step in the program.
]:
    # Run this line as one small step in the program.
    sys.modules.pop(module_name, None)

# Show this message on the screen.
print("Using project folder:")
# Show this message on the screen.
print(PROJECT_FOLDER)

# Bring in the helper that knows the camera mounting transform.
from camera_calibration import CameraCalibration
# Bring in the main service that performs the neck-follow movement.
from camera_neck_follow_service import CameraNeckFollowService
# Bring in the helper that builds camera look-at poses.
from camera_pose_builder import CameraPoseBuilder
# Bring in the settings from config.py.
from config import Config
# Bring in the helper that creates debug targets in RoboDK.
from debug_target_service import DebugTargetService
# Bring in the helper that makes the line of look points.
from look_line_generator import LookLineGenerator
# Bring in the helper that moves and checks the robot.
from robot_controller import RobotController


# Create the main function that starts the whole program.
def main():
    # Create the settings object.
    config = Config()

    # Open a connection to the running RoboDK program.
    rdk = Robolink()

    # Ask the user to select the Doosan robot in RoboDK.
    robot = rdk.ItemUserPick(
        # Add this value to the current list or function call.
        "Select your Doosan M0609 robot",
        # Use this RoboDK name later in the program.
        ITEM_TYPE_ROBOT
    )

    # Check if the user did not select a valid robot.
    if not robot.Valid():
        # Stop the program because something important is wrong.
        raise Exception("No valid robot selected.")

    # Show this message on the screen.
    print("Selected robot:", robot.Name())

    # Create the robot helper object.
    robot_controller = RobotController(
        # Add this value to the current list or function call.
        config,
        # Add this value to the current list or function call.
        rdk,
        # Run this line as one small step in the program.
        robot
    )

    # Connect to the robot or to RoboDK simulation.
    robot_controller.connect()

    # Create the helper for camera calibration values.
    camera_calibration = CameraCalibration(config)
    # Create the helper that makes look points.
    look_line_generator = LookLineGenerator(config)
    # Create the helper that builds camera poses.
    camera_pose_builder = CameraPoseBuilder(config)
    # Create the helper that draws debug targets.
    debug_target_service = DebugTargetService(config, rdk)

    # Create the main neck-follow service.
    camera_neck_follow_service = CameraNeckFollowService(
        # Add this value to the current list or function call.
        config,
        # Add this value to the current list or function call.
        robot_controller,
        # Add this value to the current list or function call.
        camera_calibration,
        # Add this value to the current list or function call.
        look_line_generator,
        # Add this value to the current list or function call.
        camera_pose_builder,
        # Run this line as one small step in the program.
        debug_target_service
    )

    # Start the full camera-neck-follow movement.
    camera_neck_follow_service.run()


# Run main only when this file is started directly.
if __name__ == "__main__":
    # Start the main program.
    main()
