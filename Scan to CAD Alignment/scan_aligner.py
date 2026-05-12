import copy
import numpy as np
import open3d as o3d


class ScanAligner:
    """
    Handles floor leveling, wall yaw alignment, CAD center alignment, and ICP refinement.
    """

    def __init__(self, config, plane_detector):
        self.config = config
        self.plane_detector = plane_detector

    def rotation_matrix_from_vectors(self, vec_from, vec_to):
        a = vec_from / np.linalg.norm(vec_from)
        b = vec_to / np.linalg.norm(vec_to)

        cross = np.cross(a, b)
        dot = np.clip(np.dot(a, b), -1.0, 1.0)

        if np.isclose(dot, 1.0):
            return np.eye(3)

        if np.isclose(dot, -1.0):
            axis = np.array([1.0, 0.0, 0.0])

            if abs(a[0]) > 0.9:
                axis = np.array([0.0, 1.0, 0.0])

            axis = axis - a * np.dot(axis, a)
            axis = axis / np.linalg.norm(axis)

            skew_matrix = np.array([
                [0.0, -axis[2], axis[1]],
                [axis[2], 0.0, -axis[0]],
                [-axis[1], axis[0], 0.0],
            ])

            return np.eye(3) + 2.0 * (skew_matrix @ skew_matrix)

        sine_value = np.linalg.norm(cross)

        skew_matrix = np.array([
            [0.0, -cross[2], cross[1]],
            [cross[2], 0.0, -cross[0]],
            [-cross[1], cross[0], 0.0],
        ])

        return np.eye(3) + skew_matrix + (
            skew_matrix @ skew_matrix
        ) * ((1.0 - dot) / (sine_value ** 2))

    def level_scan_to_floor(self, scan_down, floor):
        floor_normal = floor["normal"].copy()

        if floor_normal[2] < 0:
            floor_normal = -floor_normal

        rotation_matrix = self.rotation_matrix_from_vectors(
            floor_normal,
            np.array([0.0, 0.0, 1.0])
        )

        scan_rotated = copy.deepcopy(scan_down)
        scan_rotated.rotate(rotation_matrix, center=(0.0, 0.0, 0.0))

        rotated_floor_centroid = rotation_matrix @ floor["centroid"]

        scan_rotated.translate((0.0, 0.0, -rotated_floor_centroid[2]))

        transformation = np.eye(4)
        transformation[:3, :3] = rotation_matrix
        transformation[:3, 3] = [0.0, 0.0, -rotated_floor_centroid[2]]

        return scan_rotated, transformation

    def choose_primary_wall(self, walls_after_level):
        best_wall = None
        best_score = -1.0

        for wall in walls_after_level:
            normal = wall["normal"].copy()
            normal[2] = 0.0

            norm = np.linalg.norm(normal)

            if norm < 1e-6:
                continue

            normal = normal / norm
            score = abs(normal[0]) + abs(normal[1])

            if score > best_score:
                best_score = score
                best_wall = wall

        if best_wall is None:
            raise Exception("Could not choose a primary wall.")

        return best_wall

    def yaw_align_scan_to_wall(self, scan_leveled, wall):
        normal = wall["normal"].copy()
        normal[2] = 0.0
        normal = normal / np.linalg.norm(normal)

        candidates = [
            np.array([1.0, 0.0, 0.0]),
            np.array([-1.0, 0.0, 0.0]),
            np.array([0.0, 1.0, 0.0]),
            np.array([0.0, -1.0, 0.0]),
        ]

        best_target = None
        best_dot = -np.inf

        for target in candidates:
            dot_value = np.dot(normal, target)

            if dot_value > best_dot:
                best_dot = dot_value
                best_target = target

        angle_from = np.arctan2(normal[1], normal[0])
        angle_to = np.arctan2(best_target[1], best_target[0])

        yaw = angle_to - angle_from

        cosine_yaw = np.cos(yaw)
        sine_yaw = np.sin(yaw)

        rotation_z = np.array([
            [cosine_yaw, -sine_yaw, 0.0],
            [sine_yaw, cosine_yaw, 0.0],
            [0.0, 0.0, 1.0]
        ])

        scan_yaw = copy.deepcopy(scan_leveled)
        scan_yaw.rotate(rotation_z, center=(0.0, 0.0, 0.0))

        transformation = np.eye(4)
        transformation[:3, :3] = rotation_z

        return scan_yaw, transformation, np.degrees(yaw)

    def structure_scan(self, scan_down):
        print("Detecting planes in raw scan...")

        planes_raw = self.plane_detector.detect_planes(scan_down)
        floor_raw, walls_raw = self.plane_detector.classify_floor_and_walls(planes_raw)

        print("Raw floor normal:", np.round(floor_raw["normal"], 4))
        print("Raw floor centroid:", np.round(floor_raw["centroid"], 4))
        print("Walls detected:", len(walls_raw))

        print("Leveling scan to floor...")

        scan_level, floor_transform = self.level_scan_to_floor(scan_down, floor_raw)

        planes_level = self.plane_detector.detect_planes(scan_level)
        floor_level, walls_level = self.plane_detector.classify_floor_and_walls(planes_level)

        primary_wall = self.choose_primary_wall(walls_level)

        print("Leveled floor normal:", np.round(floor_level["normal"], 4))
        print("Primary wall normal before yaw alignment:", np.round(primary_wall["normal"], 4))

        print("Yaw-aligning scan to primary wall...")

        scan_structured, yaw_transform, yaw_degrees = self.yaw_align_scan_to_wall(
            scan_level,
            primary_wall
        )

        print(f"Applied yaw rotation: {yaw_degrees:.2f} deg")

        structured_transform = yaw_transform @ floor_transform

        print("Structured scan transform:")
        print(structured_transform)

        return scan_structured, structured_transform

    def center_align_cad(self, scan_structured, cad_down):
        scan_center = np.asarray(scan_structured.points).mean(axis=0)
        cad_center = np.asarray(cad_down.points).mean(axis=0)

        initial_translation = scan_center - cad_center

        print("Scan center:", np.round(scan_center, 4))
        print("CAD center :", np.round(cad_center, 4))
        print("Initial center shift:", np.round(initial_translation, 4))

        cad_initial = copy.deepcopy(cad_down)
        cad_initial.translate(initial_translation)

        manual_translation = np.array([
            self.config.MANUAL_TX,
            self.config.MANUAL_TY,
            self.config.MANUAL_TZ
        ])

        if np.any(manual_translation != 0.0):
            cad_initial.translate(manual_translation)
            print("Applied manual shift:", manual_translation.tolist())

        center_transform = np.eye(4)
        center_transform[:3, 3] = initial_translation + manual_translation

        return cad_initial, center_transform

    def run_icp(self, cad_initial, scan_structured):
        print("Running ICP refinement...")

        registration = o3d.pipelines.registration.registration_icp(
            cad_initial,
            scan_structured,
            self.config.ICP_DISTANCE,
            np.eye(4),
            o3d.pipelines.registration.TransformationEstimationPointToPlane()
        )

        print("ICP fitness:", registration.fitness)
        print("ICP RMSE:", registration.inlier_rmse)

        print("ICP transform:")
        print(registration.transformation)

        cad_final = copy.deepcopy(cad_initial)
        cad_final.transform(registration.transformation)

        return cad_final, registration.transformation