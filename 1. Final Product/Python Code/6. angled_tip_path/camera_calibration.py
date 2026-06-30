# Bring in the numpy toolbox so this file can use it.
import numpy as np

# Bring in TransformUtils from transform_utils so we can use it here.
from transform_utils import TransformUtils


# Create the CameraCalibration object that groups related actions together.
class CameraCalibration:
    # Start the   init   function.
    def __init__(self, config):
        # Save config so the program can use it later.
        self.config = config

    # Start the get tcp to camera transform function.
    def get_tcp_to_camera_transform(self):
        # Save tcp to mount so the program can use it later.
        tcp_to_mount = TransformUtils.xyzrxryrz_to_numpy(
            # This line helps the program do the next small step.
            self.config.TCP_TO_CAMERA_MOUNT
        # Close this group of values.
        )

        # Save mount to optical so the program can use it later.
        mount_to_optical = TransformUtils.xyzrxryrz_to_numpy(
            # This line helps the program do the next small step.
            self.config.CAMERA_MOUNT_TO_OPTICAL
        # Close this group of values.
        )

        # Send this result back to the place that called the function.
        return tcp_to_mount @ mount_to_optical

    # Start the get camera to tcp transform function.
    def get_camera_to_tcp_transform(self):
        # Send this result back to the place that called the function.
        return np.linalg.inv(
            # This line helps the program do the next small step.
            self.get_tcp_to_camera_transform()
        # Close this group of values.
        )
