# Bring in NumPy so the code can do 3D math with numbers.
import numpy as np

# Bring in TransformUtils so this file can reuse 3D transform helpers.
from transform_utils import TransformUtils


# Create the CameraNeckFollowService class so related code stays together.
class CameraNeckFollowService:
    # Create the setup function that saves the things this object needs.
    def __init__(
        # Add this value to the current list or function call.
        self,
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
    # Run this line as one small step in the program.
    ):
        # Save a value in config.
        self.config = config
        # Save a value in robot controller.
        self.robot_controller = robot_controller
        # Save a value in camera calibration.
        self.camera_calibration = camera_calibration
        # Save a value in look line generator.
        self.look_line_generator = look_line_generator
        # Save a value in camera pose builder.
        self.camera_pose_builder = camera_pose_builder
        # Save a value in debug target service.
        self.debug_target_service = debug_target_service

    # Create the run function that performs the main task.
    def run(self):
        # Get the transform from robot TCP to camera.
        tcp_to_camera = self.camera_calibration.get_tcp_to_camera_transform()
        # Get the reverse transform from camera to robot TCP.
        camera_to_tcp = np.linalg.inv(tcp_to_camera)

        # Run this line as one small step in the program.
        TransformUtils.print_transform("T_tcp_camera", tcp_to_camera)

        # Try this block because it may fail safely.
        try:
            # Run this line as one small step in the program.
            self.robot_controller.move_to_joints(
                # Add this value to the current list or function call.
                self.config.HOME_JOINTS,
                # Run this line as one small step in the program.
                "Home_Start"
            )

            # Move to the center view and store the real joint values.
            center_actual_joints = self.robot_controller.move_to_joints(
                # Add this value to the current list or function call.
                self.config.CENTER_REFERENCE_JOINTS,
                # Run this line as one small step in the program.
                "Center_Reference_View"
            )

            # Calculate the TCP pose at the center view.
            tcp_pose_base_center = self.robot_controller.solve_fk_to_numpy(
                # Run this line as one small step in the program.
                center_actual_joints
            )

            # Calculate the camera pose at the center view.
            camera_pose_base_center = tcp_pose_base_center @ tcp_to_camera

            # Run this line as one small step in the program.
            TransformUtils.print_transform(
                # Add this value to the current list or function call.
                "T_base_tcp_center",
                # Run this line as one small step in the program.
                tcp_pose_base_center
            )
            # Run this line as one small step in the program.
            TransformUtils.print_transform(
                # Add this value to the current list or function call.
                "T_base_camera_center",
                # Run this line as one small step in the program.
                camera_pose_base_center
            )

            # Generate the points the camera should look at.
            camera_frame_look_points = (
                # Run this line as one small step in the program.
                self.look_line_generator.generate_camera_frame_line_points()
            )

            # Convert the look points into robot-base coordinates.
            look_points_base = (
                # Run this line as one small step in the program.
                self.look_line_generator.transform_look_points_to_base(
                    # Add this value to the current list or function call.
                    camera_pose_base_center,
                    # Run this line as one small step in the program.
                    camera_frame_look_points
                )
            )

            # Choose the camera position that should stay fixed.
            fixed_camera_position_base = (
                # Run this line as one small step in the program.
                self.camera_pose_builder.get_fixed_camera_position(
                    # Run this line as one small step in the program.
                    camera_pose_base_center
                )
            )

            # Build the robot TCP poses needed for the motion.
            tcp_pose_targets = self._generate_tcp_pose_targets(
                # Add this value to the current list or function call.
                camera_pose_base_center,
                # Add this value to the current list or function call.
                fixed_camera_position_base,
                # Add this value to the current list or function call.
                look_points_base,
                # Run this line as one small step in the program.
                camera_to_tcp
            )

            # Run this line as one small step in the program.
            self.debug_target_service.create_debug_targets(
                # Add this value to the current list or function call.
                look_points_base,
                # Add this value to the current list or function call.
                fixed_camera_position_base,
                # Run this line as one small step in the program.
                tcp_pose_targets
            )

            # Run this line as one small step in the program.
            self._run_neck_follow_motion(tcp_pose_targets)

        # Handle the user pressing stop on the keyboard.
        except KeyboardInterrupt:
            # Show this message on the screen.
            print("")
            # Show this message on the screen.
            print("Movement interrupted by user.")

        # Always run this cleanup code at the end.
        finally:
            # Try to return the robot to the safe home position.
            self._move_home_safely()

        # Show this message on the screen.
        print("Done.")

    # Create the helper that builds all robot TCP poses for the neck motion.
    def _generate_tcp_pose_targets(
        # Add this value to the current list or function call.
        self,
        # Add this value to the current list or function call.
        camera_pose_base_center,
        # Add this value to the current list or function call.
        fixed_camera_position_base,
        # Add this value to the current list or function call.
        look_points_base,
        # Run this line as one small step in the program.
        camera_to_tcp
    # Run this line as one small step in the program.
    ):
        # Build the robot TCP poses needed for the motion.
        tcp_pose_targets = []

        # Show this message on the screen.
        print("")
        # Show this message on the screen.
        print("=" * 70)
        # Show this message on the screen.
        print("GENERATING CAMERA NECK FOLLOW POSES")
        # Show this message on the screen.
        print("=" * 70)
        # Show this message on the screen.
        print("Camera position stays fixed.")
        # Show this message on the screen.
        print("Only the camera orientation changes.")
        # Show this message on the screen.
        print("Motion: left corner -> edge center -> right corner.")
        # Show this message on the screen.
        print("=" * 70)

        # Go through each target point the camera should look at.
        for index, look_point_base in enumerate(look_points_base, start=1):
            # Create a clear name for this target point.
            label = f"Neck_Follow_Point_{index:02d}"

            # Show this message on the screen.
            print("")
            # Show this message on the screen.
            print(label)
            # Show this message on the screen.
            print("Camera fixed position:")
            # Show this message on the screen.
            print(np.round(fixed_camera_position_base * 1000.0, 2), "mm")
            # Show this message on the screen.
            print("Looking at:")
            # Show this message on the screen.
            print(np.round(look_point_base * 1000.0, 2), "mm")

            # Build the camera pose that looks at the current point.
            camera_pose_base_look = (
                # Run this line as one small step in the program.
                self.camera_pose_builder.build_camera_look_at_pose(
                    # Add this value to the current list or function call.
                    camera_pose_base_center,
                    # Add this value to the current list or function call.
                    fixed_camera_position_base,
                    # Run this line as one small step in the program.
                    look_point_base
                )
            )

            # Convert the camera pose into the TCP pose the robot needs.
            tcp_pose_base_look = camera_pose_base_look @ camera_to_tcp

            # Check this condition before continuing.
            if not self.robot_controller.is_generated_pose_safe(
                # Add this value to the current list or function call.
                tcp_pose_base_look,
                # Add this value to the current list or function call.
                camera_pose_base_look,
                # Run this line as one small step in the program.
                label
            # Run this line as one small step in the program.
            ):
                # Skip this item and move to the next one.
                continue

            # Add this safe TCP pose to the movement list.
            tcp_pose_targets.append(tcp_pose_base_look)

        # Give this result back to the code that asked for it.
        return tcp_pose_targets

    # Create the helper that moves through all neck-follow poses.
    def _run_neck_follow_motion(self, tcp_pose_targets):
        # Show this message on the screen.
        print("")
        # Show this message on the screen.
        print("=" * 70)
        # Show this message on the screen.
        print("CAMERA NECK FOLLOW START")
        # Show this message on the screen.
        print("=" * 70)

        # Go through each robot target pose in order.
        for index, tcp_pose_base_target in enumerate(tcp_pose_targets, start=1):
            # Create a clear name for this target point.
            label = f"Neck_Follow_Point_{index:02d}"

            # Run this line as one small step in the program.
            self.robot_controller.move_to_pose(
                # Add this value to the current list or function call.
                tcp_pose_base_target,
                # Run this line as one small step in the program.
                label
            )

        # Show this message on the screen.
        print("")
        # Show this message on the screen.
        print("=" * 70)
        # Show this message on the screen.
        print("CAMERA NECK FOLLOW FINISHED")
        # Show this message on the screen.
        print("=" * 70)

    # Create the helper that tries to bring the robot back home.
    def _move_home_safely(self):
        # Try this block because it may fail safely.
        try:
            # Run this line as one small step in the program.
            self.robot_controller.move_to_joints(
                # Add this value to the current list or function call.
                self.config.HOME_JOINTS,
                # Run this line as one small step in the program.
                "Home_End"
            )
        # Handle an error without crashing this final safety step.
        except Exception as error:
            # Show this message on the screen.
            print("Could not move robot back to home position:", error)
