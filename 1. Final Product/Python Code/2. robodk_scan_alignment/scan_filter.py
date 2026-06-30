# Bring in copy so this file can use it.
import copy
# Bring in numpy so this file can use it.
import numpy as np
# Bring in open3d so this file can use it.
import open3d as o3d


# Create the ScanFilter class, which groups related code together.
class ScanFilter:


    # Create the setup function that runs when this object is made.
    def __init__(self, config):
        # Save this value inside the object for later.
        self.config = config

    # Create the remove scan points outside cad bounds function.
    def remove_scan_points_outside_cad_bounds(self, scan_pcd, cad_pcd):
        # Count how many points are inside this object.
        if len(scan_pcd.points) == 0:
            # Stop the program and show a clear error message.
            raise Exception("Scan point cloud is empty before CAD-bound filtering.")

        # Count how many points are inside this object.
        if len(cad_pcd.points) == 0:
            # Stop the program and show a clear error message.
            raise Exception("CAD point cloud is empty before CAD-bound filtering.")

        # Show helpful information on the screen.
        print("")
        # Show helpful information on the screen.
        print("=" * 70)
        # Show helpful information on the screen.
        print("Cleaning PCD scan using aligned STL/CAD range")
        # Show helpful information on the screen.
        print("=" * 70)

        # Count how many points are inside this object.
        print("Input scan points:", len(scan_pcd.points))
        # Count how many points are inside this object.
        print("Input CAD points :", len(cad_pcd.points))

        # Create a simple box around the object.
        cad_bounding_box = cad_pcd.get_axis_aligned_bounding_box()

        # Save a value in cad min bound.
        cad_min_bound = cad_bounding_box.get_min_bound()
        # Save a value in cad max bound.
        cad_max_bound = cad_bounding_box.get_max_bound()

        # Put these numbers into a NumPy array.
        margin = np.array([
            # Add this value to the current group.
            self.config.OUTER_CAD_MARGIN,
            # Add this value to the current group.
            self.config.OUTER_CAD_MARGIN,
            # Run this line as one small step in the program.
            self.config.OUTER_CAD_MARGIN
        # Save several results into separate variable names.
        ], dtype=np.float64)

        # Save a value in expanded min bound.
        expanded_min_bound = cad_min_bound - margin
        # Save a value in expanded max bound.
        expanded_max_bound = cad_max_bound + margin

        # Round the numbers so they are easier to read.
        print("CAD min bound:", np.round(cad_min_bound, 4))
        # Round the numbers so they are easier to read.
        print("CAD max bound:", np.round(cad_max_bound, 4))
        # Show helpful information on the screen.
        print("CAD bound margin:", self.config.OUTER_CAD_MARGIN, "m")
        # Round the numbers so they are easier to read.
        print("Expanded CAD min bound:", np.round(expanded_min_bound, 4))
        # Round the numbers so they are easier to read.
        print("Expanded CAD max bound:", np.round(expanded_max_bound, 4))

        # Save a value in expanded cad bounding box.
        expanded_cad_bounding_box = o3d.geometry.AxisAlignedBoundingBox(
            # Save a value in min bound.
            min_bound=expanded_min_bound,
            # Save a value in max bound.
            max_bound=expanded_max_bound
        )

        # Find which scan points are inside the CAD box.
        inside_indices = expanded_cad_bounding_box.get_point_indices_within_bounding_box(
            # Run this line as one small step in the program.
            scan_pcd.points
        )

        # Save a value in inside indices.
        inside_indices = set(inside_indices)

        # Count how many points are inside this object.
        all_indices = set(range(len(scan_pcd.points)))

        # Save a value in outside indices.
        outside_indices = list(all_indices - inside_indices)
        # Save a value in inside indices.
        inside_indices = list(inside_indices)

        # Pick only the points with these index numbers.
        filtered_scan = scan_pcd.select_by_index(inside_indices)
        # Pick only the points with these index numbers.
        removed_noise = scan_pcd.select_by_index(outside_indices)

        # Count how many points are inside this object.
        print("Points kept inside STL/CAD range:", len(filtered_scan.points))
        # Count how many points are inside this object.
        print("Points removed outside STL/CAD range:", len(removed_noise.points))

        # Count how many points are inside this object.
        if len(filtered_scan.points) == 0:
            # Stop the program and show a clear error message.
            raise Exception(
                # Run this line as one small step in the program.
                "All scan points were removed by CAD-bound filtering. "
                # Run this line as one small step in the program.
                "Increase OUTER_CAD_MARGIN or check CAD/scan alignment."
            )

        # Count how many points are inside this object.
        if self.config.SAVE_REMOVED_NOISE and len(removed_noise.points) > 0:
            # Save a point cloud file to the computer.
            o3d.io.write_point_cloud(
                # Add this value to the current group.
                self.config.REMOVED_NOISE_FILE,
                # Run this line as one small step in the program.
                removed_noise
            )
            # Show helpful information on the screen.
            print("Saved removed noise points to:", self.config.REMOVED_NOISE_FILE)

        # Save a value in filtered scan.
        filtered_scan = self.remove_post_filter_outliers(filtered_scan)

        # Calculate which way the surface points are facing.
        filtered_scan.estimate_normals(
            # Save a value in search param.
            search_param=o3d.geometry.KDTreeSearchParamHybrid(
                # Save a value in radius.
                radius=self.config.VOXEL_SIZE * 2.0,
                # Save a value in max nn.
                max_nn=30
            )
        )

        # Count how many points are inside this object.
        print("Final cleaned scan points:", len(filtered_scan.points))
        # Show helpful information on the screen.
        print("=" * 70)
        # Show helpful information on the screen.
        print("")

        # Send this result back to the part of the code that asked for it.
        return filtered_scan

    # Create the remove post filter outliers function.
    def remove_post_filter_outliers(self, point_cloud):
        # Check this condition before choosing what happens next.
        if not self.config.POST_FILTER_REMOVE_OUTLIERS:
            # Show helpful information on the screen.
            print("Post-filter outlier removal disabled.")
            # Send this result back to the part of the code that asked for it.
            return point_cloud

        # Count how many points are inside this object.
        if len(point_cloud.points) == 0:
            # Send this result back to the part of the code that asked for it.
            return point_cloud

        # Count how many points are inside this object.
        before_count = len(point_cloud.points)

        # Remove points that look like random noise.
        cleaned_cloud, _ = point_cloud.remove_statistical_outlier(
            # Save a value in nb neighbors.
            nb_neighbors=self.config.POST_FILTER_OUTLIER_NB,
            # Save a value in std ratio.
            std_ratio=self.config.POST_FILTER_OUTLIER_STD
        )

        # Count how many points are inside this object.
        removed_count = before_count - len(cleaned_cloud.points)

        # Show helpful information on the screen.
        print("Post-filter outlier removal enabled.")
        # Show helpful information on the screen.
        print("Post-filter removed points:", removed_count)
        # Count how many points are inside this object.
        print("Points after post-filter cleanup:", len(cleaned_cloud.points))

        # Count how many points are inside this object.
        if len(cleaned_cloud.points) == 0:
            # Stop the program and show a clear error message.
            raise Exception(
                # Run this line as one small step in the program.
                "Post-filter outlier removal removed all points. "
                # Run this line as one small step in the program.
                "Increase POST_FILTER_OUTLIER_STD or disable POST_FILTER_REMOVE_OUTLIERS."
            )

        # Send this result back to the part of the code that asked for it.
        return cleaned_cloud

    # Create the preview cad range filter function.
    def preview_cad_range_filter(self, scan_pcd, cad_pcd):


        # Create a simple box around the object.
        cad_bounding_box = cad_pcd.get_axis_aligned_bounding_box()

        # Put these numbers into a NumPy array.
        margin = np.array([
            # Add this value to the current group.
            self.config.OUTER_CAD_MARGIN,
            # Add this value to the current group.
            self.config.OUTER_CAD_MARGIN,
            # Run this line as one small step in the program.
            self.config.OUTER_CAD_MARGIN
        # Save several results into separate variable names.
        ], dtype=np.float64)

        # Save a value in expanded cad bounding box.
        expanded_cad_bounding_box = o3d.geometry.AxisAlignedBoundingBox(
            # Save a value in min bound.
            min_bound=cad_bounding_box.get_min_bound() - margin,
            # Save a value in max bound.
            max_bound=cad_bounding_box.get_max_bound() + margin
        )

        # Find which scan points are inside the CAD box.
        inside_indices = expanded_cad_bounding_box.get_point_indices_within_bounding_box(
            # Run this line as one small step in the program.
            scan_pcd.points
        )

        # Save a value in inside indices.
        inside_indices = set(inside_indices)
        # Count how many points are inside this object.
        all_indices = set(range(len(scan_pcd.points)))

        # Save a value in outside indices.
        outside_indices = list(all_indices - inside_indices)
        # Save a value in inside indices.
        inside_indices = list(inside_indices)

        # Make a safe copy so the original object does not change.
        kept_scan = copy.deepcopy(scan_pcd.select_by_index(inside_indices))
        # Make a safe copy so the original object does not change.
        removed_noise = copy.deepcopy(scan_pcd.select_by_index(outside_indices))
        # Make a safe copy so the original object does not change.
        cad_copy = copy.deepcopy(cad_pcd)

        # Give the whole point cloud one color.
        kept_scan.paint_uniform_color([0.1, 0.7, 1.0])
        # Give the whole point cloud one color.
        removed_noise.paint_uniform_color([1.0, 0.0, 0.0])
        # Give the whole point cloud one color.
        cad_copy.paint_uniform_color([0.0, 1.0, 0.0])

        # Open a 3D window to show the scan and CAD model.
        o3d.visualization.draw_geometries(
            # Start a group of values.
            [
                # Add this value to the current group.
                kept_scan,
                # Add this value to the current group.
                removed_noise,
                # Add this value to the current group.
                cad_copy,
                # Run this line as one small step in the program.
                expanded_cad_bounding_box
            ],
            # Save a value in window name.
            window_name="CAD Range Filter Preview: Blue=Kept, Red=Removed, Green=CAD"
        )
