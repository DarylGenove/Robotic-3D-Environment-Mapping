# Bring in sys so Python can change where it searches for files.
import sys

# Bring in NumPy so the code can do 3D math with numbers.
import numpy as np

# Add this folder so Python can import the needed RoboDK or project files.
sys.path.append("C:/RoboDK/Python")

# Bring in RoboDK math tools for robot pose matrices.
from robodk.robomath import TxyzRxyz_2_Pose, Mat


# Create the TransformUtils class so related code stays together.
class TransformUtils:
    # Mark the next function as a special static helper.
    @staticmethod
    # Create the helper that converts a RoboDK matrix into a NumPy matrix.
    def robodk_mat_to_numpy(mat):
        # Create a 4x4 identity matrix for a 3D transform.
        transform = np.eye(4, dtype=np.float64)

        # Go through each row of the 3D matrix.
        for row in range(3):
            # Go through each column of the rotation part.
            for col in range(3):
                # Copy one rotation value from RoboDK into NumPy.
                transform[row, col] = mat[row, col]

            # Copy one position value and convert millimeters to meters.
            transform[row, 3] = mat[row, 3] / 1000.0

        # Give back the completed transform matrix.
        return transform

    # Mark the next function as a special static helper.
    @staticmethod
    # Create the helper that converts a NumPy matrix into a RoboDK matrix.
    def numpy_to_robodk_mat(transform):
        # Create and return a RoboDK matrix from the NumPy values.
        return Mat([
            [
                # Add this value to the current list or function call.
                transform[0, 0],
                # Add this value to the current list or function call.
                transform[0, 1],
                # Add this value to the current list or function call.
                transform[0, 2],
                # Add this value to the current list or function call.
                transform[0, 3] * 1000.0,
            ],
            [
                # Add this value to the current list or function call.
                transform[1, 0],
                # Add this value to the current list or function call.
                transform[1, 1],
                # Add this value to the current list or function call.
                transform[1, 2],
                # Add this value to the current list or function call.
                transform[1, 3] * 1000.0,
            ],
            [
                # Add this value to the current list or function call.
                transform[2, 0],
                # Add this value to the current list or function call.
                transform[2, 1],
                # Add this value to the current list or function call.
                transform[2, 2],
                # Add this value to the current list or function call.
                transform[2, 3] * 1000.0,
            ],
            # Add this value to the current list or function call.
            [0, 0, 0, 1],
        # Run this line as one small step in the program.
        ])

    # Mark the next function as a special static helper.
    @staticmethod
    # Create the helper that converts XYZ and rotation values into a matrix.
    def xyzrxryrz_to_numpy(pose_values):
        # Create a RoboDK pose from XYZ position and rotation values.
        pose = TxyzRxyz_2_Pose([
            # Add this value to the current list or function call.
            pose_values[0],
            # Add this value to the current list or function call.
            pose_values[1],
            # Add this value to the current list or function call.
            pose_values[2],
            # Add this value to the current list or function call.
            np.radians(pose_values[3]),
            # Add this value to the current list or function call.
            np.radians(pose_values[4]),
            # Add this value to the current list or function call.
            np.radians(pose_values[5]),
        # Run this line as one small step in the program.
        ])

        # Give back the converted robot pose as a NumPy matrix.
        return TransformUtils.robodk_mat_to_numpy(pose)

    # Mark the next function as a special static helper.
    @staticmethod
    # Create the helper that turns robot joints into a normal Python list.
    def joints_to_list(joints_mat):
        # Try this block because it may fail safely.
        try:
            # Give back the robot joints as a normal list.
            return list(joints_mat.list())
        # Handle a problem and try the backup option.
        except Exception:
            # Try this block because it may fail safely.
            try:
                # Give back the robot joints as a normal list.
                return list(joints_mat)
            # Handle a problem and try the backup option.
            except Exception:
                # Give this result back to the code that asked for it.
                return [
                    # Run this line as one small step in the program.
                    joints_mat[index]
                    # Repeat this block for each item in the group.
                    for index in range(len(joints_mat))
                ]

    # Mark the next function as a special static helper.
    @staticmethod
    # Create the helper that turns a vector into a length-one direction.
    def normalize(vector):
        # Calculate the length of the vector.
        norm = np.linalg.norm(vector)

        # Check if the vector is too small to become a direction.
        if norm < 1e-9:
            # Stop the program because something important is wrong.
            raise Exception("Cannot normalize zero-length vector.")

        # Give back the same direction with length one.
        return vector / norm

    # Mark the next function as a special static helper.
    @staticmethod
    # Create the helper that moves one 3D point using a transform matrix.
    def transform_point(transform, point):
        # Turn the 3D point into a 4-number point so a matrix can move it.
        point_h = np.array(
            # Add this value to the current list or function call.
            [point[0], point[1], point[2], 1.0],
            # Run this line as one small step in the program.
            dtype=np.float64
        )

        # Move the point using the transform matrix.
        transformed = transform @ point_h

        # Give back the completed transform matrix.
        return transformed[:3]

    # Mark the next function as a special static helper.
    @staticmethod
    # Create the helper that prints a transform matrix neatly.
    def print_transform(name, transform):
        # Show this message on the screen.
        print(f"\n{name}:")
        # Show this message on the screen.
        print(np.round(transform, 6))
