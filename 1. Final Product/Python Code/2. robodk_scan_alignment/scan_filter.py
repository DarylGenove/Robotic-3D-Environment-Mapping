import copy
import numpy as np
import open3d as o3d


class ScanFilter:
    """
    Cleans the scan point cloud using the aligned CAD/STL model.

    Main logic:
    1. Get the aligned CAD/STL bounding box.
    2. Expand it slightly using OUTER_CAD_MARGIN.
    3. Keep only scan points inside that CAD range.
    4. Treat scan points outside that CAD range as noise.
    5. Optionally remove statistical outliers after the CAD-bound crop.
    """

    def __init__(self, config):
        self.config = config

    def remove_scan_points_outside_cad_bounds(self, scan_pcd, cad_pcd):
        if len(scan_pcd.points) == 0:
            raise Exception("Scan point cloud is empty before CAD-bound filtering.")

        if len(cad_pcd.points) == 0:
            raise Exception("CAD point cloud is empty before CAD-bound filtering.")

        print("")
        print("=" * 70)
        print("Cleaning PCD scan using aligned STL/CAD range")
        print("=" * 70)

        print("Input scan points:", len(scan_pcd.points))
        print("Input CAD points :", len(cad_pcd.points))

        cad_bounding_box = cad_pcd.get_axis_aligned_bounding_box()

        cad_min_bound = cad_bounding_box.get_min_bound()
        cad_max_bound = cad_bounding_box.get_max_bound()

        margin = np.array([
            self.config.OUTER_CAD_MARGIN,
            self.config.OUTER_CAD_MARGIN,
            self.config.OUTER_CAD_MARGIN
        ], dtype=np.float64)

        expanded_min_bound = cad_min_bound - margin
        expanded_max_bound = cad_max_bound + margin

        print("CAD min bound:", np.round(cad_min_bound, 4))
        print("CAD max bound:", np.round(cad_max_bound, 4))
        print("CAD bound margin:", self.config.OUTER_CAD_MARGIN, "m")
        print("Expanded CAD min bound:", np.round(expanded_min_bound, 4))
        print("Expanded CAD max bound:", np.round(expanded_max_bound, 4))

        expanded_cad_bounding_box = o3d.geometry.AxisAlignedBoundingBox(
            min_bound=expanded_min_bound,
            max_bound=expanded_max_bound
        )

        inside_indices = expanded_cad_bounding_box.get_point_indices_within_bounding_box(
            scan_pcd.points
        )

        inside_indices = set(inside_indices)

        all_indices = set(range(len(scan_pcd.points)))

        outside_indices = list(all_indices - inside_indices)
        inside_indices = list(inside_indices)

        filtered_scan = scan_pcd.select_by_index(inside_indices)
        removed_noise = scan_pcd.select_by_index(outside_indices)

        print("Points kept inside STL/CAD range:", len(filtered_scan.points))
        print("Points removed outside STL/CAD range:", len(removed_noise.points))

        if len(filtered_scan.points) == 0:
            raise Exception(
                "All scan points were removed by CAD-bound filtering. "
                "Increase OUTER_CAD_MARGIN or check CAD/scan alignment."
            )

        if self.config.SAVE_REMOVED_NOISE and len(removed_noise.points) > 0:
            o3d.io.write_point_cloud(
                self.config.REMOVED_NOISE_FILE,
                removed_noise
            )
            print("Saved removed noise points to:", self.config.REMOVED_NOISE_FILE)

        filtered_scan = self.remove_post_filter_outliers(filtered_scan)

        filtered_scan.estimate_normals(
            search_param=o3d.geometry.KDTreeSearchParamHybrid(
                radius=self.config.VOXEL_SIZE * 2.0,
                max_nn=30
            )
        )

        print("Final cleaned scan points:", len(filtered_scan.points))
        print("=" * 70)
        print("")

        return filtered_scan

    def remove_post_filter_outliers(self, point_cloud):
        if not self.config.POST_FILTER_REMOVE_OUTLIERS:
            print("Post-filter outlier removal disabled.")
            return point_cloud

        if len(point_cloud.points) == 0:
            return point_cloud

        before_count = len(point_cloud.points)

        cleaned_cloud, _ = point_cloud.remove_statistical_outlier(
            nb_neighbors=self.config.POST_FILTER_OUTLIER_NB,
            std_ratio=self.config.POST_FILTER_OUTLIER_STD
        )

        removed_count = before_count - len(cleaned_cloud.points)

        print("Post-filter outlier removal enabled.")
        print("Post-filter removed points:", removed_count)
        print("Points after post-filter cleanup:", len(cleaned_cloud.points))

        if len(cleaned_cloud.points) == 0:
            raise Exception(
                "Post-filter outlier removal removed all points. "
                "Increase POST_FILTER_OUTLIER_STD or disable POST_FILTER_REMOVE_OUTLIERS."
            )

        return cleaned_cloud

    def preview_cad_range_filter(self, scan_pcd, cad_pcd):
        """
        Optional debug preview.

        Blue  = kept scan points inside STL/CAD range
        Red   = removed noise outside STL/CAD range
        Green = aligned CAD/STL point cloud
        """

        cad_bounding_box = cad_pcd.get_axis_aligned_bounding_box()

        margin = np.array([
            self.config.OUTER_CAD_MARGIN,
            self.config.OUTER_CAD_MARGIN,
            self.config.OUTER_CAD_MARGIN
        ], dtype=np.float64)

        expanded_cad_bounding_box = o3d.geometry.AxisAlignedBoundingBox(
            min_bound=cad_bounding_box.get_min_bound() - margin,
            max_bound=cad_bounding_box.get_max_bound() + margin
        )

        inside_indices = expanded_cad_bounding_box.get_point_indices_within_bounding_box(
            scan_pcd.points
        )

        inside_indices = set(inside_indices)
        all_indices = set(range(len(scan_pcd.points)))

        outside_indices = list(all_indices - inside_indices)
        inside_indices = list(inside_indices)

        kept_scan = copy.deepcopy(scan_pcd.select_by_index(inside_indices))
        removed_noise = copy.deepcopy(scan_pcd.select_by_index(outside_indices))
        cad_copy = copy.deepcopy(cad_pcd)

        kept_scan.paint_uniform_color([0.1, 0.7, 1.0])
        removed_noise.paint_uniform_color([1.0, 0.0, 0.0])
        cad_copy.paint_uniform_color([0.0, 1.0, 0.0])

        o3d.visualization.draw_geometries(
            [
                kept_scan,
                removed_noise,
                cad_copy,
                expanded_cad_bounding_box
            ],
            window_name="CAD Range Filter Preview: Blue=Kept, Red=Removed, Green=CAD"
        )