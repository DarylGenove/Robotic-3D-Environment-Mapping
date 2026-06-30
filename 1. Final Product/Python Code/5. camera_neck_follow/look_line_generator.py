# Bring in NumPy so the code can do 3D math with numbers.
import numpy as np

# Bring in TransformUtils so this file can reuse 3D transform helpers.
from transform_utils import TransformUtils


# Create the LookLineGenerator class so related code stays together.
class LookLineGenerator:
    # Create the setup function that saves the things this object needs.
    def __init__(self, config):
        # Save a value in config.
        self.config = config

    # Create the function that makes look points from left to right in camera view.
    def generate_camera_frame_line_points(self):
        # Create the left point of the line in the camera view.
        left_corner = np.array(
            [
                # Add this value to the current list or function call.
                -self.config.LINE_HALF_WIDTH_M,
                # Add this value to the current list or function call.
                self.config.LINE_Y_M,
                # Add this value to the current list or function call.
                self.config.LINE_Z_M,
            ],
            # Run this line as one small step in the program.
            dtype=np.float64
        )

        # Create the middle point of the line in the camera view.
        edge_center = np.array(
            [
                # Add this value to the current list or function call.
                0.0,
                # Add this value to the current list or function call.
                self.config.LINE_Y_M,
                # Add this value to the current list or function call.
                self.config.LINE_Z_M,
            ],
            # Run this line as one small step in the program.
            dtype=np.float64
        )

        # Create the right point of the line in the camera view.
        right_corner = np.array(
            [
                # Add this value to the current list or function call.
                self.config.LINE_HALF_WIDTH_M,
                # Add this value to the current list or function call.
                self.config.LINE_Y_M,
                # Add this value to the current list or function call.
                self.config.LINE_Z_M,
            ],
            # Run this line as one small step in the program.
            dtype=np.float64
        )

        # Count how many points go from the left corner to the center.
        left_count = self.config.NUM_LOOK_POINTS // 2 + 1
        # Count how many points go from the center to the right corner.
        right_count = self.config.NUM_LOOK_POINTS - left_count + 1

        # Make evenly spaced points from the left corner to the center.
        left_to_center = np.linspace(
            # Add this value to the current list or function call.
            left_corner,
            # Add this value to the current list or function call.
            edge_center,
            # Run this line as one small step in the program.
            left_count
        )

        # Make evenly spaced points from the center to the right corner.
        center_to_right = np.linspace(
            # Add this value to the current list or function call.
            edge_center,
            # Add this value to the current list or function call.
            right_corner,
            # Run this line as one small step in the program.
            right_count
        # Run this line as one small step in the program.
        )[1:]

        # Join the left and right point lists into one line.
        points = np.vstack((left_to_center, center_to_right))

        # Run this line as one small step in the program.
        self._print_camera_frame_line(
            # Add this value to the current list or function call.
            left_corner,
            # Add this value to the current list or function call.
            edge_center,
            # Add this value to the current list or function call.
            right_corner,
            # Run this line as one small step in the program.
            points
        )

        # Give the generated line points back to the caller.
        return points

    # Create the function that changes camera points into robot-base points.
    def transform_look_points_to_base(
        # Add this value to the current list or function call.
        self,
        # Add this value to the current list or function call.
        camera_pose_base_center,
        # Run this line as one small step in the program.
        camera_frame_points
    # Run this line as one small step in the program.
    ):
        # Start an empty list for points in the robot-base frame.
        base_points = []

        # Go through each point made in the camera frame.
        for point in camera_frame_points:
            # Convert one camera-frame point into a robot-base point.
            base_point = TransformUtils.transform_point(
                # Add this value to the current list or function call.
                camera_pose_base_center,
                # Run this line as one small step in the program.
                point
            )

            # Add the converted point to the list.
            base_points.append(base_point)

        # Give the robot-base look points back to the caller.
        return base_points

    # Create the helper that prints the generated look line points.
    def _print_camera_frame_line(
        # Add this value to the current list or function call.
        self,
        # Add this value to the current list or function call.
        left_corner,
        # Add this value to the current list or function call.
        edge_center,
        # Add this value to the current list or function call.
        right_corner,
        # Run this line as one small step in the program.
        points
    # Run this line as one small step in the program.
    ):
        # Show this message on the screen.
        print("")
        # Show this message on the screen.
        print("=" * 70)
        # Show this message on the screen.
        print("Generated camera-frame look line")
        # Show this message on the screen.
        print("=" * 70)
        # Show this message on the screen.
        print("Left corner :", np.round(left_corner, 4))
        # Show this message on the screen.
        print("Edge center :", np.round(edge_center, 4))
        # Show this message on the screen.
        print("Right corner:", np.round(right_corner, 4))

        # Print each generated point with its number.
        for index, point in enumerate(points, start=1):
            # Show this message on the screen.
            print(f"Look point {index:02d}: {np.round(point, 4)} m")
