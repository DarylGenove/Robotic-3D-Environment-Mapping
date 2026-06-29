import numpy as np

from transform_utils import TransformUtils


class CameraPoseBuilder:
    def __init__(self, config):
        self.config = config

    def get_fixed_camera_position(self, camera_pose_base_center):
        camera_position = camera_pose_base_center[:3, 3].copy()

        camera_position += np.array([
            self.config.CAMERA_FIXED_X_OFFSET_M,
            self.config.CAMERA_FIXED_Y_OFFSET_M,
            self.config.CAMERA_FIXED_Z_OFFSET_M,
        ], dtype=np.float64)

        return camera_position

    def build_camera_look_at_pose(
        self,
        camera_pose_base_reference,
        camera_position_base,
        look_at_point_base
    ):
        direction = look_at_point_base - camera_position_base
        camera_forward = TransformUtils.normalize(direction)

        reference_rotation = camera_pose_base_reference[:3, :3]

        reference_up = reference_rotation[:, 1]
        reference_right = reference_rotation[:, 0]

        camera_right = np.cross(reference_up, camera_forward)

        if np.linalg.norm(camera_right) < 1e-6:
            camera_right = reference_right
        else:
            camera_right = TransformUtils.normalize(camera_right)

        camera_up = np.cross(camera_forward, camera_right)
        camera_up = TransformUtils.normalize(camera_up)

        camera_right = np.cross(camera_up, camera_forward)
        camera_right = TransformUtils.normalize(camera_right)

        camera_pose_base = np.eye(4, dtype=np.float64)

        camera_pose_base[:3, 0] = camera_right
        camera_pose_base[:3, 1] = camera_up
        camera_pose_base[:3, 2] = camera_forward
        camera_pose_base[:3, 3] = camera_position_base

        return camera_pose_base
