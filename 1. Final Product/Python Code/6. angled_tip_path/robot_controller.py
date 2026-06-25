import sys
import time

sys.path.append("C:/RoboDK/Python")

from robodk.robolink import (
    ROBOTCOM_READY,
    RUNMODE_RUN_ROBOT,
    RUNMODE_SIMULATE,
)

from transform_utils import TransformUtils


class RobotController:
    def __init__(self, config, rdk, robot):
        self.config = config
        self.rdk = rdk
        self.robot = robot

    def connect(self):
        if self.config.RUN_ON_REAL_ROBOT:
            self.rdk.setRunMode(RUNMODE_RUN_ROBOT)

            status = self.robot.ConnectSafe()
            print("ConnectSafe status:", status)

            if status != ROBOTCOM_READY:
                raise Exception(
                    "Robot is not ready. Check RoboDK connection settings."
                )
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
                return TransformUtils.joints_to_list(
                    self.robot.Joints()
                )
            except Exception:
                if time.time() - start > timeout_sec:
                    raise Exception("Could not read robot joints.")

                time.sleep(self.config.POLL_INTERVAL_SEC)

    def move_to_joints(self, joints, label):
        target = self.rdk.AddTarget(f"_angled_tip_path_{label}")
        target.setAsJointTarget()
        target.setJoints(joints)

        print(f"\nMoving to {label}: {[round(joint, 2) for joint in joints]}")

        self._set_run_mode()

        self.robot.MoveJ(target, blocking=False)

        self.wait_until_robot_stops()

        target.Delete()

        print(
            f"Arrived at {label}. "
            f"Settling for {self.config.SETTLE_TIME:.1f} seconds..."
        )
        time.sleep(self.config.SETTLE_TIME)

        return self.get_joints_when_ready()

    def move_to_pose(
        self,
        tcp_pose_base,
        seed_joints,
        locked_j6_value,
        label
    ):
        target = self.rdk.AddTarget(f"_angled_tip_path_{label}")
        target_pose = TransformUtils.numpy_to_robodk_mat(tcp_pose_base)

        target.setPose(target_pose)
        target.setAsCartesianTarget()

        seed = list(seed_joints)

        if self.config.LOCK_J6_WITH_SEED:
            seed[5] = locked_j6_value

        target.setJoints(seed)

        print(f"\nMoving to angled tip pose: {label}")
        print("Target TCP position in robot base frame:")
        print(f"X: {tcp_pose_base[0, 3] * 1000.0:.1f} mm")
        print(f"Y: {tcp_pose_base[1, 3] * 1000.0:.1f} mm")
        print(f"Z: {tcp_pose_base[2, 3] * 1000.0:.1f} mm")
        print("Seed joints:")
        print([round(joint, 2) for joint in seed])

        self._set_run_mode()

        self.robot.MoveJ(target, blocking=False)

        self.wait_until_robot_stops()

        actual_joints = self.get_joints_when_ready()

        target.Delete()

        print(
            f"Arrived at {label}. "
            f"Settling for {self.config.SETTLE_TIME:.1f} seconds..."
        )
        print("Actual joints:")
        print([round(joint, 2) for joint in actual_joints])
        print("Actual J6:", round(actual_joints[5], 2))

        if abs(actual_joints[5] - locked_j6_value) > self.config.MAX_J6_WARNING_DEGREES:
            print("")
            print("WARNING: J6 changed more than expected.")
            print("The angle may require a different wrist configuration.")

        time.sleep(self.config.SETTLE_TIME)

        return actual_joints

    def solve_fk_to_numpy(self, joints):
        return TransformUtils.robodk_mat_to_numpy(
            self.robot.SolveFK(joints)
        )

    def is_pose_safe(self, tcp_pose_base, label):
        tcp_z_mm = tcp_pose_base[2, 3] * 1000.0

        if tcp_z_mm < self.config.MIN_SAFE_TCP_Z_MM:
            print("")
            print(f"SKIPPING {label}")
            print(f"Reason: TCP Z is too low: {tcp_z_mm:.1f} mm")
            return False

        return True

    def _set_run_mode(self):
        if self.config.RUN_ON_REAL_ROBOT:
            self.rdk.setRunMode(RUNMODE_RUN_ROBOT)
        else:
            self.rdk.setRunMode(RUNMODE_SIMULATE)
