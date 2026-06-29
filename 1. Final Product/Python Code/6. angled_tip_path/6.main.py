import sys
from pathlib import Path


ROBODK_PYTHON_FOLDER = Path("C:/RoboDK/Python")

if ROBODK_PYTHON_FOLDER.exists():
    sys.path.insert(0, str(ROBODK_PYTHON_FOLDER))

from robodk.robolink import Robolink, ITEM_TYPE_ROBOT


PROJECT_FOLDER_NAME = "6. angled_tip_path"

REQUIRED_PROJECT_FILES = [
    "config.py",
    "angled_tcp_pose_builder.py",
    "angled_tip_path_service.py",
    "camera_calibration.py",
    "debug_target_service.py",
    "robot_controller.py",
    "seam_path_generator.py",
]


def is_correct_project_folder(folder: Path) -> bool:
    return folder.exists() and folder.is_dir() and all(
        (folder / file_name).exists()
        for file_name in REQUIRED_PROJECT_FILES
    )


def find_project_folder() -> Path:
    current_folder = Path(__file__).resolve().parent
    working_folder = Path.cwd().resolve()
    home_folder = Path.home()

    possible_folders = [
        current_folder,
        working_folder,
        home_folder / "Desktop" / PROJECT_FOLDER_NAME,
        home_folder / "OneDrive" / "Desktop" / PROJECT_FOLDER_NAME,
        home_folder / "Documents" / PROJECT_FOLDER_NAME,
        home_folder / "Downloads" / PROJECT_FOLDER_NAME,
    ]

    possible_folders.extend(current_folder.parents)
    possible_folders.extend(working_folder.parents)

    for folder in possible_folders:
        if is_correct_project_folder(folder):
            return folder.resolve()

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

        try:
            for folder in search_location.rglob(PROJECT_FOLDER_NAME):
                if is_correct_project_folder(folder):
                    return folder.resolve()
        except PermissionError:
            continue

    raise FileNotFoundError(
        "Could not find the project folder automatically.\n\n"
        f"Expected folder name:\n{PROJECT_FOLDER_NAME}\n\n"
        "The folder must contain:\n"
        + "\n".join(f"- {file_name}" for file_name in REQUIRED_PROJECT_FILES)
        + "\n\n"
        "Place the full project folder inside Desktop, OneDrive/Desktop, "
        "Documents, Downloads, or your user folder."
    )


PROJECT_FOLDER = find_project_folder()

project_folder_string = str(PROJECT_FOLDER)

if project_folder_string in sys.path:
    sys.path.remove(project_folder_string)

sys.path.insert(0, project_folder_string)

for module_name in [
    "config",
    "angled_tcp_pose_builder",
    "angled_tip_path_service",
    "camera_calibration",
    "debug_target_service",
    "robot_controller",
    "seam_path_generator",
]:
    sys.modules.pop(module_name, None)

print("Using project folder:")
print(PROJECT_FOLDER)

from angled_tcp_pose_builder import AngledTcpPoseBuilder
from angled_tip_path_service import AngledTipPathService
from camera_calibration import CameraCalibration
from config import Config
from debug_target_service import DebugTargetService
from robot_controller import RobotController
from seam_path_generator import SeamPathGenerator


def main():
    config = Config()

    rdk = Robolink()

    robot = rdk.ItemUserPick(
        "Select your Doosan M0609 robot",
        ITEM_TYPE_ROBOT
    )

    if not robot.Valid():
        raise Exception("No valid robot selected.")

    print("Selected robot:", robot.Name())

    robot_controller = RobotController(
        config,
        rdk,
        robot
    )

    robot_controller.connect()

    camera_calibration = CameraCalibration(config)
    seam_path_generator = SeamPathGenerator(config)
    angled_tcp_pose_builder = AngledTcpPoseBuilder(config)
    debug_target_service = DebugTargetService(config, rdk)

    angled_tip_path_service = AngledTipPathService(
        config,
        robot_controller,
        camera_calibration,
        seam_path_generator,
        angled_tcp_pose_builder,
        debug_target_service
    )

    angled_tip_path_service.run()


if __name__ == "__main__":
    main()