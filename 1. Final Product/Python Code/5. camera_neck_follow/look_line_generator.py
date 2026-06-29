import numpy as np

from transform_utils import TransformUtils


class LookLineGenerator:
    def __init__(self, config):
        self.config = config

    def generate_camera_frame_line_points(self):
        left_corner = np.array(
            [
                -self.config.LINE_HALF_WIDTH_M,
                self.config.LINE_Y_M,
                self.config.LINE_Z_M,
            ],
            dtype=np.float64
        )

        edge_center = np.array(
            [
                0.0,
                self.config.LINE_Y_M,
                self.config.LINE_Z_M,
            ],
            dtype=np.float64
        )

        right_corner = np.array(
            [
                self.config.LINE_HALF_WIDTH_M,
                self.config.LINE_Y_M,
                self.config.LINE_Z_M,
            ],
            dtype=np.float64
        )

        left_count = self.config.NUM_LOOK_POINTS // 2 + 1
        right_count = self.config.NUM_LOOK_POINTS - left_count + 1

        left_to_center = np.linspace(
            left_corner,
            edge_center,
            left_count
        )

        center_to_right = np.linspace(
            edge_center,
            right_corner,
            right_count
        )[1:]

        points = np.vstack((left_to_center, center_to_right))

        self._print_camera_frame_line(
            left_corner,
            edge_center,
            right_corner,
            points
        )

        return points

    def transform_look_points_to_base(
        self,
        camera_pose_base_center,
        camera_frame_points
    ):
        base_points = []

        for point in camera_frame_points:
            base_point = TransformUtils.transform_point(
                camera_pose_base_center,
                point
            )

            base_points.append(base_point)

        return base_points

    def _print_camera_frame_line(
        self,
        left_corner,
        edge_center,
        right_corner,
        points
    ):
        print("")
        print("=" * 70)
        print("Generated camera-frame look line")
        print("=" * 70)
        print("Left corner :", np.round(left_corner, 4))
        print("Edge center :", np.round(edge_center, 4))
        print("Right corner:", np.round(right_corner, 4))

        for index, point in enumerate(points, start=1):
            print(f"Look point {index:02d}: {np.round(point, 4)} m")
