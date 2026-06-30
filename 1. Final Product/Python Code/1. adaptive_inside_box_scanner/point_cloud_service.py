import numpy as np  # Loads NumPy as np so the code can do fast number and matrix math.
import open3d as o3d  # Loads Open3D so the code can work with 3D point clouds.


class PointCloudService:  # Makes a toolbox for point-cloud checking, cropping, cleaning, and saving.
    def __init__(self, config):  # Makes a function named   init  .
        self.config = config  # Stores the scanner settings so the program can use them.

    @staticmethod  # Lets this helper run without using object data.
    def print_cloud_bounds(name, point_cloud):  # Shows useful size information about a point cloud.
        if len(point_cloud.points) == 0:  # Checks if there are no items to work with.
            print(f"{name}: empty point cloud")  # Shows a message in the console.
            return  # Gives this result back to the part of the code that called it.

        bounding_box = point_cloud.get_axis_aligned_bounding_box()  # Stores a simple box around all 3D points.

        print("")  # Shows a message in the console.
        print(name)  # Shows a message in the console.
        print("Points:", len(point_cloud.points))  # Shows a message in the console.
        print("Min bound:", np.round(bounding_box.get_min_bound(), 4))  # Shows a message in the console.
        print("Max bound:", np.round(bounding_box.get_max_bound(), 4))  # Shows a message in the console.
        print("Center   :", np.round(bounding_box.get_center(), 4))  # Shows a message in the console.
        print("Extent   :", np.round(bounding_box.get_extent(), 4))  # Shows a message in the console.

    def estimate_camera_cloud_bounds(self, point_cloud):  # Estimates the cabinet area from the first camera scan.
        points = np.asarray(point_cloud.points)  # Stores the point cloud points as a NumPy table.

        if len(points) < self.config.MIN_REFERENCE_POINTS:  # Checks if there are too few items to trust.
            raise Exception(  # Stops the program because something important went wrong.
                f"Not enough points for adaptive scan estimation. "  # Runs this line as one small step in the program.
                f"Points found: {len(points)}"  # Counts how many items there are.
            )  # Closes the multi-line code started above.

        valid_mask = (  # Marks only points/pixels that look usable.
            np.isfinite(points[:, 0])  # Checks that numbers are real and not broken.
            & np.isfinite(points[:, 1])  # Checks that numbers are real and not broken.
            & np.isfinite(points[:, 2])  # Checks that numbers are real and not broken.
            & (points[:, 2] > 0.05)  # Adds another rule to the filter condition.
            & (points[:, 2] < self.config.DEPTH_TRUNC_MAX)  # Adds another rule to the filter condition.
        )  # Closes the multi-line code started above.

        points = points[valid_mask]  # Stores the point cloud points as a NumPy table.

        if len(points) < self.config.MIN_REFERENCE_POINTS:  # Checks if there are too few items to trust.
            raise Exception(  # Stops the program because something important went wrong.
                f"Not enough valid depth points for adaptive scan estimation. "  # Runs this line as one small step in the program.
                f"Valid points found: {len(points)}"  # Counts how many items there are.
            )  # Closes the multi-line code started above.

        min_x = np.percentile(points[:, 0], self.config.BOUNDS_LOW_PERCENTILE)  # Stores min x for use in the next steps.
        max_x = np.percentile(points[:, 0], self.config.BOUNDS_HIGH_PERCENTILE)  # Stores max x for use in the next steps.

        min_y = np.percentile(points[:, 1], self.config.BOUNDS_LOW_PERCENTILE)  # Stores min y for use in the next steps.
        max_y = np.percentile(points[:, 1], self.config.BOUNDS_HIGH_PERCENTILE)  # Stores max y for use in the next steps.

        min_z = np.percentile(points[:, 2], self.config.BOUNDS_LOW_PERCENTILE)  # Stores min z for use in the next steps.
        max_z = np.percentile(points[:, 2], self.config.BOUNDS_HIGH_PERCENTILE)  # Stores max z for use in the next steps.

        bounds = {  # Stores the min, max, center, and size of the point cloud.
            "min_x": float(min_x),  # Changes the value into a decimal number.
            "max_x": float(max_x),  # Changes the value into a decimal number.
            "min_y": float(min_y),  # Changes the value into a decimal number.
            "max_y": float(max_y),  # Changes the value into a decimal number.
            "min_z": float(min_z),  # Changes the value into a decimal number.
            "max_z": float(max_z),  # Changes the value into a decimal number.
            "center_x": float((min_x + max_x) / 2.0),  # Changes the value into a decimal number.
            "center_y": float((min_y + max_y) / 2.0),  # Changes the value into a decimal number.
            "center_z": float(np.median(points[:, 2])),  # Finds the middle value to reduce noise.
            "extent_x": float(max_x - min_x),  # Changes the value into a decimal number.
            "extent_y": float(max_y - min_y),  # Changes the value into a decimal number.
            "extent_z": float(max_z - min_z),  # Changes the value into a decimal number.
        }  # Closes the multi-line code started above.

        print("")  # Shows a message in the console.
        print("Adaptive camera-frame bounds estimated from reference scan:")  # Shows a message in the console.
        for key, value in bounds.items():  # Repeats the next indented lines for each item.
            print(f"{key}: {value:.4f} m")  # Shows a message in the console.

        return bounds  # Gives this result back to the part of the code that called it.

    def crop_adaptive(self, point_cloud, adaptive_bounds):  # Cuts the point cloud to the useful cabinet area.
        if len(point_cloud.points) == 0:  # Checks if there are no items to work with.
            return point_cloud  # Gives this result back to the part of the code that called it.

        points = np.asarray(point_cloud.points)  # Stores the point cloud points as a NumPy table.

        min_x = adaptive_bounds["min_x"] - self.config.ADAPTIVE_CROP_MARGIN_X_M  # Stores min x for use in the next steps.
        max_x = adaptive_bounds["max_x"] + self.config.ADAPTIVE_CROP_MARGIN_X_M  # Stores max x for use in the next steps.

        min_y = adaptive_bounds["min_y"] - self.config.ADAPTIVE_CROP_MARGIN_Y_M  # Stores min y for use in the next steps.
        max_y = adaptive_bounds["max_y"] + self.config.ADAPTIVE_CROP_MARGIN_Y_M  # Stores max y for use in the next steps.

        min_z = max(0.05, adaptive_bounds["min_z"] - self.config.ADAPTIVE_CROP_MARGIN_Z_M)  # Stores min z for use in the next steps.
        max_z = min(  # Stores max z for use in the next steps.
            self.config.DEPTH_TRUNC_MAX,  # Adds one item to the multi-line value.
            adaptive_bounds["max_z"] + self.config.ADAPTIVE_CROP_MARGIN_Z_M,  # Adds one item to the multi-line value.
        )  # Closes the multi-line code started above.

        mask = (  # Stores True or False for points/pixels that should be kept.
            (points[:, 0] >= min_x)  # Adds data inside the value being built.
            & (points[:, 0] <= max_x)  # Adds another rule to the filter condition.
            & (points[:, 1] >= min_y)  # Adds another rule to the filter condition.
            & (points[:, 1] <= max_y)  # Adds another rule to the filter condition.
            & (points[:, 2] >= min_z)  # Adds another rule to the filter condition.
            & (points[:, 2] <= max_z)  # Adds another rule to the filter condition.
        )  # Closes the multi-line code started above.

        indices = np.where(mask)[0]  # Stores the positions of the points that passed the filter.

        if len(indices) == 0:  # Checks if there are no items to work with.
            print("WARNING: Adaptive crop removed all points. Keeping original cloud.")  # Shows a message in the console.
            return point_cloud  # Gives this result back to the part of the code that called it.

        cropped_cloud = point_cloud.select_by_index(indices)  # Stores the point cloud after cutting away unwanted points.

        print("Adaptive camera-frame crop enabled.")  # Shows a message in the console.
        print("Points before adaptive crop:", len(point_cloud.points))  # Shows a message in the console.
        print("Points after adaptive crop :", len(cropped_cloud.points))  # Shows a message in the console.

        return cropped_cloud  # Gives this result back to the part of the code that called it.

    def clean(self, point_cloud):  # Makes the point cloud smaller and removes noisy points.
        if len(point_cloud.points) == 0:  # Checks if there are no items to work with.
            return point_cloud  # Gives this result back to the part of the code that called it.

        point_cloud = point_cloud.voxel_down_sample(  # Stores the 3D points captured by the camera.
            voxel_size=self.config.SURFACE_VOXEL_SIZE  # Stores voxel size for use in the next steps.
        )  # Closes the multi-line code started above.

        if len(point_cloud.points) == 0:  # Checks if there are no items to work with.
            return point_cloud  # Gives this result back to the part of the code that called it.

        point_cloud, _ = point_cloud.remove_statistical_outlier(  # Removes lonely noisy points from the scan.
            nb_neighbors=self.config.OUTLIER_NB_NEIGHBORS,  # Stores nb neighbors for use in the next steps.
            std_ratio=self.config.OUTLIER_STD_RATIO,  # Stores std ratio for use in the next steps.
        )  # Closes the multi-line code started above.

        return point_cloud  # Gives this result back to the part of the code that called it.

    def estimate_normals(self, point_cloud):  # Calculates surface directions for the point cloud.
        if len(point_cloud.points) == 0:  # Checks if there are no items to work with.
            return point_cloud  # Gives this result back to the part of the code that called it.

        point_cloud.estimate_normals(  # Calculates surface directions for the final point cloud.
            search_param=o3d.geometry.KDTreeSearchParamHybrid(  # Stores search param for use in the next steps.
                radius=self.config.NORMAL_RADIUS,  # Stores radius for use in the next steps.
                max_nn=self.config.NORMAL_MAX_NN,  # Stores max nn for use in the next steps.
            )  # Closes the multi-line code started above.
        )  # Closes the multi-line code started above.

        return point_cloud  # Gives this result back to the part of the code that called it.

    def save_debug_scan(self, label, point_cloud):  # Saves one scan for checking and debugging later.
        debug_file = self.config.OUTPUT_FOLDER / f"debug_{label}.pcd"  # Stores debug file for use in the next steps.

        o3d.io.write_point_cloud(str(debug_file), point_cloud)  # Saves the point cloud to a file.

        print("Saved debug scan:", debug_file)  # Shows a message in the console.
        self.print_cloud_bounds(f"Debug scan bounds - {label}", point_cloud)  # Shows the size and position information for this point cloud.
