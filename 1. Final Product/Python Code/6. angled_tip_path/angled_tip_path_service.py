from transform_utils import TransformUtils


class AngledTipPathService:
    def __init__(
        self,
        config,
        robot_controller,
        camera_calibration,
        seam_path_generator,
        angled_tcp_pose_builder,
        debug_target_service
    ):
        self.config = config
        self.robot_controller = robot_controller
        self.camera_calibration = camera_calibration
        self.seam_path_generator = seam_path_generator
        self.angled_tcp_pose_builder = angled_tcp_pose_builder
        self.debug_target_service = debug_target_service

    def run(self):
        tcp_to_camera = self.camera_calibration.get_tcp_to_camera_transform()

        TransformUtils.print_transform("T_tcp_camera", tcp_to_camera)

        try:
            self.robot_controller.move_to_joints(
                self.config.HOME_JOINTS,
                "Home_Start"
            )

            actual_center_joints = self.robot_controller.move_to_joints(
                self.config.CENTER_REFERENCE_JOINTS,
                "Center_Reference_View"
            )

            locked_j6_value = actual_center_joints[5]

            tcp_pose_base_center = self.robot_controller.solve_fk_to_numpy(
                actual_center_joints
            )

            camera_pose_base_center = tcp_pose_base_center @ tcp_to_camera

            TransformUtils.print_transform(
                "T_base_tcp_center",
                tcp_pose_base_center
            )
            TransformUtils.print_transform(
                "T_base_camera_center",
                camera_pose_base_center
            )

            print("")
            print("J6 reference value:", round(locked_j6_value, 2))

            seam_points_camera = (
                self.seam_path_generator.generate_seam_points_camera_frame()
            )

            seam_points_base = (
                self.seam_path_generator.transform_seam_points_to_base(
                    camera_pose_base_center,
                    seam_points_camera
                )
            )

            targets = self.angled_tcp_pose_builder.generate_angled_tcp_targets(
                camera_pose_base_center,
                seam_points_base
            )

            self.debug_target_service.create_debug_targets(targets)

            self._run_angled_tip_path(
                targets,
                actual_center_joints,
                locked_j6_value
            )

        except KeyboardInterrupt:
            print("")
            print("Movement interrupted by user.")

        finally:
            self._move_home_safely()

        print("Done.")

    def _run_angled_tip_path(
        self,
        targets,
        center_joints,
        locked_j6_value
    ):
        print("")
        print("=" * 70)
        print("ANGLED TIP PATH START")
        print("=" * 70)
        print("The tool now has an angle toward the seam.")
        print("The TCP is placed slightly before the seam using TIP_STANDOFF_M.")
        print("No welding machine or arc is triggered.")
        print("=" * 70)

        successful_moves = 0
        skipped_moves = 0
        failed_moves = 0

        seed_joints = center_joints

        for label, tcp_pose_base_target, _ in targets:
            if not self.robot_controller.is_pose_safe(
                tcp_pose_base_target,
                label
            ):
                skipped_moves += 1
                continue

            try:
                actual_joints = self.robot_controller.move_to_pose(
                    tcp_pose_base_target,
                    seed_joints,
                    locked_j6_value,
                    label
                )

                if self.config.LOCK_J6_WITH_SEED:
                    actual_joints[5] = locked_j6_value

                seed_joints = actual_joints

                successful_moves += 1

            except Exception as error:
                print("")
                print(f"WARNING: Could not move to {label}.")
                print("Move error:", error)
                failed_moves += 1
                continue

        print("")
        print("=" * 70)
        print("ANGLED TIP PATH FINISHED")
        print("=" * 70)
        print("Successful moves:", successful_moves)
        print("Skipped moves:", skipped_moves)
        print("Failed moves:", failed_moves)

    def _move_home_safely(self):
        try:
            self.robot_controller.move_to_joints(
                self.config.HOME_JOINTS,
                "Home_End"
            )
        except Exception as error:
            print("Could not move robot back to home position:", error)
