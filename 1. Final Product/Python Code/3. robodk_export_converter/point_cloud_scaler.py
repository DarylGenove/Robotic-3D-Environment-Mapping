import open3d as o3d


class PointCloudScaler:
    def scale_point_cloud_from_meters_to_millimeters(self, point_cloud):
        scaled_point_cloud = o3d.geometry.PointCloud(point_cloud)

        scaled_point_cloud.scale(
            1000.0,
            center=(0.0, 0.0, 0.0)
        )

        return scaled_point_cloud

    def scale_mesh_from_meters_to_millimeters(self, mesh):
        mesh.scale(
            1000.0,
            center=(0.0, 0.0, 0.0)
        )

        return mesh
