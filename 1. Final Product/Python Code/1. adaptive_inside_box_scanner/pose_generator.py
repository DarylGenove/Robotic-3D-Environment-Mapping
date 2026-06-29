from transform_utils import clamp, make_local_offset_transform


class AdaptivePoseGenerator:
    def __init__(self, config):
        self.config = config

    def generate_scan_offsets(self, adaptive_bounds):
        extent_x = adaptive_bounds["extent_x"]
        extent_y = adaptive_bounds["extent_y"]

        center_x = adaptive_bounds["center_x"]
        center_y = adaptive_bounds["center_y"]
        center_z = adaptive_bounds["center_z"]

        side_offset = clamp(
            extent_x * 0.35,
            self.config.MIN_SIDE_OFFSET_M,
            self.config.MAX_SIDE_OFFSET_M,
        )

        vertical_offset = clamp(
            extent_y * 0.35,
            self.config.MIN_VERTICAL_OFFSET_M,
            self.config.MAX_VERTICAL_OFFSET_M,
        )

        forward_offset = clamp(
            center_z * 0.12,
            self.config.MIN_FORWARD_OFFSET_M,
            self.config.MAX_FORWARD_OFFSET_M,
        )

        print("")
        print("Adaptive scan movement offsets:")
        print(f"Side offset: {side_offset:.4f} m")
        print(f"Vertical offset: {vertical_offset:.4f} m")
        print(f"Forward offset: {forward_offset:.4f} m")

        return [
            ("Reference_Center", 0.00, 0.00, 0.00),
            ("Left_Inside_Area", center_x - side_offset, center_y, 0.00),
            ("Right_Inside_Area", center_x + side_offset, center_y, 0.00),
            ("Upper_Inside_Area", center_x, center_y - vertical_offset, 0.00),
            ("Lower_Inside_Area", center_x, center_y + vertical_offset, 0.00),
            ("Upper_Left_Inside_Area", center_x - side_offset, center_y - vertical_offset, 0.00),
            ("Upper_Right_Inside_Area", center_x + side_offset, center_y - vertical_offset, 0.00),
            ("Lower_Left_Inside_Area", center_x - side_offset, center_y + vertical_offset, 0.00),
            ("Lower_Right_Inside_Area", center_x + side_offset, center_y + vertical_offset, 0.00),
            ("Closer_Center", center_x, center_y, forward_offset),
            ("Closer_Left", center_x - side_offset * 0.70, center_y, forward_offset),
            ("Closer_Right", center_x + side_offset * 0.70, center_y, forward_offset),
            ("Closer_Upper", center_x, center_y - vertical_offset * 0.70, forward_offset),
            ("Closer_Lower", center_x, center_y + vertical_offset * 0.70, forward_offset),
        ]

    def generate_scan_camera_poses_from_center(self, T_base_camera_center, adaptive_bounds):
        generated_poses = []
        adaptive_offsets = self.generate_scan_offsets(adaptive_bounds)

        print("\nGenerating adaptive scan poses from center reference...")
        print("Center camera position in robot base frame:")
        print(f"X: {T_base_camera_center[0, 3] * 1000.0:.1f} mm")
        print(f"Y: {T_base_camera_center[1, 3] * 1000.0:.1f} mm")
        print(f"Z: {T_base_camera_center[2, 3] * 1000.0:.1f} mm")

        for label, offset_x, offset_y, offset_z in adaptive_offsets:
            T_camera_offset = make_local_offset_transform(offset_x, offset_y, offset_z)
            T_base_camera_target = T_base_camera_center @ T_camera_offset

            print("")
            print(f"Generated camera pose: {label}")
            print(f"Local offset X: {offset_x * 1000.0:.1f} mm")
            print(f"Local offset Y: {offset_y * 1000.0:.1f} mm")
            print(f"Local offset Z: {offset_z * 1000.0:.1f} mm")
            print("Generated camera position in robot base frame:")
            print(f"X: {T_base_camera_target[0, 3] * 1000.0:.1f} mm")
            print(f"Y: {T_base_camera_target[1, 3] * 1000.0:.1f} mm")
            print(f"Z: {T_base_camera_target[2, 3] * 1000.0:.1f} mm")

            generated_poses.append((label, T_base_camera_target))

        return generated_poses
