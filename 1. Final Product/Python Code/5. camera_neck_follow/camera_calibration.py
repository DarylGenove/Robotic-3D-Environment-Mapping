# Bring in NumPy so the code can do 3D math with numbers.
import numpy as np

# Bring in TransformUtils so this file can reuse 3D transform helpers.
from transform_utils import TransformUtils


# Create the CameraCalibration class so related code stays together.
class CameraCalibration:
    # Create the setup function that saves the things this object needs.
    def __init__(self, config):
        # Save a value in config.
        self.config = config

    # Create the function that finds where the camera is compared to the robot TCP.
    def get_tcp_to_camera_transform(self):
        # Convert the TCP-to-camera-mount values into a transform matrix.
        tcp_to_mount = TransformUtils.xyzrxryrz_to_numpy(
            # Run this line as one small step in the program.
            self.config.TCP_TO_CAMERA_MOUNT
        )

        # Convert the camera-mount-to-optical values into a transform matrix.
        mount_to_optical = TransformUtils.xyzrxryrz_to_numpy(
            # Run this line as one small step in the program.
            self.config.CAMERA_MOUNT_TO_OPTICAL
        )

        # Combine the two camera transforms into one final transform.
        return tcp_to_mount @ mount_to_optical

    # Create the function that finds where the robot TCP is compared to the camera.
    def get_camera_to_tcp_transform(self):
        # Return the same transform but reversed.
        return np.linalg.inv(self.get_tcp_to_camera_transform())
