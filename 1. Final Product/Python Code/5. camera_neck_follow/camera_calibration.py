import numpy as np

from transform_utils import TransformUtils


class CameraCalibration:
    def __init__(self, config):
        self.config = config

    def get_tcp_to_camera_transform(self):
        tcp_to_mount = TransformUtils.xyzrxryrz_to_numpy(
            self.config.TCP_TO_CAMERA_MOUNT
        )

        mount_to_optical = TransformUtils.xyzrxryrz_to_numpy(
            self.config.CAMERA_MOUNT_TO_OPTICAL
        )

        return tcp_to_mount @ mount_to_optical

    def get_camera_to_tcp_transform(self):
        return np.linalg.inv(self.get_tcp_to_camera_transform())
