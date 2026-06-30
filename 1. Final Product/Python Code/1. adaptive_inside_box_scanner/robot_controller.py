import sys  # Loads sys so the code can change where Python looks for files.
import time  # Loads time so the code can wait and measure seconds.

sys.path.append("C:/RoboDK/Python")  # Runs this line as one small step in the program.

from robodk.robolink import *  # Gets * from robodk.robolink so this file can use it.

from transform_utils import joints_to_list, numpy_to_robodk_mat  # Gets joints_to_list, numpy_to_robodk_mat from transform_utils so this file can use it.


class RobotController:  # Makes a toolbox for connecting to RoboDK and moving the robot.
    def __init__(self, config, rdk, robot):  # Makes a function named   init  .
        self.config = config  # Stores the scanner settings so the program can use them.
        self.rdk = rdk  # Saves rdk inside this object so other methods can use it.
        self.robot = robot  # Saves robot inside this object so other methods can use it.

    @classmethod  # Lets this method create the object without needing an object first.
    def create_from_user_selection(cls, config):  # Lets the user select the robot from RoboDK.
        rdk = Robolink()  # Stores rdk for use in the next steps.
        robot = rdk.ItemUserPick("Select your Doosan M0609 robot", ITEM_TYPE_ROBOT)  # Stores robot for use in the next steps.

        if not robot.Valid():  # Checks if this condition is not true.
            raise Exception("No valid robot selected.")  # Stops the program because something important went wrong.

        print("Selected robot:", robot.Name())  # Shows a message in the console.
        return cls(config, rdk, robot)  # Gives this result back to the part of the code that called it.

    def connect(self):  # Connects RoboDK to either the real robot or simulation.
        if self.config.RUN_ON_REAL_ROBOT:  # Checks a condition before running the next indented lines.
            self.rdk.setRunMode(RUNMODE_RUN_ROBOT)  # Tells RoboDK whether to simulate or move the real robot.

            status = self.robot.ConnectSafe()  # Stores the robot connection result.
            print("ConnectSafe status:", status)  # Shows a message in the console.

            if status != ROBOTCOM_READY:  # Checks a condition before running the next indented lines.
                raise Exception("Robot is not ready. Check RoboDK connection settings.")  # Stops the program because something important went wrong.
        else:  # Runs this part when the earlier condition was not true.
            self.rdk.setRunMode(RUNMODE_SIMULATE)  # Tells RoboDK whether to simulate or move the real robot.
            print("Running in RoboDK simulation mode.")  # Shows a message in the console.

    def wait_until_robot_stops(self, timeout_sec=None):  # Waits until the robot finishes moving.
        if timeout_sec is None:  # Checks if this value is missing.
            timeout_sec = self.config.MOVE_TIMEOUT_SEC  # Stores timeout sec for use in the next steps.

        start = time.time()  # Stores the time when waiting began.

        while True:  # Keeps repeating until the code returns, breaks, or raises an error.
            try:  # Tries the next steps because they might fail.
                if not self.robot.Busy():  # Checks if this condition is not true.
                    return  # Gives this result back to the part of the code that called it.
            except Exception:  # Runs this part if something goes wrong.
                pass  # Does nothing here, but keeps the code valid.

            if time.time() - start > timeout_sec:  # Checks a condition before running the next indented lines.
                raise Exception("Timeout waiting for robot to stop.")  # Stops the program because something important went wrong.

            time.sleep(self.config.POLL_INTERVAL_SEC)  # Waits for a short time.

    def get_joints_when_ready(self, timeout_sec=5.0):  # Reads the robot joints when they are available.
        start = time.time()  # Stores the time when waiting began.

        while True:  # Keeps repeating until the code returns, breaks, or raises an error.
            try:  # Tries the next steps because they might fail.
                return joints_to_list(self.robot.Joints())  # Gives this result back to the part of the code that called it.
            except Exception:  # Runs this part if something goes wrong.
                if time.time() - start > timeout_sec:  # Checks a condition before running the next indented lines.
                    raise Exception("Could not read robot joints.")  # Stops the program because something important went wrong.

                time.sleep(self.config.POLL_INTERVAL_SEC)  # Waits for a short time.

    def set_run_mode(self):  # Sets RoboDK to real robot mode or simulation mode.
        if self.config.RUN_ON_REAL_ROBOT:  # Checks a condition before running the next indented lines.
            self.rdk.setRunMode(RUNMODE_RUN_ROBOT)  # Tells RoboDK whether to simulate or move the real robot.
        else:  # Runs this part when the earlier condition was not true.
            self.rdk.setRunMode(RUNMODE_SIMULATE)  # Tells RoboDK whether to simulate or move the real robot.

    def move_to_joints(self, joints, label):  # Moves the robot to a target using joint angles.
        target = self.rdk.AddTarget(f"_adaptive_inside_box_{label}")  # Creates a temporary RoboDK target for the robot to move to.
        target.setAsJointTarget()  # Makes the target use joint angles.
        target.setJoints(joints)  # Reads the robot joint angles.

        print(f"\nMoving to {label}: {[round(joint, 2) for joint in joints]}")  # Shows a message in the console.

        self.set_run_mode()  # Runs this line as one small step in the program.
        self.robot.MoveJ(target, blocking=False)  # Moves the robot with a joint movement.
        self.wait_until_robot_stops()  # Runs this line as one small step in the program.
        target.Delete()  # Removes the temporary RoboDK target.

        print(f"Arrived at {label}. Settling for {self.config.SETTLE_TIME:.1f} seconds...")  # Shows a message in the console.
        time.sleep(self.config.SETTLE_TIME)  # Waits for a short time.

        return self.get_joints_when_ready()  # Gives this result back to the part of the code that called it.

    def move_to_pose(self, T_base_tcp, label):  # Moves the robot to a generated 3D pose.
        target = self.rdk.AddTarget(f"_adaptive_inside_box_{label}")  # Creates a temporary RoboDK target for the robot to move to.
        target_pose = numpy_to_robodk_mat(T_base_tcp)  # Stores the RoboDK version of the target pose.

        target.setPose(target_pose)  # Stores a 3D pose inside the target.
        target.setAsCartesianTarget()  # Makes the target use a 3D position and rotation.

        print(f"\nMoving to generated pose: {label}")  # Shows a message in the console.
        print("Target TCP position in robot base frame:")  # Shows a message in the console.
        print(f"X: {T_base_tcp[0, 3] * 1000.0:.1f} mm")  # Shows a message in the console.
        print(f"Y: {T_base_tcp[1, 3] * 1000.0:.1f} mm")  # Shows a message in the console.
        print(f"Z: {T_base_tcp[2, 3] * 1000.0:.1f} mm")  # Shows a message in the console.

        self.set_run_mode()  # Runs this line as one small step in the program.
        self.robot.MoveJ(target, blocking=False)  # Moves the robot with a joint movement.
        self.wait_until_robot_stops()  # Runs this line as one small step in the program.
        target.Delete()  # Removes the temporary RoboDK target.

        print(f"Arrived at {label}. Settling for {self.config.SETTLE_TIME:.1f} seconds...")  # Shows a message in the console.
        time.sleep(self.config.SETTLE_TIME)  # Waits for a short time.

        return self.get_joints_when_ready()  # Gives this result back to the part of the code that called it.

    def is_generated_pose_safe(self, T_base_tcp, T_base_camera, label):  # Checks if the planned pose is safe before moving.
        tcp_z_mm = T_base_tcp[2, 3] * 1000.0  # Stores tcp z mm for use in the next steps.
        camera_z_mm = T_base_camera[2, 3] * 1000.0  # Stores camera z mm for use in the next steps.

        if tcp_z_mm < self.config.MIN_SAFE_TCP_Z_MM:  # Checks a condition before running the next indented lines.
            print("")  # Shows a message in the console.
            print(f"SKIPPING {label}")  # Shows a message in the console.
            print(f"Reason: TCP Z is too low: {tcp_z_mm:.1f} mm")  # Shows a message in the console.
            print(f"Minimum safe TCP Z: {self.config.MIN_SAFE_TCP_Z_MM:.1f} mm")  # Shows a message in the console.
            return False  # Gives this result back to the part of the code that called it.

        if camera_z_mm < self.config.MIN_SAFE_CAMERA_Z_MM:  # Checks a condition before running the next indented lines.
            print("")  # Shows a message in the console.
            print(f"SKIPPING {label}")  # Shows a message in the console.
            print(f"Reason: Camera Z is too low: {camera_z_mm:.1f} mm")  # Shows a message in the console.
            print(f"Minimum safe camera Z: {self.config.MIN_SAFE_CAMERA_Z_MM:.1f} mm")  # Shows a message in the console.
            return False  # Gives this result back to the part of the code that called it.

        return True  # Gives this result back to the part of the code that called it.
