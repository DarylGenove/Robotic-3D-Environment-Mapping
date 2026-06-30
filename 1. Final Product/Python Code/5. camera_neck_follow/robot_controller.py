# Bring in sys so Python can change where it searches for files.
import sys
# Bring in time so the code can wait and check timeouts.
import time

# Add this folder so Python can import the needed RoboDK or project files.
sys.path.append("C:/RoboDK/Python")

# Bring in RoboDK constants used for robot connection and run mode.
from robodk.robolink import (
    # Use this RoboDK name later in the program.
    ROBOTCOM_READY,
    # Use this RoboDK name later in the program.
    RUNMODE_RUN_ROBOT,
    # Use this RoboDK name later in the program.
    RUNMODE_SIMULATE,
)

# Bring in TransformUtils so this file can reuse 3D transform helpers.
from transform_utils import TransformUtils


# Create the RobotController class so related code stays together.
class RobotController:
    # Create the setup function that saves the things this object needs.
    def __init__(self, config, rdk, robot):
        # Save a value in config.
        self.config = config
        # Save a value in rdk.
        self.rdk = rdk
        # Save a value in robot.
        self.robot = robot

    # Create the function that connects RoboDK to the robot or simulation.
    def connect(self):
        # Check if the program should control the real robot.
        if self.config.RUN_ON_REAL_ROBOT:
            # Tell RoboDK to run the real robot.
            self.rdk.setRunMode(RUNMODE_RUN_ROBOT)

            # Save a value in status.
            status = self.robot.ConnectSafe()
            # Show this message on the screen.
            print("ConnectSafe status:", status)

            # Check if the robot connection is not ready.
            if status != ROBOTCOM_READY:
                # Stop the program because something important is wrong.
                raise Exception(
                    # Run this line as one small step in the program.
                    "Robot is not ready. Check RoboDK connection settings."
                )
        # Use this second path when the first condition was false.
        else:
            # Tell RoboDK to only simulate the movement.
            self.rdk.setRunMode(RUNMODE_SIMULATE)
            # Show this message on the screen.
            print("Running in RoboDK simulation mode.")

    # Create the function that waits until the robot is finished moving.
    def wait_until_robot_stops(self, timeout_sec=None):
        # Use the default move timeout if no custom timeout was given.
        if timeout_sec is None:
            # Save a value in timeout sec.
            timeout_sec = self.config.MOVE_TIMEOUT_SEC

        # Save a value in start.
        start = time.time()

        # Run this line as one small step in the program.
        while True:
            # Try this block because it may fail safely.
            try:
                # Check if the robot is no longer moving.
                if not self.robot.Busy():
                    # Run this line as one small step in the program.
                    return
            # Handle a problem and try the backup option.
            except Exception:
                # Do nothing here and keep going.
                pass

            # Stop waiting if the robot took too long.
            if time.time() - start > timeout_sec:
                # Stop the program because something important is wrong.
                raise Exception("Timeout waiting for robot to stop.")

            # Run this line as one small step in the program.
            time.sleep(self.config.POLL_INTERVAL_SEC)

    # Create the function that reads the robot joint angles when they are available.
    def get_joints_when_ready(self, timeout_sec=5.0):
        # Save a value in start.
        start = time.time()

        # Run this line as one small step in the program.
        while True:
            # Try this block because it may fail safely.
            try:
                # Give back the converted robot pose as a NumPy matrix.
                return TransformUtils.joints_to_list(self.robot.Joints())
            # Handle a problem and try the backup option.
            except Exception:
                # Stop waiting if the robot took too long.
                if time.time() - start > timeout_sec:
                    # Stop the program because something important is wrong.
                    raise Exception("Could not read robot joints.")

                # Run this line as one small step in the program.
                time.sleep(self.config.POLL_INTERVAL_SEC)

    # Create the function that moves the robot to a saved joint position.
    def move_to_joints(self, joints, label):
        # Create a new RoboDK target with this name.
        target = self.rdk.AddTarget(f"_camera_neck_follow_{label}")
        # Tell RoboDK that this target uses joint angles.
        target.setAsJointTarget()
        # Put the requested joint angles into the target.
        target.setJoints(joints)

        # Show this message on the screen.
        print(f"\nMoving to {label}: {[round(joint, 2) for joint in joints]}")

        # Choose real robot mode or simulation mode before moving.
        self._set_run_mode()

        # Start a joint movement without freezing Python.
        self.robot.MoveJ(target, blocking=False)

        # Wait until the robot finishes the movement.
        self.wait_until_robot_stops()

        # Delete the temporary target after using it.
        target.Delete()

        # Show this message on the screen.
        print(
            # Run this line as one small step in the program.
            f"Arrived at {label}. "
            # Run this line as one small step in the program.
            f"Settling for {self.config.SETTLE_TIME:.1f} seconds..."
        )
        # Wait a little so the robot can settle after moving.
        time.sleep(self.config.SETTLE_TIME)

        # Give this result back to the code that asked for it.
        return self.get_joints_when_ready()

    # Create the function that moves the robot TCP to a 3D pose.
    def move_to_pose(self, tcp_pose_base, label):
        # Create a new RoboDK target with this name.
        target = self.rdk.AddTarget(f"_camera_neck_follow_{label}")
        # Save a value in target pose.
        target_pose = TransformUtils.numpy_to_robodk_mat(tcp_pose_base)

        # Put the requested 3D pose into the RoboDK target.
        target.setPose(target_pose)
        # Tell RoboDK that this target uses a 3D TCP pose.
        target.setAsCartesianTarget()

        # Show this message on the screen.
        print(f"\nMoving to camera neck pose: {label}")
        # Show this message on the screen.
        print("Target TCP position in robot base frame:")
        # Show this message on the screen.
        print(f"X: {tcp_pose_base[0, 3] * 1000.0:.1f} mm")
        # Show this message on the screen.
        print(f"Y: {tcp_pose_base[1, 3] * 1000.0:.1f} mm")
        # Show this message on the screen.
        print(f"Z: {tcp_pose_base[2, 3] * 1000.0:.1f} mm")

        # Choose real robot mode or simulation mode before moving.
        self._set_run_mode()

        # Start a joint movement without freezing Python.
        self.robot.MoveJ(target, blocking=False)

        # Wait until the robot finishes the movement.
        self.wait_until_robot_stops()

        # Delete the temporary target after using it.
        target.Delete()

        # Show this message on the screen.
        print(
            # Run this line as one small step in the program.
            f"Arrived at {label}. "
            # Run this line as one small step in the program.
            f"Settling for {self.config.SETTLE_TIME:.1f} seconds..."
        )
        # Wait a little so the robot can settle after moving.
        time.sleep(self.config.SETTLE_TIME)

        # Give this result back to the code that asked for it.
        return self.get_joints_when_ready()

    # Create the function that turns robot joints into a 3D position matrix.
    def solve_fk_to_numpy(self, joints):
        # Give back the converted robot pose as a NumPy matrix.
        return TransformUtils.robodk_mat_to_numpy(
            # Run this line as one small step in the program.
            self.robot.SolveFK(joints)
        )

    # Create the function that checks if a generated pose is safely above the table.
    def is_generated_pose_safe(self, tcp_pose_base, camera_pose_base, label):
        # Save a value in tcp z mm.
        tcp_z_mm = tcp_pose_base[2, 3] * 1000.0
        # Save a value in camera z mm.
        camera_z_mm = camera_pose_base[2, 3] * 1000.0

        # Check if the robot TCP is too low to be safe.
        if tcp_z_mm < self.config.MIN_SAFE_TCP_Z_MM:
            # Show this message on the screen.
            print("")
            # Show this message on the screen.
            print(f"SKIPPING {label}")
            # Show this message on the screen.
            print(f"Reason: TCP Z is too low: {tcp_z_mm:.1f} mm")
            # Show this message on the screen.
            print(f"Minimum safe TCP Z: {self.config.MIN_SAFE_TCP_Z_MM:.1f} mm")
            # Say no because this pose or folder is not safe or valid.
            return False

        # Check if the camera is too low to be safe.
        if camera_z_mm < self.config.MIN_SAFE_CAMERA_Z_MM:
            # Show this message on the screen.
            print("")
            # Show this message on the screen.
            print(f"SKIPPING {label}")
            # Show this message on the screen.
            print(f"Reason: Camera Z is too low: {camera_z_mm:.1f} mm")
            # Show this message on the screen.
            print(
                # Run this line as one small step in the program.
                f"Minimum safe camera Z: "
                # Run this line as one small step in the program.
                f"{self.config.MIN_SAFE_CAMERA_Z_MM:.1f} mm"
            )
            # Say no because this pose or folder is not safe or valid.
            return False

        # Say yes because this check passed.
        return True

    # Create the helper that chooses real robot mode or simulation mode.
    def _set_run_mode(self):
        # Check if the program should control the real robot.
        if self.config.RUN_ON_REAL_ROBOT:
            # Tell RoboDK to run the real robot.
            self.rdk.setRunMode(RUNMODE_RUN_ROBOT)
        # Use this second path when the first condition was false.
        else:
            # Tell RoboDK to only simulate the movement.
            self.rdk.setRunMode(RUNMODE_SIMULATE)
