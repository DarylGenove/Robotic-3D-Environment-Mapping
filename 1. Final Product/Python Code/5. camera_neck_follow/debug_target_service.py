import sys

import numpy as np

sys.path.append("C:/RoboDK/Python")

from robodk.robolink import ITEM_TYPE_TARGET

from transform_utils import TransformUtils


class DebugTargetService:
    def __init__(self, config, rdk):
        self.config = config
        self.rdk = rdk

    def create_debug_targets(
        self,
        look_points_base,
        camera_position_base,
        tcp_pose_targets
    ):
        if not self.config.CREATE_DEBUG_TARGETS:
            return

        self.create_point_marker(
            "NECK_CAMERA_FIXED_POSITION",
            camera_position_base
        )

        for index, look_point in enumerate(look_points_base, start=1):
            self.create_point_marker(
                f"NECK_LOOK_POINT_{index:02d}",
                look_point
            )

        for index, tcp_pose_base in enumerate(tcp_pose_targets, start=1):
            self.create_target_marker(
                f"NECK_TCP_TARGET_{index:02d}",
                tcp_pose_base
            )

    def create_point_marker(self, name, position_base):
        target_pose_base = np.eye(4, dtype=np.float64)
        target_pose_base[:3, 3] = position_base

        return self.create_target_marker(
            name,
            target_pose_base
        )

    def create_target_marker(self, name, target_pose_base):
        self.delete_existing_item(name, ITEM_TYPE_TARGET)

        target = self.rdk.AddTarget(name)
        target.setPose(TransformUtils.numpy_to_robodk_mat(target_pose_base))

        return target

    def delete_existing_item(self, name, item_type):
        item = self.rdk.Item(name, item_type)

        if item.Valid():
            item.Delete()
