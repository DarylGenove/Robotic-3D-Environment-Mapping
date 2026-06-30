# Bring in os so this file can use it.
import os
# Bring in numpy so this file can use it.
import numpy as np
# Bring in open3d so this file can use it.
import open3d as o3d


# Create the PointCloudProcessor class, which groups related code together.
class PointCloudProcessor:


    # Create the setup function that runs when this object is made.
    def __init__(self, config):
        # Save this value inside the object for later.
        self.config = config

    # Create the load scan function.
    def load_scan(self):
        # Check this condition before choosing what happens next.
        if not os.path.exists(self.config.SCAN_FILE):
            # Stop the program because an important file or folder is missing.
            raise FileNotFoundError(
                # Run this line as one small step in the program.
                f"Scan file was not found: {self.config.SCAN_FILE}"
            )

        # Load a point cloud file so the program can use the scanned dots.
        scan = o3d.io.read_point_cloud(self.config.SCAN_FILE)

        # Count how many points are inside this object.
        if len(scan.points) == 0:
            # Stop the program and show a clear error message.
            raise Exception(
                # Run this line as one small step in the program.
                f"Scan point cloud is empty or could not be read: "
                # Run this line as one small step in the program.
                f"{self.config.SCAN_FILE}"
            )

        # Show helpful information on the screen.
        print("")
        # Show helpful information on the screen.
        print("Loaded scan file:", self.config.SCAN_FILE)
        # Count how many points are inside this object.
        print("Raw scan points:", len(scan.points))
        # Round the numbers so they are easier to read.
        print("Raw scan min bound:", np.round(scan.get_min_bound(), 4))
        # Round the numbers so they are easier to read.
        print("Raw scan max bound:", np.round(scan.get_max_bound(), 4))

        # Save a value in scan.
        scan = self.crop_scan(scan)

        # Send this result back to the part of the code that asked for it.
        return scan

    # Create the load cad as point cloud function.
    def load_cad_as_point_cloud(self):
        # Check this condition before choosing what happens next.
        if not os.path.exists(self.config.CAD_FILE):
            # Stop the program because an important file or folder is missing.
            raise FileNotFoundError(
                # Run this line as one small step in the program.
                f"CAD file was not found: {self.config.CAD_FILE}"
            )

        # Load the CAD/STL mesh so the program can compare it with the scan.
        cad_mesh = o3d.io.read_triangle_mesh(self.config.CAD_FILE)

        # Check if the loaded CAD model has no usable shape.
        if cad_mesh.is_empty():
            # Stop the program and show a clear error message.
            raise Exception(
                # Run this line as one small step in the program.
                f"CAD mesh is empty or could not be read: "
                # Run this line as one small step in the program.
                f"{self.config.CAD_FILE}"
            )

        # Show helpful information on the screen.
        print("")
        # Show helpful information on the screen.
        print("Loaded CAD file:", self.config.CAD_FILE)
        # Round the numbers so they are easier to read.
        print("CAD mesh min bound before scale:", np.round(cad_mesh.get_min_bound(), 4))
        # Round the numbers so they are easier to read.
        print("CAD mesh max bound before scale:", np.round(cad_mesh.get_max_bound(), 4))

        # Resize the 3D object.
        cad_mesh.scale(
            # Add this value to the current group.
            self.config.CAD_SCALE,
            # Save a value in center.
            center=(0.0, 0.0, 0.0)
        )

        # Show helpful information on the screen.
        print("CAD scale applied:", self.config.CAD_SCALE)
        # Round the numbers so they are easier to read.
        print("CAD mesh min bound after scale:", np.round(cad_mesh.get_min_bound(), 4))
        # Round the numbers so they are easier to read.
        print("CAD mesh max bound after scale:", np.round(cad_mesh.get_max_bound(), 4))

        # Save a value in cad mesh.
        cad_mesh = self.apply_extra_cad_rotation(cad_mesh)

        # Prepare the CAD surface so it displays correctly.
        cad_mesh.compute_vertex_normals()

        # Turn the CAD surface into many small points.
        cad_point_cloud = cad_mesh.sample_points_uniformly(
            # Save a value in number of points.
            number_of_points=self.config.CAD_SAMPLE_POINTS
        )

        # Count how many points are inside this object.
        print("CAD sampled points:", len(cad_point_cloud.points))
        # Round the numbers so they are easier to read.
        print("CAD point cloud min bound:", np.round(cad_point_cloud.get_min_bound(), 4))
        # Round the numbers so they are easier to read.
        print("CAD point cloud max bound:", np.round(cad_point_cloud.get_max_bound(), 4))

        # Send this result back to the part of the code that asked for it.
        return cad_point_cloud

    # Create the apply extra cad rotation function.
    def apply_extra_cad_rotation(self, cad_mesh):
        # Save a value in rx.
        rx = np.radians(self.config.CAD_EXTRA_RX_DEG)
        # Save a value in ry.
        ry = np.radians(self.config.CAD_EXTRA_RY_DEG)
        # Save a value in rz.
        rz = np.radians(self.config.CAD_EXTRA_RZ_DEG)

        # Save a value in rotation matrix.
        rotation_matrix = cad_mesh.get_rotation_matrix_from_xyz(
            # Start a group of values.
            (rx, ry, rz)
        )

        # Save a value in cad center.
        cad_center = cad_mesh.get_center()

        # Rotate the CAD model around its center.
        cad_mesh.rotate(
            # Add this value to the current group.
            rotation_matrix,
            # Save a value in center.
            center=cad_center
        )

        # Show helpful information on the screen.
        print("")
        # Show helpful information on the screen.
        print("Extra CAD rotation applied:")
        # Show helpful information on the screen.
        print("  RX:", self.config.CAD_EXTRA_RX_DEG, "degrees")
        # Show helpful information on the screen.
        print("  RY:", self.config.CAD_EXTRA_RY_DEG, "degrees")
        # Show helpful information on the screen.
        print("  RZ:", self.config.CAD_EXTRA_RZ_DEG, "degrees")
        # Round the numbers so they are easier to read.
        print("CAD mesh min bound after rotation:", np.round(cad_mesh.get_min_bound(), 4))
        # Round the numbers so they are easier to read.
        print("CAD mesh max bound after rotation:", np.round(cad_mesh.get_max_bound(), 4))

        # Send this result back to the part of the code that asked for it.
        return cad_mesh

    # Create the preprocess function.
    def preprocess(self, point_cloud):
        # Show helpful information on the screen.
        print("")
        # Show helpful information on the screen.
        print("Preprocessing point cloud...")
        # Count how many points are inside this object.
        print("Input points:", len(point_cloud.points))

        # Make the point cloud lighter by merging nearby points.
        point_cloud = point_cloud.voxel_down_sample(self.config.VOXEL_SIZE)

        # Count how many points are inside this object.
        print("Points after voxel downsample:", len(point_cloud.points))

        # Count how many points are inside this object.
        if self.config.REMOVE_OUTLIERS and len(point_cloud.points) > 0:
            # Count how many points are inside this object.
            before_outlier_removal = len(point_cloud.points)

            # Remove points that look like random noise.
            point_cloud, _ = point_cloud.remove_statistical_outlier(
                # Save a value in nb neighbors.
                nb_neighbors=self.config.OUTLIER_NB,
                # Save a value in std ratio.
                std_ratio=self.config.OUTLIER_STD
            )

            # Count how many points are inside this object.
            removed_points = before_outlier_removal - len(point_cloud.points)

            # Show helpful information on the screen.
            print("Outlier removal enabled.")
            # Show helpful information on the screen.
            print("Removed outlier points:", removed_points)
            # Count how many points are inside this object.
            print("Points after outlier removal:", len(point_cloud.points))
        # Use this path when the earlier checks were false.
        else:
            # Show helpful information on the screen.
            print("Outlier removal disabled. Keeping downsampled raw points.")

        # Count how many points are inside this object.
        if len(point_cloud.points) == 0:
            # Stop the program and show a clear error message.
            raise Exception("Point cloud became empty after preprocessing.")

        # Calculate which way the surface points are facing.
        point_cloud.estimate_normals(
            # Save a value in search param.
            search_param=o3d.geometry.KDTreeSearchParamHybrid(
                # Save a value in radius.
                radius=self.config.VOXEL_SIZE * 2.0,
                # Save a value in max nn.
                max_nn=30
            )
        )

        # Round the numbers so they are easier to read.
        print("Preprocessed min bound:", np.round(point_cloud.get_min_bound(), 4))
        # Round the numbers so they are easier to read.
        print("Preprocessed max bound:", np.round(point_cloud.get_max_bound(), 4))

        # Send this result back to the part of the code that asked for it.
        return point_cloud

    # Create the crop scan function.
    def crop_scan(self, scan):
        # Check this condition before choosing what happens next.
        if not self.config.USE_CROP:
            # Show helpful information on the screen.
            print("Manual crop disabled. Keeping full scan.")
            # Send this result back to the part of the code that asked for it.
            return scan

        # Save a value in bounding box.
        bounding_box = o3d.geometry.AxisAlignedBoundingBox(
            # Put these numbers into a NumPy array.
            min_bound=np.array(self.config.CROP_MIN, dtype=np.float64),
            # Put these numbers into a NumPy array.
            max_bound=np.array(self.config.CROP_MAX, dtype=np.float64)
        )

        # Save a value in cropped scan.
        cropped_scan = scan.crop(bounding_box)

        # Count how many points are inside this object.
        if len(cropped_scan.points) == 0:
            # Stop the program and show a clear error message.
            raise Exception("Cropped scan is empty. Adjust crop bounds.")

        # Show helpful information on the screen.
        print("Manual crop enabled.")
        # Count how many points are inside this object.
        print("Cropped scan points:", len(cropped_scan.points))
        # Round the numbers so they are easier to read.
        print("Cropped scan min bound:", np.round(cropped_scan.get_min_bound(), 4))
        # Round the numbers so they are easier to read.
        print("Cropped scan max bound:", np.round(cropped_scan.get_max_bound(), 4))

        # Send this result back to the part of the code that asked for it.
        return cropped_scan
