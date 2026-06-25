import numpy as np

from transform_utils import TransformUtils


class SeamPathGenerator:
    def __init__(self, config):
        self.config = config

    def generate_seam_points_camera_frame(self):
        left_corner = np.array(
            [
                -self.config.SEAM_HALF_WIDTH_M,
                self.config.SEAM_Y_M + self.config.DRY_RUN_HEIGHT_OFFSET_M,
                self.config.SEAM_Z_M
            ],
            dtype=np.float64
        )

        center_edge = np.array(
            [
                0.0,
                self.config.SEAM_Y_M + self.config.DRY_RUN_HEIGHT_OFFSET_M,
                self.config.SEAM_Z_M
            ],
            dtype=np.float64
        )

        right_corner = np.array(
            [
                self.config.SEAM_HALF_WIDTH_M,
                self.config.SEAM_Y_M + self.config.DRY_RUN_HEIGHT_OFFSET_M,
                self.config.SEAM_Z_M
            ],
            dtype=np.float64
        )

        left_count = self.config.NUM_PATH_POINTS // 2 + 1
        right_count = self.config.NUM_PATH_POINTS - left_count + 1

        left_to_center = np.linspace(
            left_corner,
            center_edge,
            left_count
        )

        center_to_right = np.linspace(
            center_edge,
            right_corner,
            right_count
        )[1:]

        points = np.vstack((left_to_center, center_to_right))

        self._print_seam_points(
            left_corner,
            center_edge,
            right_corner,
            points
        )

        return points

    def transform_seam_points_to_base(
        self,
        camera_pose_base_center,
        seam_points_camera
    ):
        seam_points_base = []

        for point in seam_points_camera:
            seam_points_base.append(
                TransformUtils.transform_point(
                    camera_pose_base_center,
                    point
                )
            )

        return seam_points_base

    def _print_seam_points(
        self,
        left_corner,
        center_edge,
        right_corner,
        points
    ):
        print("")
        print("=" * 70)
        print("Generated angled seam points in camera frame")
        print("=" * 70)
        print("Left corner :", np.round(left_corner, 4))
        print("Center edge :", np.round(center_edge, 4))
        print("Right corner:", np.round(right_corner, 4))

        for index, point in enumerate(points, start=1):
            print(f"Seam point {index:02d}: {np.round(point, 4)} m")
