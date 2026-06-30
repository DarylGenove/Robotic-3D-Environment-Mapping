# Use Open3D to read, write, and change 3D files.
import open3d as o3d


# Create the CadExporter class to group related code together.
class CadExporter:
    # Set up this object when it is created.
    def __init__(self, point_cloud_scaler):
        # Save this value inside the object as point_cloud_scaler.
        self.point_cloud_scaler = point_cloud_scaler

    # Create the save_scaled_cad_stl function.
    def save_scaled_cad_stl(self, input_file, output_file):
        # Show a message on the screen.
        print("")
        # Show a message on the screen.
        print("Loading aligned CAD STL:")
        # Show a message on the screen.
        print(input_file)

        # Read a 3D mesh file from the computer.
        cad_mesh = o3d.io.read_triangle_mesh(str(input_file))

        # Check if this condition is true.
        if cad_mesh.is_empty():
            # Stop the program and show a clear problem message.
            raise Exception("Aligned CAD STL is empty.")

        # Calculate surface directions so the 3D model displays better.
        cad_mesh.compute_vertex_normals()

        # Store the 3D mesh in cad_mesh.
        cad_mesh = self.point_cloud_scaler.scale_mesh_from_meters_to_millimeters(
            # This line helps the program do the next small step.
            cad_mesh
        )

        # Save a 3D mesh file to the computer.
        o3d.io.write_triangle_mesh(
            # Call this function to do one job.
            str(output_file),
            # This line helps the program do the next small step.
            cad_mesh
        )

        # Show a message on the screen.
        print("")
        # Show a message on the screen.
        print("Saved RoboDK CAD STL:")
        # Show a message on the screen.
        print(output_file)
