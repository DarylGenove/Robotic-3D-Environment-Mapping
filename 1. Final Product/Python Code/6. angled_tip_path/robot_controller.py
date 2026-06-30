# Bring in the sys toolbox so this file can use it.
import sys
# Bring in the time toolbox so this file can use it.
import time

# Add the RoboDK Python folder so RoboDK tools can be imported.
sys.path.append("C:/RoboDK/Python")

# Bring in ( from robodk.robolink so we can use it here.
from robodk.robolink import (
    # This line helps the program do the next small step.
    ROBOTCOM_READY,
    # This line helps the program do the next small step.
    RUNMODE_RUN_ROBOT,
    # This line helps the program do the next small step.
    RUNMODE_SIMULATE,
# Close this group of values.
)

# Bring in TransformUtils from transform_utils so we can use it here.
from transform_utils import TransformUtils


# Create the RobotController object that groups related actions together.
class RobotController:
    # Start the   init   function.
    def __init__(self, config, rdk, robot):
        # Save config so the program can use it later.
        self.config = config
        # Save rdk so the program can use it later.
        self.rdk = rdk
        # Save robot so the program can use it later.
        self.robot = robot

    # Start the connect function.
    def connect(self):
        # Check if this condition is true.
        if self.config.RUN_ON_REAL_ROBOT:
            # Choose whether RoboDK runs the real robot or only simulation.
            self.rdk.setRunMode(RUNMODE_RUN_ROBOT)

            # Connect to the real robot in a safer way.
            status = self.robot.ConnectSafe()
            # Show a message on the screen.
            print("ConnectSafe status:", status)

            # Check if this condition is true.
            if status != ROBOTCOM_READY:
                # Stop the program and show this problem message.
                raise Exception(
                    # This line helps the program do the next small step.
                    "Robot is not ready. Check RoboDK connection settings."
                # Close this group of values.
                )
        # Use this backup path when the earlier condition was false.
        else:
            # Choose whether RoboDK runs the real robot or only simulation.
            self.rdk.setRunMode(RUNMODE_SIMULATE)
            # Show a message on the screen.
            print("Running in RoboDK simulation mode.")

    # Start the wait until robot stops function.
    def wait_until_robot_stops(self, timeout_sec=None):
        # Check if this condition is true.
        if timeout_sec is None:
            # Save timeout sec so the program can use it later.
            timeout_sec = self.config.MOVE_TIMEOUT_SEC

        # Save start so the program can use it later.
        start = time.time()

        # Keep repeating this step while the condition is true.
        while True:
            # Try this risky step safely.
            try:
                # Check if this condition is true.
                if not self.robot.Busy():
                    # Go back without sending a value.
                    return
            # Handle the problem if the try step fails.
            except Exception:
                # Do nothing here and keep the program valid.
                pass

            # Check if this condition is true.
            if time.time() - start > timeout_sec:
                # Stop the program and show this problem message.
                raise Exception("Timeout waiting for robot to stop.")

            # Wait a little so the robot can settle.
            time.sleep(self.config.POLL_INTERVAL_SEC)

    # Start the get joints when ready function.
    def get_joints_when_ready(self, timeout_sec=5.0):
        # Save start so the program can use it later.
        start = time.time()

        # Keep repeating this step while the condition is true.
        while True:
            # Try this risky step safely.
            try:
                # Send this result back to the place that called the function.
                return TransformUtils.joints_to_list(
                    # Read the current robot joint angles.
                    self.robot.Joints()
                # Close this group of values.
                )
            # Handle the problem if the try step fails.
            except Exception:
                # Check if this condition is true.
                if time.time() - start > timeout_sec:
                    # Stop the program and show this problem message.
                    raise Exception("Could not read robot joints.")

                # Wait a little so the robot can settle.
                time.sleep(self.config.POLL_INTERVAL_SEC)

    # Start the move to joints function.
    def move_to_joints(self, joints, label):
        # Create a temporary target inside RoboDK.
        target = self.rdk.AddTarget(f"_angled_tip_path_{label}")
        # Tell RoboDK this target uses joint angles.
        target.setAsJointTarget()
        # Save joint angles inside the RoboDK target.
        target.setJoints(joints)

        # Show a message on the screen.
        print(f"\nMoving to {label}: {[round(joint, 2) for joint in joints]}")

        # This line helps the program do the next small step.
        self._set_run_mode()

        # Move the robot using a joint movement.
        self.robot.MoveJ(target, blocking=False)

        # This line helps the program do the next small step.
        self.wait_until_robot_stops()

        # Remove the temporary RoboDK item after using it.
        target.Delete()

        # Show a message on the screen.
        print(
            # This line helps the program do the next small step.
            f"Arrived at {label}. "
            # This line helps the program do the next small step.
            f"Settling for {self.config.SETTLE_TIME:.1f} seconds..."
        # Close this group of values.
        )
        # Wait a little so the robot can settle.
        time.sleep(self.config.SETTLE_TIME)

        # Send this result back to the place that called the function.
        return self.get_joints_when_ready()

    # Start the move to pose function.
    def move_to_pose(
        # This line helps the program do the next small step.
        self,
        # This line helps the program do the next small step.
        tcp_pose_base,
        # This line helps the program do the next small step.
        seed_joints,
        # This line helps the program do the next small step.
        locked_j6_value,
        # This line helps the program do the next small step.
        label
    # This line helps the program do the next small step.
    ):
        # Create a temporary target inside RoboDK.
        target = self.rdk.AddTarget(f"_angled_tip_path_{label}")
        # Convert the NumPy 3D pose into RoboDK format.
        target_pose = TransformUtils.numpy_to_robodk_mat(tcp_pose_base)

        # Save the 3D position and rotation inside the RoboDK target.
        target.setPose(target_pose)
        # Tell RoboDK this target uses a 3D pose.
        target.setAsCartesianTarget()

        # Save seed so the program can use it later.
        seed = list(seed_joints)

        # Check if this condition is true.
        if self.config.LOCK_J6_WITH_SEED:
            # Save seed[5] so the program can use it later.
            seed[5] = locked_j6_value

        # Save joint angles inside the RoboDK target.
        target.setJoints(seed)

        # Show a message on the screen.
        print(f"\nMoving to angled tip pose: {label}")
        # Show a message on the screen.
        print("Target TCP position in robot base frame:")
        # Show a message on the screen.
        print(f"X: {tcp_pose_base[0, 3] * 1000.0:.1f} mm")
        # Show a message on the screen.
        print(f"Y: {tcp_pose_base[1, 3] * 1000.0:.1f} mm")
        # Show a message on the screen.
        print(f"Z: {tcp_pose_base[2, 3] * 1000.0:.1f} mm")
        # Show a message on the screen.
        print("Seed joints:")
        # Show a message on the screen.
        print([round(joint, 2) for joint in seed])

        # This line helps the program do the next small step.
        self._set_run_mode()

        # Move the robot using a joint movement.
        self.robot.MoveJ(target, blocking=False)

        # This line helps the program do the next small step.
        self.wait_until_robot_stops()

        # Save actual joints so the program can use it later.
        actual_joints = self.get_joints_when_ready()

        # Remove the temporary RoboDK item after using it.
        target.Delete()

        # Show a message on the screen.
        print(
            # This line helps the program do the next small step.
            f"Arrived at {label}. "
            # This line helps the program do the next small step.
            f"Settling for {self.config.SETTLE_TIME:.1f} seconds..."
        # Close this group of values.
        )
        # Show a message on the screen.
        print("Actual joints:")
        # Show a message on the screen.
        print([round(joint, 2) for joint in actual_joints])
        # Show a message on the screen.
        print("Actual J6:", round(actual_joints[5], 2))

        # Check if this condition is true.
        if abs(actual_joints[5] - locked_j6_value) > self.config.MAX_J6_WARNING_DEGREES:
            # Show a message on the screen.
            print("")
            # Show a message on the screen.
            print("WARNING: J6 changed more than expected.")
            # Show a message on the screen.
            print("The angle may require a different wrist configuration.")

        # Wait a little so the robot can settle.
        time.sleep(self.config.SETTLE_TIME)

        # Send this result back to the place that called the function.
        return actual_joints

    # Start the solve fk to numpy function.
    def solve_fk_to_numpy(self, joints):
        # Send this result back to the place that called the function.
        return TransformUtils.robodk_mat_to_numpy(
            # Convert robot joint angles into a 3D TCP pose.
            self.robot.SolveFK(joints)
        # Close this group of values.
        )

    # Start the is pose safe function.
    def is_pose_safe(self, tcp_pose_base, label):
        # Save tcp z mm so the program can use it later.
        tcp_z_mm = tcp_pose_base[2, 3] * 1000.0

        # Check if this condition is true.
        if tcp_z_mm < self.config.MIN_SAFE_TCP_Z_MM:
            # Show a message on the screen.
            print("")
            # Show a message on the screen.
            print(f"SKIPPING {label}")
            # Show a message on the screen.
            print(f"Reason: TCP Z is too low: {tcp_z_mm:.1f} mm")
            # Send this result back to the place that called the function.
            return False

        # Send this result back to the place that called the function.
        return True

    # Start the  set run mode function.
    def _set_run_mode(self):
        # Check if this condition is true.
        if self.config.RUN_ON_REAL_ROBOT:
            # Choose whether RoboDK runs the real robot or only simulation.
            self.rdk.setRunMode(RUNMODE_RUN_ROBOT)
        # Use this backup path when the earlier condition was false.
        else:
            # Choose whether RoboDK runs the real robot or only simulation.
            self.rdk.setRunMode(RUNMODE_SIMULATE)
