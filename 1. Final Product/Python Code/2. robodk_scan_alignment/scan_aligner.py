import copy
import itertools

import numpy as np
import open3d as o3d


class ScanAligner:
    """
    Handles cabinet-based scan and CAD alignment.

    This version does not automatically guess the cabinet opening direction.
    The previous opening-detection approach could rotate the scan and CAD
    differently when the hole/opening was detected on different faces.

    New logic:
    1. Keep the scan in the original robot-base coordinate frame.
    2. Try all safe 90-degree CAD orientations.
    3. Center-align each CAD candidate to the scan.
    4. Run ICP for each candidate.
    5. Choose the candidate with the best ICP result.
    """

    def __init__(self, config, plane_detector):
        self.config = config
        self.plane_detector = plane_detector

    def get_robust_bounds(self, point_cloud):
        if len(point_cloud.points) == 0:
            raise Exception("Point cloud is empty.")

        points = np.asarray(point_cloud.points)

        min_bound = np.percentile(
            points,
            1.0,
            axis=0
        )

        max_bound = np.percentile(
            points,
            99.0,
            axis=0
        )

        return min_bound, max_bound

    def make_transform_from_rotation(self, rotation_matrix):
        transformation = np.eye(4)
        transformation[:3, :3] = rotation_matrix
        return transformation

    def make_transform_from_translation(self, translation):
        transformation = np.eye(4)
        transformation[:3, 3] = translation
        return transformation

    def rotation_x(self, angle_radians):
        cosine_angle = np.cos(angle_radians)
        sine_angle = np.sin(angle_radians)

        return np.array([
            [1.0, 0.0, 0.0],
            [0.0, cosine_angle, -sine_angle],
            [0.0, sine_angle, cosine_angle]
        ])

    def rotation_y(self, angle_radians):
        cosine_angle = np.cos(angle_radians)
        sine_angle = np.sin(angle_radians)

        return np.array([
            [cosine_angle, 0.0, sine_angle],
            [0.0, 1.0, 0.0],
            [-sine_angle, 0.0, cosine_angle]
        ])

    def rotation_z(self, angle_radians):
        cosine_angle = np.cos(angle_radians)
        sine_angle = np.sin(angle_radians)

        return np.array([
            [cosine_angle, -sine_angle, 0.0],
            [sine_angle, cosine_angle, 0.0],
            [0.0, 0.0, 1.0]
        ])

    def generate_right_angle_rotations(self):
        """
        Generates unique 90-degree rotation candidates.

        This is safer than guessing the opening side from point density.
        It lets the code test different CAD orientations and select the
        one that best matches the scanned cabinet.
        """

        angles = [
            0.0,
            np.pi / 2.0,
            np.pi,
            3.0 * np.pi / 2.0
        ]

        rotations = []

        for rx, ry, rz in itertools.product(angles, angles, angles):
            rotation_matrix = (
                self.rotation_z(rz)
                @ self.rotation_y(ry)
                @ self.rotation_x(rx)
            )

            rounded_matrix = np.round(rotation_matrix, 6)

            is_duplicate = False

            for existing_rotation in rotations:
                if np.allclose(
                    rounded_matrix,
                    existing_rotation,
                    atol=1e-6
                ):
                    is_duplicate = True
                    break

            if not is_duplicate:
                rotations.append(rounded_matrix)

        print("")
        print("Generated right-angle CAD orientation candidates:", len(rotations))

        return rotations

    def estimate_normals(self, point_cloud):
        if len(point_cloud.points) == 0:
            raise Exception("Cannot estimate normals on an empty point cloud.")

        point_cloud.estimate_normals(
            search_param=o3d.geometry.KDTreeSearchParamHybrid(
                radius=self.config.VOXEL_SIZE * 2.0,
                max_nn=30
            )
        )

        return point_cloud

    def structure_scan(self, scan_down):
        """
        Keep the scan in the robot-base coordinate frame.

        The scan was already created from the robot FK and camera transform
        during the RoboDK scanning step. Rotating it again here can break
        the relationship between the robot and the scanned cabinet.
        """

        print("")
        print("=" * 70)
        print("Keeping scan in original robot-base coordinate frame")
        print("=" * 70)

        scan_structured = copy.deepcopy(scan_down)
        scan_structured = self.estimate_normals(scan_structured)

        structure_transform = np.eye(4)

        return scan_structured, structure_transform

    def structure_cad_to_floor(self, cad_down):
        """
        Keep the CAD in its loaded orientation first.

        The correct CAD orientation is selected later by testing multiple
        right-angle candidates against the scan.
        """

        print("")
        print("=" * 70)
        print("Keeping CAD in loaded orientation before orientation search")
        print("=" * 70)

        cad_structured = copy.deepcopy(cad_down)
        cad_structured = self.estimate_normals(cad_structured)

        cad_structure_transform = np.eye(4)

        return cad_structured, cad_structure_transform

    def center_align_cad(self, scan_structured, cad_down):
        """
        Aligns CAD to scan using bounding-box centers.
        """

        scan_bounding_box = scan_structured.get_axis_aligned_bounding_box()
        cad_bounding_box = cad_down.get_axis_aligned_bounding_box()

        scan_center = scan_bounding_box.get_center()
        cad_center = cad_bounding_box.get_center()

        scan_extent = scan_bounding_box.get_extent()
        cad_extent = cad_bounding_box.get_extent()

        initial_translation = scan_center - cad_center

        print("")
        print("=" * 70)
        print("Center-aligning CAD to scan using bounding-box center")
        print("=" * 70)
        print("Scan bbox min   :", np.round(scan_bounding_box.get_min_bound(), 4))
        print("Scan bbox max   :", np.round(scan_bounding_box.get_max_bound(), 4))
        print("Scan bbox center:", np.round(scan_center, 4))
        print("Scan bbox extent:", np.round(scan_extent, 4))
        print("")
        print("CAD bbox min    :", np.round(cad_bounding_box.get_min_bound(), 4))
        print("CAD bbox max    :", np.round(cad_bounding_box.get_max_bound(), 4))
        print("CAD bbox center :", np.round(cad_center, 4))
        print("CAD bbox extent :", np.round(cad_extent, 4))
        print("")
        print("Initial XYZ center shift:", np.round(initial_translation, 4))

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

        cad_initial = self.estimate_normals(cad_initial)

        return cad_initial, center_transform

    def run_icp(self, cad_initial, scan_structured):
        print("")
        print("Running cabinet ICP refinement.")

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

        cad_final = self.estimate_normals(cad_final)

        return cad_final, registration.transformation

    def align_cad_to_scan_by_orientation_search(self, scan_structured, cad_structured):
        """
        Finds the best CAD orientation by trying all right-angle rotations.

        Returns:
        - best CAD before ICP
        - best CAD after ICP
        - best full CAD-to-scan transform
        - best orientation transform
        - best center transform
        - best ICP transform
        """

        print("")
        print("=" * 70)
        print("Starting CAD orientation search")
        print("=" * 70)

        scan_structured = self.estimate_normals(scan_structured)

        rotations = self.generate_right_angle_rotations()

        best_result = None
        best_score = -np.inf

        for index, rotation_matrix in enumerate(rotations, start=1):
            print("")
            print("-" * 70)
            print(f"Testing CAD orientation candidate {index}/{len(rotations)}")
            print("-" * 70)

            orientation_transform = self.make_transform_from_rotation(
                rotation_matrix
            )

            cad_oriented = copy.deepcopy(cad_structured)
            cad_oriented.transform(orientation_transform)
            cad_oriented = self.estimate_normals(cad_oriented)

            cad_initial, center_transform = self.center_align_cad(
                scan_structured,
                cad_oriented
            )

            try:
                cad_final, icp_transform = self.run_icp(
                    cad_initial,
                    scan_structured
                )
            except Exception as error:
                print("ICP failed for this orientation:", error)
                continue

            evaluation = o3d.pipelines.registration.evaluate_registration(
                cad_final,
                scan_structured,
                self.config.ICP_DISTANCE
            )

            fitness = float(evaluation.fitness)
            rmse = float(evaluation.inlier_rmse)

            score = fitness - rmse

            print("")
            print("Candidate result:")
            print("Fitness:", fitness)
            print("RMSE   :", rmse)
            print("Score  :", score)

            full_transform = (
                icp_transform
                @ center_transform
                @ orientation_transform
            )

            if best_result is None or score > best_score:
                best_score = score
                best_result = {
                    "candidate_index": index,
                    "cad_initial": cad_initial,
                    "cad_final": cad_final,
                    "full_transform": full_transform,
                    "orientation_transform": orientation_transform,
                    "center_transform": center_transform,
                    "icp_transform": icp_transform,
                    "fitness": fitness,
                    "rmse": rmse,
                    "score": score,
                }

        if best_result is None:
            raise Exception("No valid CAD orientation candidate could be aligned.")

        print("")
        print("=" * 70)
        print("Best CAD orientation selected")
        print("=" * 70)
        print("Candidate index:", best_result["candidate_index"])
        print("Fitness        :", best_result["fitness"])
        print("RMSE           :", best_result["rmse"])
        print("Score          :", best_result["score"])
        print("")
        print("Best CAD-to-scan transform:")
        print(best_result["full_transform"])

        return (
            best_result["cad_initial"],
            best_result["cad_final"],
            best_result["full_transform"],
            best_result["orientation_transform"],
            best_result["center_transform"],
            best_result["icp_transform"],
        )

    def create_floor_locked_transform(self, transformation):
        return transformation