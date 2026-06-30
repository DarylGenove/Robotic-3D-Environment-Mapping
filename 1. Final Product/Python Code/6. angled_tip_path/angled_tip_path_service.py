# Bring in TransformUtils from transform_utils so we can use it here.
from transform_utils import TransformUtils


# Create the AngledTipPathService object that groups related actions together.
class AngledTipPathService:
    # Start the   init   function.
    def __init__(
        # This line helps the program do the next small step.
        self,
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
    # This line helps the program do the next small step.
    ):
        # Save config so the program can use it later.
        self.config = config
        # Save robot controller so the program can use it later.
        self.robot_controller = robot_controller
        # Save camera calibration so the program can use it later.
        self.camera_calibration = camera_calibration
        # Save seam path generator so the program can use it later.
        self.seam_path_generator = seam_path_generator
        # Save angled tcp pose builder so the program can use it later.
        self.angled_tcp_pose_builder = angled_tcp_pose_builder
        # Save debug target service so the program can use it later.
        self.debug_target_service = debug_target_service

    # Start the run function.
    def run(self):
        # Save tcp to camera so the program can use it later.
        tcp_to_camera = self.camera_calibration.get_tcp_to_camera_transform()

        # Print this 3D transform so we can check it.
        TransformUtils.print_transform("T_tcp_camera", tcp_to_camera)

        # Try this risky step safely.
        try:
            # Start a multi-line command.
            self.robot_controller.move_to_joints(
                # This line helps the program do the next small step.
                self.config.HOME_JOINTS,
                # This line helps the program do the next small step.
                "Home_Start"
            # Close this group of values.
            )

            # Save actual center joints so the program can use it later.
            actual_center_joints = self.robot_controller.move_to_joints(
                # This line helps the program do the next small step.
                self.config.CENTER_REFERENCE_JOINTS,
                # This line helps the program do the next small step.
                "Center_Reference_View"
            # Close this group of values.
            )

            # Save locked j6 value so the program can use it later.
            locked_j6_value = actual_center_joints[5]

            # Save tcp pose base center so the program can use it later.
            tcp_pose_base_center = self.robot_controller.solve_fk_to_numpy(
                # This line helps the program do the next small step.
                actual_center_joints
            # Close this group of values.
            )

            # Combine two 3D transforms or apply one transform after another.
            camera_pose_base_center = tcp_pose_base_center @ tcp_to_camera

            # Print this 3D transform so we can check it.
            TransformUtils.print_transform(
                # This line helps the program do the next small step.
                "T_base_tcp_center",
                # This line helps the program do the next small step.
                tcp_pose_base_center
            # Close this group of values.
            )
            # Print this 3D transform so we can check it.
            TransformUtils.print_transform(
                # This line helps the program do the next small step.
                "T_base_camera_center",
                # This line helps the program do the next small step.
                camera_pose_base_center
            # Close this group of values.
            )

            # Show a message on the screen.
            print("")
            # Show a message on the screen.
            print("J6 reference value:", round(locked_j6_value, 2))

            # Save seam points camera so the program can use it later.
            seam_points_camera = (
                # This line helps the program do the next small step.
                self.seam_path_generator.generate_seam_points_camera_frame()
            # Close this group of values.
            )

            # Save seam points base so the program can use it later.
            seam_points_base = (
                # Start a multi-line command.
                self.seam_path_generator.transform_seam_points_to_base(
                    # This line helps the program do the next small step.
                    camera_pose_base_center,
                    # This line helps the program do the next small step.
                    seam_points_camera
                # Close this group of values.
                )
            # Close this group of values.
            )

            # Save targets so the program can use it later.
            targets = self.angled_tcp_pose_builder.generate_angled_tcp_targets(
                # This line helps the program do the next small step.
                camera_pose_base_center,
                # This line helps the program do the next small step.
                seam_points_base
            # Close this group of values.
            )

            # This line helps the program do the next small step.
            self.debug_target_service.create_debug_targets(targets)

            # Start a multi-line command.
            self._run_angled_tip_path(
                # This line helps the program do the next small step.
                targets,
                # This line helps the program do the next small step.
                actual_center_joints,
                # This line helps the program do the next small step.
                locked_j6_value
            # Close this group of values.
            )

        # Handle the problem if the try step fails.
        except KeyboardInterrupt:
            # Show a message on the screen.
            print("")
            # Show a message on the screen.
            print("Movement interrupted by user.")

        # Always do this cleanup step at the end.
        finally:
            # This line helps the program do the next small step.
            self._move_home_safely()

        # Show a message on the screen.
        print("Done.")

    # Start the  run angled tip path function.
    def _run_angled_tip_path(
        # This line helps the program do the next small step.
        self,
        # This line helps the program do the next small step.
        targets,
        # This line helps the program do the next small step.
        center_joints,
        # This line helps the program do the next small step.
        locked_j6_value
    # This line helps the program do the next small step.
    ):
        # Show a message on the screen.
        print("")
        # Show a message on the screen.
        print("=" * 70)
        # Show a message on the screen.
        print("ANGLED TIP PATH START")
        # Show a message on the screen.
        print("=" * 70)
        # Show a message on the screen.
        print("The tool now has an angle toward the seam.")
        # Show a message on the screen.
        print("The TCP is placed slightly before the seam using TIP_STANDOFF_M.")
        # Show a message on the screen.
        print("No welding machine or arc is triggered.")
        # Show a message on the screen.
        print("=" * 70)

        # Save successful moves so the program can use it later.
        successful_moves = 0
        # Save skipped moves so the program can use it later.
        skipped_moves = 0
        # Save failed moves so the program can use it later.
        failed_moves = 0

        # Save seed joints so the program can use it later.
        seed_joints = center_joints

        # Repeat this step for every item in the group.
        for label, tcp_pose_base_target, _ in targets:
            # Check if this condition is true.
            if not self.robot_controller.is_pose_safe(
                # This line helps the program do the next small step.
                tcp_pose_base_target,
                # This line helps the program do the next small step.
                label
            # This line helps the program do the next small step.
            ):
                # Save skipped moves + so the program can use it later.
                skipped_moves += 1
                # Skip the rest of this loop and go to the next item.
                continue

            # Try this risky step safely.
            try:
                # Save actual joints so the program can use it later.
                actual_joints = self.robot_controller.move_to_pose(
                    # This line helps the program do the next small step.
                    tcp_pose_base_target,
                    # This line helps the program do the next small step.
                    seed_joints,
                    # This line helps the program do the next small step.
                    locked_j6_value,
                    # This line helps the program do the next small step.
                    label
                # Close this group of values.
                )

                # Check if this condition is true.
                if self.config.LOCK_J6_WITH_SEED:
                    # Save actual joints[5] so the program can use it later.
                    actual_joints[5] = locked_j6_value

                # Save seed joints so the program can use it later.
                seed_joints = actual_joints

                # Save successful moves + so the program can use it later.
                successful_moves += 1

            # Handle the problem if the try step fails.
            except Exception as error:
                # Show a message on the screen.
                print("")
                # Show a message on the screen.
                print(f"WARNING: Could not move to {label}.")
                # Show a message on the screen.
                print("Move error:", error)
                # Save failed moves + so the program can use it later.
                failed_moves += 1
                # Skip the rest of this loop and go to the next item.
                continue

        # Show a message on the screen.
        print("")
        # Show a message on the screen.
        print("=" * 70)
        # Show a message on the screen.
        print("ANGLED TIP PATH FINISHED")
        # Show a message on the screen.
        print("=" * 70)
        # Show a message on the screen.
        print("Successful moves:", successful_moves)
        # Show a message on the screen.
        print("Skipped moves:", skipped_moves)
        # Show a message on the screen.
        print("Failed moves:", failed_moves)

    # Start the  move home safely function.
    def _move_home_safely(self):
        # Try this risky step safely.
        try:
            # Start a multi-line command.
            self.robot_controller.move_to_joints(
                # This line helps the program do the next small step.
                self.config.HOME_JOINTS,
                # This line helps the program do the next small step.
                "Home_End"
            # Close this group of values.
            )
        # Handle the problem if the try step fails.
        except Exception as error:
            # Show a message on the screen.
            print("Could not move robot back to home position:", error)
