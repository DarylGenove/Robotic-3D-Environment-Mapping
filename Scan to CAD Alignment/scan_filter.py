import numpy as np
import open3d as o3d


class ScanFilter:
    """
    Removes scan points outside the aligned CAD bounding box.
    """

    def __init__(self, config):
        self.config = config

    def remove_scan_points_outside_cad_bounds(self, scan_pcd, cad_pcd):
        if len(scan_pcd.points) == 0:
            raise Exception("Scan point cloud is empty before outer-bound filtering.")

        if len(cad_pcd.points) == 0:
            raise Exception("CAD point cloud is empty before outer-bound filtering.")

        cad_bounding_box = cad_pcd.get_axis_aligned_bounding_box()

        min_bound = cad_bounding_box.get_min_bound() - np.array([
            self.config.OUTER_CAD_MARGIN,
            self.config.OUTER_CAD_MARGIN,
            self.config.OUTER_CAD_MARGIN
        ])

        max_bound = cad_bounding_box.get_max_bound() + np.array([
            self.config.OUTER_CAD_MARGIN,
            self.config.OUTER_CAD_MARGIN,
            self.config.OUTER_CAD_MARGIN
        ])

        expanded_bounding_box = o3d.geometry.AxisAlignedBoundingBox(
            min_bound=min_bound,
            max_bound=max_bound
        )

        filtered_scan = scan_pcd.crop(expanded_bounding_box)

        if len(filtered_scan.points) == 0:
            raise Exception("All scan points were removed. Increase OUTER_CAD_MARGIN.")

        filtered_scan.estimate_normals(
            search_param=o3d.geometry.KDTreeSearchParamHybrid(
                radius=self.config.VOXEL_SIZE * 2.0,
                max_nn=30
            )
        )

        removed_count = len(scan_pcd.points) - len(filtered_scan.points)

        print("Removed outside scan points:", removed_count)
        print("Remaining scan points:", len(filtered_scan.points))

        return filtered_scan