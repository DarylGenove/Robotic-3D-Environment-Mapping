# Use Open3D to read, write, and change 3D files.
import open3d as o3d


# Create the ColoredScanExporter class to group related code together.
class ColoredScanExporter:
    # Set up this object when it is created.
    def __init__(self, point_cloud_scaler, colored_voxel_obj_writer):
        # Save this value inside the object as point_cloud_scaler.
        self.point_cloud_scaler = point_cloud_scaler
        # Save this value inside the object as colored_voxel_obj_writer.
        self.colored_voxel_obj_writer = colored_voxel_obj_writer

    # Create the load_colored_scan function.
    def load_colored_scan(self, input_file):
        # Show a message on the screen.
        print("Loading cleaned scan PCD:")
        # Show a message on the screen.
        print(input_file)

        # Read a point cloud file from the computer.
        point_cloud = o3d.io.read_point_cloud(str(input_file))

        # Check if this condition is true.
        if len(point_cloud.points) == 0:
            # Stop the program and show a clear problem message.
            raise Exception("Cleaned scan PCD is empty.")

        # Show a message on the screen.
        print("Scan points:", len(point_cloud.points))
        # Show a message on the screen.
        print("Scan has colors:", point_cloud.has_colors())
        # Show a message on the screen.
        print("Scan color count:", len(point_cloud.colors))

        # Check if this condition is true.
        if not point_cloud.has_colors():
            # Stop the program and show a clear problem message.
            raise Exception(
                # Add this text value.
                "The cleaned scan PCD has no RGB color data. "
                # Add this text value.
                "Fix the RealSense/Open3D scanning export first."
            )

        # Give this value back to the code that asked for it.
        return point_cloud

    # Create the save_colored_point_cloud_ply function.
    def save_colored_point_cloud_ply(self, point_cloud, output_file):
        # Check if this condition is true.
        if len(point_cloud.points) == 0:
            # Stop the program and show a clear problem message.
            raise Exception("Point cloud is empty.")

        # Check if this condition is true.
        if not point_cloud.has_colors():
            # Stop the program and show a clear problem message.
            raise Exception(
                # Add this text value.
                "The cleaned scan PCD does not contain color data. "
                # Add this text value.
                "Cannot save colored PLY."
            )

        # Store the point cloud in scaled_point_cloud.
        scaled_point_cloud = (
            # This line helps the program do the next small step.
            self.point_cloud_scaler.scale_point_cloud_from_meters_to_millimeters(
                # This line helps the program do the next small step.
                point_cloud
            )
        )

        # Save a point cloud file to the computer.
        o3d.io.write_point_cloud(
            # Call this function to do one job.
            str(output_file),
            # Add this value to the list or function call.
            scaled_point_cloud,
            # Store this value in write_ascii.
            write_ascii=False,
            # Store this value in compressed.
            compressed=False
        )

        # Read a point cloud file from the computer.
        test_point_cloud = o3d.io.read_point_cloud(str(output_file))

        # Show a message on the screen.
        print("")
        # Show a message on the screen.
        print("Saved colored PLY point cloud:")
        # Show a message on the screen.
        print(output_file)
        # Show a message on the screen.
        print("PLY points:", len(test_point_cloud.points))
        # Show a message on the screen.
        print("PLY has colors:", test_point_cloud.has_colors())

    # Create the save_colored_voxel_obj function.
    def save_colored_voxel_obj(
        # Add this value to the list or function call.
        self,
        # Add this value to the list or function call.
        point_cloud,
        # Add this value to the list or function call.
        obj_file,
        # Add this value to the list or function call.
        mtl_file,
        # Add this value to the list or function call.
        voxel_size_m,
        # This line helps the program do the next small step.
        color_levels
    # This line helps the program do the next small step.
    ):
        # Show a message on the screen.
        print("")
        # Show a message on the screen.
        print("Writing colored OBJ/MTL voxel mesh for RoboDK...")
        # Show a message on the screen.
        print("This file is more likely to preserve visible color in RoboDK.")

        # This line helps the program do the next small step.
        self.colored_voxel_obj_writer.write(
            # Add this value to the list or function call.
            point_cloud,
            # Add this value to the list or function call.
            obj_file,
            # Add this value to the list or function call.
            mtl_file,
            # Store this value in voxel_size_m.
            voxel_size_m=voxel_size_m,
            # Store this value in color_levels.
            color_levels=color_levels
        )

        # Show a message on the screen.
        print("")
        # Show a message on the screen.
        print("Saved colored RoboDK scan OBJ:")
        # Show a message on the screen.
        print(obj_file)

        # Show a message on the screen.
        print("Saved colored RoboDK scan MTL:")
        # Show a message on the screen.
        print(mtl_file)
