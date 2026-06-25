import sys
from pathlib import Path

sys.path.append("C:/RoboDK/Python")

from robodk.robolink import Robolink, ITEM_TYPE_ROBOT


PROJECT_FOLDER = Path(
    r"C:\Users\daryl\Desktop\Robotic D Environment Mapping\Robotic-3D-Environment-Mapping\1. Final Product\Python Code\6. angled_tip_path"
)

CURRENT_FOLDER = Path(__file__).resolve().parent

if (PROJECT_FOLDER / "config.py").exists():
    sys.path.insert(0, str(PROJECT_FOLDER))
elif (CURRENT_FOLDER / "config.py").exists():
    sys.path.insert(0, str(CURRENT_FOLDER))
else:
    raise FileNotFoundError(
        "config.py was not found. Change PROJECT_FOLDER in main.py "
        "to the real folder that contains config.py."
    )

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
