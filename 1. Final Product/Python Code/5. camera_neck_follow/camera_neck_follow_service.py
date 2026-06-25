import numpy as np

from transform_utils import TransformUtils


class CameraNeckFollowService:
    def __init__(
        self,
        config,
        robot_controller,
        camera_calibration,
        look_line_generator,
        camera_pose_builder,
        debug_target_service
    ):
        self.config = config
        self.robot_controller = robot_controller
        self.camera_calibration = camera_calibration
        self.look_line_generator = look_line_generator
        self.camera_pose_builder = camera_pose_builder
        self.debug_target_service = debug_target_service

    def run(self):
        tcp_to_camera = self.camera_calibration.get_tcp_to_camera_transform()
        camera_to_tcp = np.linalg.inv(tcp_to_camera)

        TransformUtils.print_transform("T_tcp_camera", tcp_to_camera)

        try:
            self.robot_controller.move_to_joints(
                self.config.HOME_JOINTS,
                "Home_Start"
            )

            center_actual_joints = self.robot_controller.move_to_joints(
                self.config.CENTER_REFERENCE_JOINTS,
                "Center_Reference_View"
            )

            tcp_pose_base_center = self.robot_controller.solve_fk_to_numpy(
                center_actual_joints
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

            camera_frame_look_points = (
                self.look_line_generator.generate_camera_frame_line_points()
            )

            look_points_base = (
                self.look_line_generator.transform_look_points_to_base(
                    camera_pose_base_center,
                    camera_frame_look_points
                )
            )

            fixed_camera_position_base = (
                self.camera_pose_builder.get_fixed_camera_position(
                    camera_pose_base_center
                )
            )

            tcp_pose_targets = self._generate_tcp_pose_targets(
                camera_pose_base_center,
                fixed_camera_position_base,
                look_points_base,
                camera_to_tcp
            )

            self.debug_target_service.create_debug_targets(
                look_points_base,
                fixed_camera_position_base,
                tcp_pose_targets
            )

            self._run_neck_follow_motion(tcp_pose_targets)

        except KeyboardInterrupt:
            print("")
            print("Movement interrupted by user.")

        finally:
            self._move_home_safely()

        print("Done.")

    def _generate_tcp_pose_targets(
        self,
        camera_pose_base_center,
        fixed_camera_position_base,
        look_points_base,
        camera_to_tcp
    ):
        tcp_pose_targets = []

        print("")
        print("=" * 70)
        print("GENERATING CAMERA NECK FOLLOW POSES")
        print("=" * 70)
        print("Camera position stays fixed.")
        print("Only the camera orientation changes.")
        print("Motion: left corner -> edge center -> right corner.")
        print("=" * 70)

        for index, look_point_base in enumerate(look_points_base, start=1):
            label = f"Neck_Follow_Point_{index:02d}"

            print("")
            print(label)
            print("Camera fixed position:")
            print(np.round(fixed_camera_position_base * 1000.0, 2), "mm")
            print("Looking at:")
            print(np.round(look_point_base * 1000.0, 2), "mm")

            camera_pose_base_look = (
                self.camera_pose_builder.build_camera_look_at_pose(
                    camera_pose_base_center,
                    fixed_camera_position_base,
                    look_point_base
                )
            )

            tcp_pose_base_look = camera_pose_base_look @ camera_to_tcp

            if not self.robot_controller.is_generated_pose_safe(
                tcp_pose_base_look,
                camera_pose_base_look,
                label
            ):
                continue

            tcp_pose_targets.append(tcp_pose_base_look)

        return tcp_pose_targets

    def _run_neck_follow_motion(self, tcp_pose_targets):
        print("")
        print("=" * 70)
        print("CAMERA NECK FOLLOW START")
        print("=" * 70)

        for index, tcp_pose_base_target in enumerate(tcp_pose_targets, start=1):
            label = f"Neck_Follow_Point_{index:02d}"

            self.robot_controller.move_to_pose(
                tcp_pose_base_target,
                label
            )

        print("")
        print("=" * 70)
        print("CAMERA NECK FOLLOW FINISHED")
        print("=" * 70)

    def _move_home_safely(self):
        try:
            self.robot_controller.move_to_joints(
                self.config.HOME_JOINTS,
                "Home_End"
            )
        except Exception as error:
            print("Could not move robot back to home position:", error)
