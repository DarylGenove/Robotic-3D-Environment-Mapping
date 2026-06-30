# Bring in NumPy so the code can do 3D math with numbers.
import numpy as np

# Bring in TransformUtils so this file can reuse 3D transform helpers.
from transform_utils import TransformUtils


# Create the CameraPoseBuilder class so related code stays together.
class CameraPoseBuilder:
    # Create the setup function that saves the things this object needs.
    def __init__(self, config):
        # Save a value in config.
        self.config = config

    # Create the function that chooses the camera position that should stay still.
    def get_fixed_camera_position(self, camera_pose_base_center):
        # Copy the current camera position from the pose matrix.
        camera_position = camera_pose_base_center[:3, 3].copy()

        # Move the fixed camera position by the configured offset.
        camera_position += np.array([
            # Add this value to the current list or function call.
            self.config.CAMERA_FIXED_X_OFFSET_M,
            # Add this value to the current list or function call.
            self.config.CAMERA_FIXED_Y_OFFSET_M,
            # Add this value to the current list or function call.
            self.config.CAMERA_FIXED_Z_OFFSET_M,
        # Run this line as one small step in the program.
        ], dtype=np.float64)

        # Give back the fixed camera position.
        return camera_position

    # Create the function that turns the camera so it looks at one point.
    def build_camera_look_at_pose(
        # Add this value to the current list or function call.
        self,
        # Add this value to the current list or function call.
        camera_pose_base_reference,
        # Add this value to the current list or function call.
        camera_position_base,
        # Run this line as one small step in the program.
        look_at_point_base
    # Run this line as one small step in the program.
    ):
        # Find the direction from the camera to the point it should look at.
        direction = look_at_point_base - camera_position_base
        # Turn that direction into the camera forward direction.
        camera_forward = TransformUtils.normalize(direction)

        # Take the rotation part from the reference camera pose.
        reference_rotation = camera_pose_base_reference[:3, :3]

        # Use the old camera up direction as a guide.
        reference_up = reference_rotation[:, 1]
        # Use the old camera right direction as a backup.
        reference_right = reference_rotation[:, 0]

        # Calculate the camera right direction using cross product math.
        camera_right = np.cross(reference_up, camera_forward)

        # Check if the right direction became too small to use.
        if np.linalg.norm(camera_right) < 1e-6:
            # Use the backup right direction if the new one is too small.
            camera_right = reference_right
        # Use this second path when the first condition was false.
        else:
            # Make the right direction have length one.
            camera_right = TransformUtils.normalize(camera_right)

        # Calculate the camera up direction from forward and right.
        camera_up = np.cross(camera_forward, camera_right)
        # Make the up direction have length one.
        camera_up = TransformUtils.normalize(camera_up)

        # Calculate the camera right direction using cross product math.
        camera_right = np.cross(camera_up, camera_forward)
        # Make the right direction have length one.
        camera_right = TransformUtils.normalize(camera_right)

        # Create an empty 4x4 pose matrix.
        camera_pose_base = np.eye(4, dtype=np.float64)

        # Put the camera right direction into the pose matrix.
        camera_pose_base[:3, 0] = camera_right
        # Put the camera up direction into the pose matrix.
        camera_pose_base[:3, 1] = camera_up
        # Put the camera forward direction into the pose matrix.
        camera_pose_base[:3, 2] = camera_forward
        # Put the camera position into the pose matrix.
        camera_pose_base[:3, 3] = camera_position_base

        # Give back the finished camera pose.
        return camera_pose_base
