import open3d as o3d


class ColoredScanExporter:
    def __init__(self, point_cloud_scaler, colored_voxel_obj_writer):
        self.point_cloud_scaler = point_cloud_scaler
        self.colored_voxel_obj_writer = colored_voxel_obj_writer

    def load_colored_scan(self, input_file):
        print("Loading cleaned scan PCD:")
        print(input_file)

        point_cloud = o3d.io.read_point_cloud(str(input_file))

        if len(point_cloud.points) == 0:
            raise Exception("Cleaned scan PCD is empty.")

        print("Scan points:", len(point_cloud.points))
        print("Scan has colors:", point_cloud.has_colors())
        print("Scan color count:", len(point_cloud.colors))

        if not point_cloud.has_colors():
            raise Exception(
                "The cleaned scan PCD has no RGB color data. "
                "Fix the RealSense/Open3D scanning export first."
            )

        return point_cloud

    def save_colored_point_cloud_ply(self, point_cloud, output_file):
        if len(point_cloud.points) == 0:
            raise Exception("Point cloud is empty.")

        if not point_cloud.has_colors():
            raise Exception(
                "The cleaned scan PCD does not contain color data. "
                "Cannot save colored PLY."
            )

        scaled_point_cloud = (
            self.point_cloud_scaler.scale_point_cloud_from_meters_to_millimeters(
                point_cloud
            )
        )

        o3d.io.write_point_cloud(
            str(output_file),
            scaled_point_cloud,
            write_ascii=False,
            compressed=False
        )

        test_point_cloud = o3d.io.read_point_cloud(str(output_file))

        print("")
        print("Saved colored PLY point cloud:")
        print(output_file)
        print("PLY points:", len(test_point_cloud.points))
        print("PLY has colors:", test_point_cloud.has_colors())

    def save_colored_voxel_obj(
        self,
        point_cloud,
        obj_file,
        mtl_file,
        voxel_size_m,
        color_levels
    ):
        print("")
        print("Writing colored OBJ/MTL voxel mesh for RoboDK...")
        print("This file is more likely to preserve visible color in RoboDK.")

        self.colored_voxel_obj_writer.write(
            point_cloud,
            obj_file,
            mtl_file,
            voxel_size_m=voxel_size_m,
            color_levels=color_levels
        )

        print("")
        print("Saved colored RoboDK scan OBJ:")
        print(obj_file)

        print("Saved colored RoboDK scan MTL:")
        print(mtl_file)
