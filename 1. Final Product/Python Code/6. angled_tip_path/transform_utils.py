# Bring in the sys toolbox so this file can use it.
import sys

# Bring in the numpy toolbox so this file can use it.
import numpy as np

# Add the RoboDK Python folder so RoboDK tools can be imported.
sys.path.append("C:/RoboDK/Python")

# Bring in TxyzRxyz_2_Pose, Mat from robodk.robomath so we can use it here.
from robodk.robomath import TxyzRxyz_2_Pose, Mat


# Create the TransformUtils object that groups related actions together.
class TransformUtils:
    # Mark the next helper as a tool that does not need saved object data.
    @staticmethod
    def robodk_mat_to_numpy(mat):
        # Create a blank 3D transform that starts as no movement.
        transform = np.eye(4, dtype=np.float64)

        # Repeat this step for every item in the group.
        for row in range(3):
            # Repeat this step for every item in the group.
            for col in range(3):
                # Save transform[row, col] so the program can use it later.
                transform[row, col] = mat[row, col]

            # Save transform[row, 3] so the program can use it later.
            transform[row, 3] = mat[row, 3] / 1000.0

        # Send this result back to the place that called the function.
        return transform

    # Mark the next helper as a tool that does not need saved object data.
    @staticmethod
    def numpy_to_robodk_mat(transform):
        # Send this result back to the place that called the function.
        return Mat([
            # Start a multi-line list.
            [
                # This line helps the program do the next small step.
                transform[0, 0],
                # This line helps the program do the next small step.
                transform[0, 1],
                # This line helps the program do the next small step.
                transform[0, 2],
                # This line helps the program do the next small step.
                transform[0, 3] * 1000.0,
            # Close this group of values.
            ],
            # Start a multi-line list.
            [
                # This line helps the program do the next small step.
                transform[1, 0],
                # This line helps the program do the next small step.
                transform[1, 1],
                # This line helps the program do the next small step.
                transform[1, 2],
                # This line helps the program do the next small step.
                transform[1, 3] * 1000.0,
            # Close this group of values.
            ],
            # Start a multi-line list.
            [
                # This line helps the program do the next small step.
                transform[2, 0],
                # This line helps the program do the next small step.
                transform[2, 1],
                # This line helps the program do the next small step.
                transform[2, 2],
                # This line helps the program do the next small step.
                transform[2, 3] * 1000.0,
            # Close this group of values.
            ],
            # This line helps the program do the next small step.
            [0, 0, 0, 1],
        # Close this group of values.
        ])

    # Mark the next helper as a tool that does not need saved object data.
    @staticmethod
    def xyzrxryrz_to_numpy(pose_values):
        # Convert XYZ and rotation numbers into a RoboDK pose.
        pose = TxyzRxyz_2_Pose([
            # This line helps the program do the next small step.
            pose_values[0],
            # This line helps the program do the next small step.
            pose_values[1],
            # This line helps the program do the next small step.
            pose_values[2],
            # Change degrees into radians because math functions use radians.
            np.radians(pose_values[3]),
            # Change degrees into radians because math functions use radians.
            np.radians(pose_values[4]),
            # Change degrees into radians because math functions use radians.
            np.radians(pose_values[5]),
        # Close this group of values.
        ])

        # Send this result back to the place that called the function.
        return TransformUtils.robodk_mat_to_numpy(pose)

    # Mark the next helper as a tool that does not need saved object data.
    @staticmethod
    def joints_to_list(joints_mat):
        # Try this risky step safely.
        try:
            # Send this result back to the place that called the function.
            return list(joints_mat.list())
        # Handle the problem if the try step fails.
        except Exception:
            # Try this risky step safely.
            try:
                # Send this result back to the place that called the function.
                return list(joints_mat)
            # Handle the problem if the try step fails.
            except Exception:
                # Send this result back to the place that called the function.
                return [
                    # This line helps the program do the next small step.
                    joints_mat[index]
                    # Repeat this step for every item in the group.
                    for index in range(len(joints_mat))
                # Close this group of values.
                ]

    # Mark the next helper as a tool that does not need saved object data.
    @staticmethod
    def normalize(vector):
        # Measure the length of this 3D direction.
        norm = np.linalg.norm(vector)

        # Check if this condition is true.
        if norm < 1e-9:
            # Stop the program and show this problem message.
            raise Exception("Cannot normalize zero-length vector.")

        # Send this result back to the place that called the function.
        return vector / norm

    # Mark the next helper as a tool that does not need saved object data.
    @staticmethod
    def transform_point(transform, point):
        # Create a NumPy list of numbers for 3D math.
        point_h = np.array(
            # This line helps the program do the next small step.
            [point[0], point[1], point[2], 1.0],
            # Save dtype so the program can use it later.
            dtype=np.float64
        # Close this group of values.
        )

        # Combine two 3D transforms or apply one transform after another.
        transformed = transform @ point_h

        # Send this result back to the place that called the function.
        return transformed[:3]

    # Mark the next helper as a tool that does not need saved object data.
    @staticmethod
    def print_transform(name, transform):
        # Show a message on the screen.
        print(f"\n{name}:")
        # Show a message on the screen.
        print(np.round(transform, 6))
