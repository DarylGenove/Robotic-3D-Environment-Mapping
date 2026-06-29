import sys

import numpy as np

sys.path.append("C:/RoboDK/Python")

from robodk.robomath import TxyzRxyz_2_Pose, Mat


class TransformUtils:
    @staticmethod
    def robodk_mat_to_numpy(mat):
        transform = np.eye(4, dtype=np.float64)

        for row in range(3):
            for col in range(3):
                transform[row, col] = mat[row, col]

            transform[row, 3] = mat[row, 3] / 1000.0

        return transform

    @staticmethod
    def numpy_to_robodk_mat(transform):
        return Mat([
            [
                transform[0, 0],
                transform[0, 1],
                transform[0, 2],
                transform[0, 3] * 1000.0,
            ],
            [
                transform[1, 0],
                transform[1, 1],
                transform[1, 2],
                transform[1, 3] * 1000.0,
            ],
            [
                transform[2, 0],
                transform[2, 1],
                transform[2, 2],
                transform[2, 3] * 1000.0,
            ],
            [0, 0, 0, 1],
        ])

    @staticmethod
    def xyzrxryrz_to_numpy(pose_values):
        pose = TxyzRxyz_2_Pose([
            pose_values[0],
            pose_values[1],
            pose_values[2],
            np.radians(pose_values[3]),
            np.radians(pose_values[4]),
            np.radians(pose_values[5]),
        ])

        return TransformUtils.robodk_mat_to_numpy(pose)

    @staticmethod
    def joints_to_list(joints_mat):
        try:
            return list(joints_mat.list())
        except Exception:
            try:
                return list(joints_mat)
            except Exception:
                return [
                    joints_mat[index]
                    for index in range(len(joints_mat))
                ]

    @staticmethod
    def normalize(vector):
        norm = np.linalg.norm(vector)

        if norm < 1e-9:
            raise Exception("Cannot normalize zero-length vector.")

        return vector / norm

    @staticmethod
    def transform_point(transform, point):
        point_h = np.array(
            [point[0], point[1], point[2], 1.0],
            dtype=np.float64
        )

        transformed = transform @ point_h

        return transformed[:3]

    @staticmethod
    def print_transform(name, transform):
        print(f"\n{name}:")
        print(np.round(transform, 6))
