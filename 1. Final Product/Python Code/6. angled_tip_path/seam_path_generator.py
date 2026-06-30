# Bring in the numpy toolbox so this file can use it.
import numpy as np

# Bring in TransformUtils from transform_utils so we can use it here.
from transform_utils import TransformUtils


# Create the SeamPathGenerator object that groups related actions together.
class SeamPathGenerator:
    # Start the   init   function.
    def __init__(self, config):
        # Save config so the program can use it later.
        self.config = config

    # Start the generate seam points camera frame function.
    def generate_seam_points_camera_frame(self):
        # Create a NumPy list of numbers for 3D math.
        left_corner = np.array(
            # Start a multi-line list.
            [
                # This line helps the program do the next small step.
                -self.config.SEAM_HALF_WIDTH_M,
                # This line helps the program do the next small step.
                self.config.SEAM_Y_M + self.config.DRY_RUN_HEIGHT_OFFSET_M,
                # This line helps the program do the next small step.
                self.config.SEAM_Z_M
            # Close this group of values.
            ],
            # Save dtype so the program can use it later.
            dtype=np.float64
        # Close this group of values.
        )

        # Create a NumPy list of numbers for 3D math.
        center_edge = np.array(
            # Start a multi-line list.
            [
                # This line helps the program do the next small step.
                0.0,
                # This line helps the program do the next small step.
                self.config.SEAM_Y_M + self.config.DRY_RUN_HEIGHT_OFFSET_M,
                # This line helps the program do the next small step.
                self.config.SEAM_Z_M
            # Close this group of values.
            ],
            # Save dtype so the program can use it later.
            dtype=np.float64
        # Close this group of values.
        )

        # Create a NumPy list of numbers for 3D math.
        right_corner = np.array(
            # Start a multi-line list.
            [
                # This line helps the program do the next small step.
                self.config.SEAM_HALF_WIDTH_M,
                # This line helps the program do the next small step.
                self.config.SEAM_Y_M + self.config.DRY_RUN_HEIGHT_OFFSET_M,
                # This line helps the program do the next small step.
                self.config.SEAM_Z_M
            # Close this group of values.
            ],
            # Save dtype so the program can use it later.
            dtype=np.float64
        # Close this group of values.
        )

        # Save left count so the program can use it later.
        left_count = self.config.NUM_PATH_POINTS // 2 + 1
        # Save right count so the program can use it later.
        right_count = self.config.NUM_PATH_POINTS - left_count + 1

        # Create evenly spaced points between two positions.
        left_to_center = np.linspace(
            # This line helps the program do the next small step.
            left_corner,
            # This line helps the program do the next small step.
            center_edge,
            # This line helps the program do the next small step.
            left_count
        # Close this group of values.
        )

        # Create evenly spaced points between two positions.
        center_to_right = np.linspace(
            # This line helps the program do the next small step.
            center_edge,
            # This line helps the program do the next small step.
            right_corner,
            # This line helps the program do the next small step.
            right_count
        # This line helps the program do the next small step.
        )[1:]

        # Stack point lists together into one bigger list.
        points = np.vstack((left_to_center, center_to_right))

        # Start a multi-line command.
        self._print_seam_points(
            # This line helps the program do the next small step.
            left_corner,
            # This line helps the program do the next small step.
            center_edge,
            # This line helps the program do the next small step.
            right_corner,
            # This line helps the program do the next small step.
            points
        # Close this group of values.
        )

        # Send this result back to the place that called the function.
        return points

    # Start the transform seam points to base function.
    def transform_seam_points_to_base(
        # This line helps the program do the next small step.
        self,
        # This line helps the program do the next small step.
        camera_pose_base_center,
        # This line helps the program do the next small step.
        seam_points_camera
    # This line helps the program do the next small step.
    ):
        # Save seam points base so the program can use it later.
        seam_points_base = []

        # Repeat this step for every item in the group.
        for point in seam_points_camera:
            # Start a multi-line command.
            seam_points_base.append(
                # Move this point from one coordinate system into another.
                TransformUtils.transform_point(
                    # This line helps the program do the next small step.
                    camera_pose_base_center,
                    # This line helps the program do the next small step.
                    point
                # Close this group of values.
                )
            # Close this group of values.
            )

        # Send this result back to the place that called the function.
        return seam_points_base

    # Start the  print seam points function.
    def _print_seam_points(
        # This line helps the program do the next small step.
        self,
        # This line helps the program do the next small step.
        left_corner,
        # This line helps the program do the next small step.
        center_edge,
        # This line helps the program do the next small step.
        right_corner,
        # This line helps the program do the next small step.
        points
    # This line helps the program do the next small step.
    ):
        # Show a message on the screen.
        print("")
        # Show a message on the screen.
        print("=" * 70)
        # Show a message on the screen.
        print("Generated angled seam points in camera frame")
        # Show a message on the screen.
        print("=" * 70)
        # Show a message on the screen.
        print("Left corner :", np.round(left_corner, 4))
        # Show a message on the screen.
        print("Center edge :", np.round(center_edge, 4))
        # Show a message on the screen.
        print("Right corner:", np.round(right_corner, 4))

        # Repeat this step for every item in the group.
        for index, point in enumerate(points, start=1):
            # Show a message on the screen.
            print(f"Seam point {index:02d}: {np.round(point, 4)} m")
