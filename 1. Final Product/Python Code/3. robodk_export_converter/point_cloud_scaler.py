# Use Open3D to read, write, and change 3D files.
import open3d as o3d


# Create the PointCloudScaler class to group related code together.
class PointCloudScaler:
    # Create the scale_point_cloud_from_meters_to_millimeters function.
    def scale_point_cloud_from_meters_to_millimeters(self, point_cloud):
        # Store the point cloud in scaled_point_cloud.
        scaled_point_cloud = o3d.geometry.PointCloud(point_cloud)

        # Change the size of the 3D object.
        scaled_point_cloud.scale(
            # Add this value to the list or function call.
            1000.0,
            # Store this value in center.
            center=(0.0, 0.0, 0.0)
        )

        # Give this value back to the code that asked for it.
        return scaled_point_cloud

    # Create the scale_mesh_from_meters_to_millimeters function.
    def scale_mesh_from_meters_to_millimeters(self, mesh):
        # Change the size of the 3D object.
        mesh.scale(
            # Add this value to the list or function call.
            1000.0,
            # Store this value in center.
            center=(0.0, 0.0, 0.0)
        )

        # Give this value back to the code that asked for it.
        return mesh
