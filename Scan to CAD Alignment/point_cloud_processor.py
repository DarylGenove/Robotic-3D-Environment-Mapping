import numpy as np
import open3d as o3d


class PointCloudProcessor:
    """
    Handles loading, cropping, downsampling, outlier removal, and normal estimation.
    """

    def __init__(self, config):
        self.config = config

    def load_scan(self):
        scan = o3d.io.read_point_cloud(self.config.SCAN_FILE)

        if len(scan.points) == 0:
            raise Exception("Scan point cloud is empty.")

        scan = self.crop_scan(scan)
        return scan

    def load_cad_as_point_cloud(self):
        cad_mesh = o3d.io.read_triangle_mesh(self.config.CAD_FILE)

        if cad_mesh.is_empty():
            raise Exception("CAD mesh is empty.")

        cad_mesh.compute_vertex_normals()

        cad_point_cloud = cad_mesh.sample_points_uniformly(
            number_of_points=self.config.CAD_SAMPLE_POINTS
        )

        return cad_point_cloud

    def preprocess(self, point_cloud):
        point_cloud = point_cloud.voxel_down_sample(self.config.VOXEL_SIZE)

        if self.config.REMOVE_OUTLIERS and len(point_cloud.points) > 0:
            point_cloud, _ = point_cloud.remove_statistical_outlier(
                nb_neighbors=self.config.OUTLIER_NB,
                std_ratio=self.config.OUTLIER_STD
            )

        if len(point_cloud.points) == 0:
            raise Exception("Point cloud became empty after preprocessing.")

        point_cloud.estimate_normals(
            search_param=o3d.geometry.KDTreeSearchParamHybrid(
                radius=self.config.VOXEL_SIZE * 2.0,
                max_nn=30
            )
        )

        return point_cloud

    def crop_scan(self, scan):
        if not self.config.USE_CROP:
            return scan

        bounding_box = o3d.geometry.AxisAlignedBoundingBox(
            min_bound=np.array(self.config.CROP_MIN, dtype=np.float64),
            max_bound=np.array(self.config.CROP_MAX, dtype=np.float64)
        )

        cropped_scan = scan.crop(bounding_box)

        if len(cropped_scan.points) == 0:
            raise Exception("Cropped scan is empty. Adjust crop bounds.")

        return cropped_scan