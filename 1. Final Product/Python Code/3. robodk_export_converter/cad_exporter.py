import open3d as o3d


class CadExporter:
    def __init__(self, point_cloud_scaler):
        self.point_cloud_scaler = point_cloud_scaler

    def save_scaled_cad_stl(self, input_file, output_file):
        print("")
        print("Loading aligned CAD STL:")
        print(input_file)

        cad_mesh = o3d.io.read_triangle_mesh(str(input_file))

        if cad_mesh.is_empty():
            raise Exception("Aligned CAD STL is empty.")

        cad_mesh.compute_vertex_normals()

        cad_mesh = self.point_cloud_scaler.scale_mesh_from_meters_to_millimeters(
            cad_mesh
        )

        o3d.io.write_triangle_mesh(
            str(output_file),
            cad_mesh
        )

        print("")
        print("Saved RoboDK CAD STL:")
        print(output_file)
