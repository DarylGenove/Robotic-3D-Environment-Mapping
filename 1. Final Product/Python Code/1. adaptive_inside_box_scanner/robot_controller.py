import sys
import time

sys.path.append("C:/RoboDK/Python")

from robodk.robolink import *

from transform_utils import joints_to_list, numpy_to_robodk_mat


class RobotController:
    def __init__(self, config, rdk, robot):
        self.config = config
        self.rdk = rdk
        self.robot = robot

    @classmethod
    def create_from_user_selection(cls, config):
        rdk = Robolink()
        robot = rdk.ItemUserPick("Select your Doosan M0609 robot", ITEM_TYPE_ROBOT)

        if not robot.Valid():
            raise Exception("No valid robot selected.")

        print("Selected robot:", robot.Name())
        return cls(config, rdk, robot)

    def connect(self):
        if self.config.RUN_ON_REAL_ROBOT:
            self.rdk.setRunMode(RUNMODE_RUN_ROBOT)

            status = self.robot.ConnectSafe()
            print("ConnectSafe status:", status)

            if status != ROBOTCOM_READY:
                raise Exception("Robot is not ready. Check RoboDK connection settings.")
        else:
            self.rdk.setRunMode(RUNMODE_SIMULATE)
            print("Running in RoboDK simulation mode.")

    def wait_until_robot_stops(self, timeout_sec=None):
        if timeout_sec is None:
            timeout_sec = self.config.MOVE_TIMEOUT_SEC

        start = time.time()

        while True:
            try:
                if not self.robot.Busy():
                    return
            except Exception:
                pass

            if time.time() - start > timeout_sec:
                raise Exception("Timeout waiting for robot to stop.")

            time.sleep(self.config.POLL_INTERVAL_SEC)

    def get_joints_when_ready(self, timeout_sec=5.0):
        start = time.time()

        while True:
            try:
                return joints_to_list(self.robot.Joints())
            except Exception:
                if time.time() - start > timeout_sec:
                    raise Exception("Could not read robot joints.")

                time.sleep(self.config.POLL_INTERVAL_SEC)

    def set_run_mode(self):
        if self.config.RUN_ON_REAL_ROBOT:
            self.rdk.setRunMode(RUNMODE_RUN_ROBOT)
        else:
            self.rdk.setRunMode(RUNMODE_SIMULATE)

    def move_to_joints(self, joints, label):
        target = self.rdk.AddTarget(f"_adaptive_inside_box_{label}")
        target.setAsJointTarget()
        target.setJoints(joints)

        print(f"\nMoving to {label}: {[round(joint, 2) for joint in joints]}")

        self.set_run_mode()
        self.robot.MoveJ(target, blocking=False)
        self.wait_until_robot_stops()
        target.Delete()

        print(f"Arrived at {label}. Settling for {self.config.SETTLE_TIME:.1f} seconds...")
        time.sleep(self.config.SETTLE_TIME)

        return self.get_joints_when_ready()

    def move_to_pose(self, T_base_tcp, label):
        target = self.rdk.AddTarget(f"_adaptive_inside_box_{label}")
        target_pose = numpy_to_robodk_mat(T_base_tcp)

        target.setPose(target_pose)
        target.setAsCartesianTarget()

        print(f"\nMoving to generated pose: {label}")
        print("Target TCP position in robot base frame:")
        print(f"X: {T_base_tcp[0, 3] * 1000.0:.1f} mm")
        print(f"Y: {T_base_tcp[1, 3] * 1000.0:.1f} mm")
        print(f"Z: {T_base_tcp[2, 3] * 1000.0:.1f} mm")

        self.set_run_mode()
        self.robot.MoveJ(target, blocking=False)
        self.wait_until_robot_stops()
        target.Delete()

        print(f"Arrived at {label}. Settling for {self.config.SETTLE_TIME:.1f} seconds...")
        time.sleep(self.config.SETTLE_TIME)

        return self.get_joints_when_ready()

    def is_generated_pose_safe(self, T_base_tcp, T_base_camera, label):
        tcp_z_mm = T_base_tcp[2, 3] * 1000.0
        camera_z_mm = T_base_camera[2, 3] * 1000.0

        if tcp_z_mm < self.config.MIN_SAFE_TCP_Z_MM:
            print("")
            print(f"SKIPPING {label}")
            print(f"Reason: TCP Z is too low: {tcp_z_mm:.1f} mm")
            print(f"Minimum safe TCP Z: {self.config.MIN_SAFE_TCP_Z_MM:.1f} mm")
            return False

        if camera_z_mm < self.config.MIN_SAFE_CAMERA_Z_MM:
            print("")
            print(f"SKIPPING {label}")
            print(f"Reason: Camera Z is too low: {camera_z_mm:.1f} mm")
            print(f"Minimum safe camera Z: {self.config.MIN_SAFE_CAMERA_Z_MM:.1f} mm")
            return False

        return True
