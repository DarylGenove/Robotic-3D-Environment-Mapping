import numpy as np
import open3d as o3d


class PointCloudService:
    def __init__(self, config):
        self.config = config

    @staticmethod
    def print_cloud_bounds(name, point_cloud):
        if len(point_cloud.points) == 0:
            print(f"{name}: empty point cloud")
            return

        bounding_box = point_cloud.get_axis_aligned_bounding_box()

        print("")
        print(name)
        print("Points:", len(point_cloud.points))
        print("Min bound:", np.round(bounding_box.get_min_bound(), 4))
        print("Max bound:", np.round(bounding_box.get_max_bound(), 4))
        print("Center   :", np.round(bounding_box.get_center(), 4))
        print("Extent   :", np.round(bounding_box.get_extent(), 4))

    def estimate_camera_cloud_bounds(self, point_cloud):
        points = np.asarray(point_cloud.points)

        if len(points) < self.config.MIN_REFERENCE_POINTS:
            raise Exception(
                f"Not enough points for adaptive scan estimation. "
                f"Points found: {len(points)}"
            )

        valid_mask = (
            np.isfinite(points[:, 0])
            & np.isfinite(points[:, 1])
            & np.isfinite(points[:, 2])
            & (points[:, 2] > 0.05)
            & (points[:, 2] < self.config.DEPTH_TRUNC_MAX)
        )

        points = points[valid_mask]

        if len(points) < self.config.MIN_REFERENCE_POINTS:
            raise Exception(
                f"Not enough valid depth points for adaptive scan estimation. "
                f"Valid points found: {len(points)}"
            )

        min_x = np.percentile(points[:, 0], self.config.BOUNDS_LOW_PERCENTILE)
        max_x = np.percentile(points[:, 0], self.config.BOUNDS_HIGH_PERCENTILE)

        min_y = np.percentile(points[:, 1], self.config.BOUNDS_LOW_PERCENTILE)
        max_y = np.percentile(points[:, 1], self.config.BOUNDS_HIGH_PERCENTILE)

        min_z = np.percentile(points[:, 2], self.config.BOUNDS_LOW_PERCENTILE)
        max_z = np.percentile(points[:, 2], self.config.BOUNDS_HIGH_PERCENTILE)

        bounds = {
            "min_x": float(min_x),
            "max_x": float(max_x),
            "min_y": float(min_y),
            "max_y": float(max_y),
            "min_z": float(min_z),
            "max_z": float(max_z),
            "center_x": float((min_x + max_x) / 2.0),
            "center_y": float((min_y + max_y) / 2.0),
            "center_z": float(np.median(points[:, 2])),
            "extent_x": float(max_x - min_x),
            "extent_y": float(max_y - min_y),
            "extent_z": float(max_z - min_z),
        }

        print("")
        print("Adaptive camera-frame bounds estimated from reference scan:")
        for key, value in bounds.items():
            print(f"{key}: {value:.4f} m")

        return bounds

    def crop_adaptive(self, point_cloud, adaptive_bounds):
        if len(point_cloud.points) == 0:
            return point_cloud

        points = np.asarray(point_cloud.points)

        min_x = adaptive_bounds["min_x"] - self.config.ADAPTIVE_CROP_MARGIN_X_M
        max_x = adaptive_bounds["max_x"] + self.config.ADAPTIVE_CROP_MARGIN_X_M

        min_y = adaptive_bounds["min_y"] - self.config.ADAPTIVE_CROP_MARGIN_Y_M
        max_y = adaptive_bounds["max_y"] + self.config.ADAPTIVE_CROP_MARGIN_Y_M

        min_z = max(0.05, adaptive_bounds["min_z"] - self.config.ADAPTIVE_CROP_MARGIN_Z_M)
        max_z = min(
            self.config.DEPTH_TRUNC_MAX,
            adaptive_bounds["max_z"] + self.config.ADAPTIVE_CROP_MARGIN_Z_M,
        )

        mask = (
            (points[:, 0] >= min_x)
            & (points[:, 0] <= max_x)
            & (points[:, 1] >= min_y)
            & (points[:, 1] <= max_y)
            & (points[:, 2] >= min_z)
            & (points[:, 2] <= max_z)
        )

        indices = np.where(mask)[0]

        if len(indices) == 0:
            print("WARNING: Adaptive crop removed all points. Keeping original cloud.")
            return point_cloud

        cropped_cloud = point_cloud.select_by_index(indices)

        print("Adaptive camera-frame crop enabled.")
        print("Points before adaptive crop:", len(point_cloud.points))
        print("Points after adaptive crop :", len(cropped_cloud.points))

        return cropped_cloud

    def clean(self, point_cloud):
        if len(point_cloud.points) == 0:
            return point_cloud

        point_cloud = point_cloud.voxel_down_sample(
            voxel_size=self.config.SURFACE_VOXEL_SIZE
        )

        if len(point_cloud.points) == 0:
            return point_cloud

        point_cloud, _ = point_cloud.remove_statistical_outlier(
            nb_neighbors=self.config.OUTLIER_NB_NEIGHBORS,
            std_ratio=self.config.OUTLIER_STD_RATIO,
        )

        return point_cloud

    def estimate_normals(self, point_cloud):
        if len(point_cloud.points) == 0:
            return point_cloud

        point_cloud.estimate_normals(
            search_param=o3d.geometry.KDTreeSearchParamHybrid(
                radius=self.config.NORMAL_RADIUS,
                max_nn=self.config.NORMAL_MAX_NN,
            )
        )

        return point_cloud

    def save_debug_scan(self, label, point_cloud):
        debug_file = self.config.OUTPUT_FOLDER / f"debug_{label}.pcd"

        o3d.io.write_point_cloud(str(debug_file), point_cloud)

        print("Saved debug scan:", debug_file)
        self.print_cloud_bounds(f"Debug scan bounds - {label}", point_cloud)
