import numpy as np

from transform_utils import TransformUtils


class AngledTcpPoseBuilder:
    def __init__(self, config):
        self.config = config

    def generate_angled_tcp_targets(
        self,
        camera_pose_base_center,
        seam_points_base
    ):
        if len(seam_points_base) < 2:
            raise Exception("Not enough seam points.")

        camera_position_base = camera_pose_base_center[:3, 3]
        reference_rotation = camera_pose_base_center[:3, :3]

        seam_direction_base = seam_points_base[-1] - seam_points_base[0]
        seam_direction_base = TransformUtils.normalize(seam_direction_base)

        targets = []

        print("")
        print("=" * 70)
        print("Generating angled TCP targets")
        print("=" * 70)
        print("The tool now points toward the seam.")
        print("The tip is closer because of TIP_STANDOFF_M.")

        for index, seam_point_base in enumerate(seam_points_base, start=1):
            label = f"Angled_Tip_Point_{index:02d}"

            tcp_pose_base = self.build_angled_tcp_pose(
                camera_position_base,
                seam_point_base,
                seam_direction_base,
                reference_rotation
            )

            targets.append(
                (
                    label,
                    tcp_pose_base,
                    seam_point_base
                )
            )

            self._print_target(
                label,
                seam_point_base,
                tcp_pose_base
            )

        return targets

    def build_angled_tcp_pose(
        self,
        camera_position_base,
        seam_point_base,
        seam_direction_base,
        reference_rotation
    ):
        approach_axis = TransformUtils.normalize(
            seam_point_base - camera_position_base
        )

        tool_x_axis = (
            seam_direction_base
            - np.dot(seam_direction_base, approach_axis) * approach_axis
        )

        if np.linalg.norm(tool_x_axis) < 1e-6:
            tool_x_axis = reference_rotation[:, 0]
        else:
            tool_x_axis = TransformUtils.normalize(tool_x_axis)

        tool_y_axis = np.cross(approach_axis, tool_x_axis)
        tool_y_axis = TransformUtils.normalize(tool_y_axis)

        tool_x_axis = np.cross(tool_y_axis, approach_axis)
        tool_x_axis = TransformUtils.normalize(tool_x_axis)

        tcp_position = (
            seam_point_base
            - approach_axis * self.config.TIP_STANDOFF_M
        )

        tcp_pose_base = np.eye(4, dtype=np.float64)
        tcp_pose_base[:3, 0] = tool_x_axis
        tcp_pose_base[:3, 1] = tool_y_axis
        tcp_pose_base[:3, 2] = approach_axis
        tcp_pose_base[:3, 3] = tcp_position

        return tcp_pose_base

    def _print_target(
        self,
        label,
        seam_point_base,
        tcp_pose_base
    ):
        print("")
        print(label)
        print("Seam point:")
        print(np.round(seam_point_base * 1000.0, 2), "mm")
        print("TCP point:")
        print(np.round(tcp_pose_base[:3, 3] * 1000.0, 2), "mm")
        print("Tool approach direction:")
        print(np.round(tcp_pose_base[:3, 2], 4))
