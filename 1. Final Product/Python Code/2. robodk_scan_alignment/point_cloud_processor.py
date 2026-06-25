import os
import numpy as np
import open3d as o3d


class PointCloudProcessor:
    """
    Handles loading, cropping, downsampling, optional outlier removal,
    CAD scaling, CAD orientation correction, and normal estimation.
    """

    def __init__(self, config):
        self.config = config

    def load_scan(self):
        if not os.path.exists(self.config.SCAN_FILE):
            raise FileNotFoundError(
                f"Scan file was not found: {self.config.SCAN_FILE}"
            )

        scan = o3d.io.read_point_cloud(self.config.SCAN_FILE)

        if len(scan.points) == 0:
            raise Exception(
                f"Scan point cloud is empty or could not be read: "
                f"{self.config.SCAN_FILE}"
            )

        print("")
        print("Loaded scan file:", self.config.SCAN_FILE)
        print("Raw scan points:", len(scan.points))
        print("Raw scan min bound:", np.round(scan.get_min_bound(), 4))
        print("Raw scan max bound:", np.round(scan.get_max_bound(), 4))

        scan = self.crop_scan(scan)

        return scan

    def load_cad_as_point_cloud(self):
        if not os.path.exists(self.config.CAD_FILE):
            raise FileNotFoundError(
                f"CAD file was not found: {self.config.CAD_FILE}"
            )

        cad_mesh = o3d.io.read_triangle_mesh(self.config.CAD_FILE)

        if cad_mesh.is_empty():
            raise Exception(
                f"CAD mesh is empty or could not be read: "
                f"{self.config.CAD_FILE}"
            )

        print("")
        print("Loaded CAD file:", self.config.CAD_FILE)
        print("CAD mesh min bound before scale:", np.round(cad_mesh.get_min_bound(), 4))
        print("CAD mesh max bound before scale:", np.round(cad_mesh.get_max_bound(), 4))

        cad_mesh.scale(
            self.config.CAD_SCALE,
            center=(0.0, 0.0, 0.0)
        )

        print("CAD scale applied:", self.config.CAD_SCALE)
        print("CAD mesh min bound after scale:", np.round(cad_mesh.get_min_bound(), 4))
        print("CAD mesh max bound after scale:", np.round(cad_mesh.get_max_bound(), 4))

        cad_mesh = self.apply_extra_cad_rotation(cad_mesh)

        cad_mesh.compute_vertex_normals()

        cad_point_cloud = cad_mesh.sample_points_uniformly(
            number_of_points=self.config.CAD_SAMPLE_POINTS
        )

        print("CAD sampled points:", len(cad_point_cloud.points))
        print("CAD point cloud min bound:", np.round(cad_point_cloud.get_min_bound(), 4))
        print("CAD point cloud max bound:", np.round(cad_point_cloud.get_max_bound(), 4))

        return cad_point_cloud

    def apply_extra_cad_rotation(self, cad_mesh):
        rx = np.radians(self.config.CAD_EXTRA_RX_DEG)
        ry = np.radians(self.config.CAD_EXTRA_RY_DEG)
        rz = np.radians(self.config.CAD_EXTRA_RZ_DEG)

        rotation_matrix = cad_mesh.get_rotation_matrix_from_xyz(
            (rx, ry, rz)
        )

        cad_center = cad_mesh.get_center()

        cad_mesh.rotate(
            rotation_matrix,
            center=cad_center
        )

        print("")
        print("Extra CAD rotation applied:")
        print("  RX:", self.config.CAD_EXTRA_RX_DEG, "degrees")
        print("  RY:", self.config.CAD_EXTRA_RY_DEG, "degrees")
        print("  RZ:", self.config.CAD_EXTRA_RZ_DEG, "degrees")
        print("CAD mesh min bound after rotation:", np.round(cad_mesh.get_min_bound(), 4))
        print("CAD mesh max bound after rotation:", np.round(cad_mesh.get_max_bound(), 4))

        return cad_mesh

    def preprocess(self, point_cloud):
        print("")
        print("Preprocessing point cloud...")
        print("Input points:", len(point_cloud.points))

        point_cloud = point_cloud.voxel_down_sample(self.config.VOXEL_SIZE)

        print("Points after voxel downsample:", len(point_cloud.points))

        if self.config.REMOVE_OUTLIERS and len(point_cloud.points) > 0:
            before_outlier_removal = len(point_cloud.points)

            point_cloud, _ = point_cloud.remove_statistical_outlier(
                nb_neighbors=self.config.OUTLIER_NB,
                std_ratio=self.config.OUTLIER_STD
            )

            removed_points = before_outlier_removal - len(point_cloud.points)

            print("Outlier removal enabled.")
            print("Removed outlier points:", removed_points)
            print("Points after outlier removal:", len(point_cloud.points))
        else:
            print("Outlier removal disabled. Keeping downsampled raw points.")

        if len(point_cloud.points) == 0:
            raise Exception("Point cloud became empty after preprocessing.")

        point_cloud.estimate_normals(
            search_param=o3d.geometry.KDTreeSearchParamHybrid(
                radius=self.config.VOXEL_SIZE * 2.0,
                max_nn=30
            )
        )

        print("Preprocessed min bound:", np.round(point_cloud.get_min_bound(), 4))
        print("Preprocessed max bound:", np.round(point_cloud.get_max_bound(), 4))

        return point_cloud

    def crop_scan(self, scan):
        if not self.config.USE_CROP:
            print("Manual crop disabled. Keeping full scan.")
            return scan

        bounding_box = o3d.geometry.AxisAlignedBoundingBox(
            min_bound=np.array(self.config.CROP_MIN, dtype=np.float64),
            max_bound=np.array(self.config.CROP_MAX, dtype=np.float64)
        )

        cropped_scan = scan.crop(bounding_box)

        if len(cropped_scan.points) == 0:
            raise Exception("Cropped scan is empty. Adjust crop bounds.")

        print("Manual crop enabled.")
        print("Cropped scan points:", len(cropped_scan.points))
        print("Cropped scan min bound:", np.round(cropped_scan.get_min_bound(), 4))
        print("Cropped scan max bound:", np.round(cropped_scan.get_max_bound(), 4))

        return cropped_scan