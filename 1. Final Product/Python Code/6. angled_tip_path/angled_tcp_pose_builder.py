# Bring in the numpy toolbox so this file can use it.
import numpy as np

# Bring in TransformUtils from transform_utils so we can use it here.
from transform_utils import TransformUtils


# Create the AngledTcpPoseBuilder object that groups related actions together.
class AngledTcpPoseBuilder:
    # Start the   init   function.
    def __init__(self, config):
        # Save config so the program can use it later.
        self.config = config

    # Start the generate angled tcp targets function.
    def generate_angled_tcp_targets(
        # This line helps the program do the next small step.
        self,
        # This line helps the program do the next small step.
        camera_pose_base_center,
        # This line helps the program do the next small step.
        seam_points_base
    # This line helps the program do the next small step.
    ):
        # Check if this condition is true.
        if len(seam_points_base) < 2:
            # Stop the program and show this problem message.
            raise Exception("Not enough seam points.")

        # Save camera position base so the program can use it later.
        camera_position_base = camera_pose_base_center[:3, 3]
        # Save reference rotation so the program can use it later.
        reference_rotation = camera_pose_base_center[:3, :3]

        # Save seam direction base so the program can use it later.
        seam_direction_base = seam_points_base[-1] - seam_points_base[0]
        # Make this direction length equal to 1 so it is only a direction.
        seam_direction_base = TransformUtils.normalize(seam_direction_base)

        # Save targets so the program can use it later.
        targets = []

        # Show a message on the screen.
        print("")
        # Show a message on the screen.
        print("=" * 70)
        # Show a message on the screen.
        print("Generating angled TCP targets")
        # Show a message on the screen.
        print("=" * 70)
        # Show a message on the screen.
        print("The tool now points toward the seam.")
        # Show a message on the screen.
        print("The tip is closer because of TIP_STANDOFF_M.")

        # Repeat this step for every item in the group.
        for index, seam_point_base in enumerate(seam_points_base, start=1):
            # Save label so the program can use it later.
            label = f"Angled_Tip_Point_{index:02d}"

            # Save tcp pose base so the program can use it later.
            tcp_pose_base = self.build_angled_tcp_pose(
                # This line helps the program do the next small step.
                camera_position_base,
                # This line helps the program do the next small step.
                seam_point_base,
                # This line helps the program do the next small step.
                seam_direction_base,
                # This line helps the program do the next small step.
                reference_rotation
            # Close this group of values.
            )

            # Start a multi-line command.
            targets.append(
                # Start a multi-line command.
                (
                    # This line helps the program do the next small step.
                    label,
                    # This line helps the program do the next small step.
                    tcp_pose_base,
                    # This line helps the program do the next small step.
                    seam_point_base
                # Close this group of values.
                )
            # Close this group of values.
            )

            # Start a multi-line command.
            self._print_target(
                # This line helps the program do the next small step.
                label,
                # This line helps the program do the next small step.
                seam_point_base,
                # This line helps the program do the next small step.
                tcp_pose_base
            # Close this group of values.
            )

        # Send this result back to the place that called the function.
        return targets

    # Start the build angled tcp pose function.
    def build_angled_tcp_pose(
        # This line helps the program do the next small step.
        self,
        # This line helps the program do the next small step.
        camera_position_base,
        # This line helps the program do the next small step.
        seam_point_base,
        # This line helps the program do the next small step.
        seam_direction_base,
        # This line helps the program do the next small step.
        reference_rotation
    # This line helps the program do the next small step.
    ):
        # Make this direction length equal to 1 so it is only a direction.
        approach_axis = TransformUtils.normalize(
            # This line helps the program do the next small step.
            seam_point_base - camera_position_base
        # Close this group of values.
        )

        # Save tool x axis so the program can use it later.
        tool_x_axis = (
            # This line helps the program do the next small step.
            seam_direction_base
            # Measure how much two directions point the same way.
            - np.dot(seam_direction_base, approach_axis) * approach_axis
        # Close this group of values.
        )

        # Check if this condition is true.
        if np.linalg.norm(tool_x_axis) < 1e-6:
            # Save tool x axis so the program can use it later.
            tool_x_axis = reference_rotation[:, 0]
        # Use this backup path when the earlier condition was false.
        else:
            # Make this direction length equal to 1 so it is only a direction.
            tool_x_axis = TransformUtils.normalize(tool_x_axis)

        # Build a new direction that is sideways to two other directions.
        tool_y_axis = np.cross(approach_axis, tool_x_axis)
        # Make this direction length equal to 1 so it is only a direction.
        tool_y_axis = TransformUtils.normalize(tool_y_axis)

        # Build a new direction that is sideways to two other directions.
        tool_x_axis = np.cross(tool_y_axis, approach_axis)
        # Make this direction length equal to 1 so it is only a direction.
        tool_x_axis = TransformUtils.normalize(tool_x_axis)

        # Save tcp position so the program can use it later.
        tcp_position = (
            # This line helps the program do the next small step.
            seam_point_base
            # This line helps the program do the next small step.
            - approach_axis * self.config.TIP_STANDOFF_M
        # Close this group of values.
        )

        # Create a blank 3D transform that starts as no movement.
        tcp_pose_base = np.eye(4, dtype=np.float64)
        # Save tcp pose base[:3, 0] so the program can use it later.
        tcp_pose_base[:3, 0] = tool_x_axis
        # Save tcp pose base[:3, 1] so the program can use it later.
        tcp_pose_base[:3, 1] = tool_y_axis
        # Save tcp pose base[:3, 2] so the program can use it later.
        tcp_pose_base[:3, 2] = approach_axis
        # Save tcp pose base[:3, 3] so the program can use it later.
        tcp_pose_base[:3, 3] = tcp_position

        # Send this result back to the place that called the function.
        return tcp_pose_base

    # Start the  print target function.
    def _print_target(
        # This line helps the program do the next small step.
        self,
        # This line helps the program do the next small step.
        label,
        # This line helps the program do the next small step.
        seam_point_base,
        # This line helps the program do the next small step.
        tcp_pose_base
    # This line helps the program do the next small step.
    ):
        # Show a message on the screen.
        print("")
        # Show a message on the screen.
        print(label)
        # Show a message on the screen.
        print("Seam point:")
        # Show a message on the screen.
        print(np.round(seam_point_base * 1000.0, 2), "mm")
        # Show a message on the screen.
        print("TCP point:")
        # Show a message on the screen.
        print(np.round(tcp_pose_base[:3, 3] * 1000.0, 2), "mm")
        # Show a message on the screen.
        print("Tool approach direction:")
        # Show a message on the screen.
        print(np.round(tcp_pose_base[:3, 2], 4))
