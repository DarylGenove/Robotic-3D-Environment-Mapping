# Bring in needed tools from pathlib.
from pathlib import Path

# Bring in numpy so this file can use it.
import numpy as np
# Bring in open3d so this file can use it.
import open3d as o3d


# Set the EXPORT_FOLDER setting.
EXPORT_FOLDER = Path(
    # Run this line as one small step in the program.
    r"C:/Users/daryl/Desktop/Robotic D Environment Mapping/"
    # Run this line as one small step in the program.
    r"Robotic-3D-Environment-Mapping/RoboDK Export"
)

# Set the CLEANED_SCAN_PCD setting.
CLEANED_SCAN_PCD = EXPORT_FOLDER / "02_scan_cleaned_inside_stl_range_ROBODK.pcd"
# Set the ALIGNED_CAD_STL setting.
ALIGNED_CAD_STL = EXPORT_FOLDER / "04_aligned_cabinet_ROBODK.stl"

# Set the COLORED_SCAN_PLY_FOR_ROBODK setting.
COLORED_SCAN_PLY_FOR_ROBODK = (
    # Run this line as one small step in the program.
    EXPORT_FOLDER / "02_scan_cleaned_inside_stl_range_ROBODK_MM_COLORED.ply"
)

# Set the COLORED_SCAN_OBJ_FOR_ROBODK setting.
COLORED_SCAN_OBJ_FOR_ROBODK = (
    # Run this line as one small step in the program.
    EXPORT_FOLDER / "02_scan_cleaned_inside_stl_range_ROBODK_MM_COLORED.obj"
)

# Set the COLORED_SCAN_MTL_FOR_ROBODK setting.
COLORED_SCAN_MTL_FOR_ROBODK = (
    # Run this line as one small step in the program.
    EXPORT_FOLDER / "02_scan_cleaned_inside_stl_range_ROBODK_MM_COLORED.mtl"
)

# Set the CAD_STL_FOR_ROBODK setting.
CAD_STL_FOR_ROBODK = EXPORT_FOLDER / "04_aligned_cabinet_ROBODK_MM.stl"

# Set the VOXEL_SIZE_M setting.
VOXEL_SIZE_M = 0.01
# Set the COLOR_LEVELS setting.
COLOR_LEVELS = 12


# Create the scale point cloud from meters to millimeters function.
def scale_point_cloud_from_meters_to_millimeters(point_cloud):
    # Save a value in scaled point cloud.
    scaled_point_cloud = o3d.geometry.PointCloud(point_cloud)

    # Resize the 3D object.
    scaled_point_cloud.scale(
        # Add this value to the current group.
        1000.0,
        # Save a value in center.
        center=(0.0, 0.0, 0.0)
    )

    # Send this result back to the part of the code that asked for it.
    return scaled_point_cloud


# Create the scale mesh from meters to millimeters function.
def scale_mesh_from_meters_to_millimeters(mesh):
    # Resize the 3D object.
    mesh.scale(
        # Add this value to the current group.
        1000.0,
        # Save a value in center.
        center=(0.0, 0.0, 0.0)
    )

    # Send this result back to the part of the code that asked for it.
    return mesh


# Create the quantize color function.
def quantize_color(color, levels=12):
    # Save a value in color.
    color = np.clip(color, 0.0, 1.0)

    # Round the numbers so they are easier to read.
    quantized_color = np.round(color * (levels - 1)) / (levels - 1)

    # Send this result back to the part of the code that asked for it.
    return tuple(quantized_color.tolist())


# Create the create material name function.
def create_material_name(material_index):
    # Send this result back to the part of the code that asked for it.
    return f"scan_color_{material_index:04d}"


# Create the write colored voxel obj function.
def write_colored_voxel_obj(
    # Add this value to the current group.
    point_cloud,
    # Add this value to the current group.
    obj_file,
    # Add this value to the current group.
    mtl_file,
    # Save a value in voxel size m.
    voxel_size_m=0.01,
    # Save a value in color levels.
    color_levels=12
# Run this line as one small step in the program.
):
    # Count how many points are inside this object.
    if len(point_cloud.points) == 0:
        # Stop the program and show a clear error message.
        raise Exception("Point cloud is empty.")

    # Check this condition before choosing what happens next.
    if not point_cloud.has_colors():
        # Stop the program and show a clear error message.
        raise Exception(
            # Run this line as one small step in the program.
            "The cleaned scan PCD does not contain color data. "
            # Run this line as one small step in the program.
            "The color was already lost before this conversion step."
        )

    # Make the point cloud lighter by merging nearby points.
    point_cloud = point_cloud.voxel_down_sample(voxel_size_m)

    # Count how many points are inside this object.
    if len(point_cloud.points) == 0:
        # Stop the program and show a clear error message.
        raise Exception("Point cloud became empty after voxel downsampling.")

    # Check this condition before choosing what happens next.
    if not point_cloud.has_colors():
        # Stop the program and show a clear error message.
        raise Exception("Point cloud lost color after voxel downsampling.")

    # Change the Open3D points into NumPy numbers.
    points = np.asarray(point_cloud.points)
    # Change the Open3D points into NumPy numbers.
    colors = np.asarray(point_cloud.colors)

    # Save a value in voxel size mm.
    voxel_size_mm = voxel_size_m * 1000.0
    # Save a value in half size mm.
    half_size_mm = voxel_size_mm / 2.0

    # Put these numbers into a NumPy array.
    cube_offsets = np.array(
        # Start a group of values.
        [
            # Start a group of values.
            [-half_size_mm, -half_size_mm, -half_size_mm],
            # Start a group of values.
            [half_size_mm, -half_size_mm, -half_size_mm],
            # Start a group of values.
            [half_size_mm, half_size_mm, -half_size_mm],
            # Start a group of values.
            [-half_size_mm, half_size_mm, -half_size_mm],
            # Start a group of values.
            [-half_size_mm, -half_size_mm, half_size_mm],
            # Start a group of values.
            [half_size_mm, -half_size_mm, half_size_mm],
            # Start a group of values.
            [half_size_mm, half_size_mm, half_size_mm],
            # Start a group of values.
            [-half_size_mm, half_size_mm, half_size_mm],
        ],
        # Save a value in dtype.
        dtype=np.float64
    )

    # Save a value in cube faces.
    cube_faces = [
        # Start a group of values.
        [1, 2, 3, 4],
        # Start a group of values.
        [5, 8, 7, 6],
        # Start a group of values.
        [1, 5, 6, 2],
        # Start a group of values.
        [2, 6, 7, 3],
        # Start a group of values.
        [3, 7, 8, 4],
        # Start a group of values.
        [4, 8, 5, 1],
    ]

    # Save a value in material by color.
    material_by_color = {}
    # Save a value in material lines.
    material_lines = []
    # Save a value in obj lines.
    obj_lines = []

    # Add this item to the list.
    obj_lines.append(f"mtllib {mtl_file.name}")
    # Add this item to the list.
    obj_lines.append("o Colored_Cleaned_Scan")

    # Save a value in vertex index.
    vertex_index = 1

    # Repeat this code for every item in the group.
    for point, color in zip(points, colors):
        # Save a value in point mm.
        point_mm = point * 1000.0
        # Save a value in quantized color.
        quantized_color = quantize_color(color, levels=color_levels)

        # Check this condition before choosing what happens next.
        if quantized_color not in material_by_color:
            # Save a value in material name.
            material_name = create_material_name(len(material_by_color))
            # Save a value in material by color[quantized color].
            material_by_color[quantized_color] = material_name

            # Save several results into separate variable names.
            red, green, blue = quantized_color

            # Add this item to the list.
            material_lines.append(f"newmtl {material_name}")
            # Add this item to the list.
            material_lines.append(f"Ka {red:.6f} {green:.6f} {blue:.6f}")
            # Add this item to the list.
            material_lines.append(f"Kd {red:.6f} {green:.6f} {blue:.6f}")
            # Add this item to the list.
            material_lines.append("Ks 0.000000 0.000000 0.000000")
            # Add this item to the list.
            material_lines.append("Ns 10.000000")
            # Add this item to the list.
            material_lines.append("d 1.000000")
            # Add this item to the list.
            material_lines.append("illum 1")
            # Add this item to the list.
            material_lines.append("")

        # Save a value in material name.
        material_name = material_by_color[quantized_color]

        # Repeat this code for every item in the group.
        for offset in cube_offsets:
            # Save a value in vertex.
            vertex = point_mm + offset

            # Add this item to the list.
            obj_lines.append(
                # Run this line as one small step in the program.
                f"v {vertex[0]:.6f} {vertex[1]:.6f} {vertex[2]:.6f}"
            )

        # Add this item to the list.
        obj_lines.append(f"usemtl {material_name}")

        # Repeat this code for every item in the group.
        for face in cube_faces:
            # Save a value in face indices.
            face_indices = [
                # Run this line as one small step in the program.
                vertex_index + local_index - 1
                # Repeat this code for every item in the group.
                for local_index in face
            ]

            # Add this item to the list.
            obj_lines.append(
                # Run this line as one small step in the program.
                "f " + " ".join(str(face_index) for face_index in face_indices)
            )

        # Save a value in vertex index +.
        vertex_index += 8

    # Write text into an output file.
    obj_file.write_text("\n".join(obj_lines), encoding="utf-8")
    # Write text into an output file.
    mtl_file.write_text("\n".join(material_lines), encoding="utf-8")

    # Count how many points are inside this object.
    print("OBJ voxel points used:", len(points))
    # Show helpful information on the screen.
    print("OBJ material count:", len(material_by_color))


# Create the save colored point cloud ply function.
def save_colored_point_cloud_ply(point_cloud, output_file):
    # Count how many points are inside this object.
    if len(point_cloud.points) == 0:
        # Stop the program and show a clear error message.
        raise Exception("Point cloud is empty.")

    # Check this condition before choosing what happens next.
    if not point_cloud.has_colors():
        # Stop the program and show a clear error message.
        raise Exception(
            # Run this line as one small step in the program.
            "The cleaned scan PCD does not contain color data. "
            # Run this line as one small step in the program.
            "Cannot save colored PLY."
        )

    # Save a value in scaled point cloud.
    scaled_point_cloud = scale_point_cloud_from_meters_to_millimeters(point_cloud)

    # Save a point cloud file to the computer.
    o3d.io.write_point_cloud(
        # Add this value to the current group.
        str(output_file),
        # Add this value to the current group.
        scaled_point_cloud,
        # Save a value in write ascii.
        write_ascii=False,
        # Save a value in compressed.
        compressed=False
    )

    # Load a point cloud file so the program can use the scanned dots.
    test_point_cloud = o3d.io.read_point_cloud(str(output_file))

    # Show helpful information on the screen.
    print("")
    # Show helpful information on the screen.
    print("Saved colored PLY point cloud:")
    # Show helpful information on the screen.
    print(output_file)
    # Count how many points are inside this object.
    print("PLY points:", len(test_point_cloud.points))
    # Show helpful information on the screen.
    print("PLY has colors:", test_point_cloud.has_colors())


# Create the save scaled cad stl function.
def save_scaled_cad_stl(input_file, output_file):
    # Load the CAD/STL mesh so the program can compare it with the scan.
    cad_mesh = o3d.io.read_triangle_mesh(str(input_file))

    # Check if the loaded CAD model has no usable shape.
    if cad_mesh.is_empty():
        # Stop the program and show a clear error message.
        raise Exception("Aligned CAD STL is empty.")

    # Prepare the CAD surface so it displays correctly.
    cad_mesh.compute_vertex_normals()
    # Save a value in cad mesh.
    cad_mesh = scale_mesh_from_meters_to_millimeters(cad_mesh)

    # Save a mesh file to the computer.
    o3d.io.write_triangle_mesh(
        # Add this value to the current group.
        str(output_file),
        # Run this line as one small step in the program.
        cad_mesh
    )

    # Show helpful information on the screen.
    print("")
    # Show helpful information on the screen.
    print("Saved RoboDK CAD STL:")
    # Show helpful information on the screen.
    print(output_file)


# Create the main function that starts the program.
def main():
    # Create this folder if it is missing.
    EXPORT_FOLDER.mkdir(parents=True, exist_ok=True)

    # Check this condition before choosing what happens next.
    if not CLEANED_SCAN_PCD.exists():
        # Stop the program because an important file or folder is missing.
        raise FileNotFoundError(
            # Run this line as one small step in the program.
            f"Cleaned scan PCD not found: {CLEANED_SCAN_PCD}"
        )

    # Check this condition before choosing what happens next.
    if not ALIGNED_CAD_STL.exists():
        # Stop the program because an important file or folder is missing.
        raise FileNotFoundError(
            # Run this line as one small step in the program.
            f"Aligned CAD STL not found: {ALIGNED_CAD_STL}"
        )

    # Show helpful information on the screen.
    print("")
    # Show helpful information on the screen.
    print("=" * 70)
    # Show helpful information on the screen.
    print("CONVERTING COLORED PCD AND CAD FILES FOR ROBODK")
    # Show helpful information on the screen.
    print("=" * 70)
    # Show helpful information on the screen.
    print("")

    # Show helpful information on the screen.
    print("Loading cleaned scan PCD:")
    # Show helpful information on the screen.
    print(CLEANED_SCAN_PCD)

    # Load a point cloud file so the program can use the scanned dots.
    scan_pcd = o3d.io.read_point_cloud(str(CLEANED_SCAN_PCD))

    # Count how many points are inside this object.
    if len(scan_pcd.points) == 0:
        # Stop the program and show a clear error message.
        raise Exception("Cleaned scan PCD is empty.")

    # Count how many points are inside this object.
    print("Scan points:", len(scan_pcd.points))
    # Show helpful information on the screen.
    print("Scan has colors:", scan_pcd.has_colors())
    # Show helpful information on the screen.
    print("Scan color count:", len(scan_pcd.colors))

    # Check this condition before choosing what happens next.
    if not scan_pcd.has_colors():
        # Stop the program and show a clear error message.
        raise Exception(
            # Run this line as one small step in the program.
            "The cleaned scan PCD has no RGB color data. "
            # Run this line as one small step in the program.
            "Fix the RealSense/Open3D scanning export first."
        )

    # Show helpful information on the screen.
    print("")
    # Show helpful information on the screen.
    print("Saving colored PLY point cloud for RoboDK...")
    # Run this line as one small step in the program.
    save_colored_point_cloud_ply(
        # Add this value to the current group.
        scan_pcd,
        # Run this line as one small step in the program.
        COLORED_SCAN_PLY_FOR_ROBODK
    )

    # Show helpful information on the screen.
    print("")
    # Show helpful information on the screen.
    print("Writing colored OBJ/MTL voxel mesh for RoboDK...")
    # Show helpful information on the screen.
    print("This file is more likely to preserve visible color in RoboDK.")

    # Run this line as one small step in the program.
    write_colored_voxel_obj(
        # Add this value to the current group.
        scan_pcd,
        # Add this value to the current group.
        COLORED_SCAN_OBJ_FOR_ROBODK,
        # Add this value to the current group.
        COLORED_SCAN_MTL_FOR_ROBODK,
        # Save a value in voxel size m.
        voxel_size_m=VOXEL_SIZE_M,
        # Save a value in color levels.
        color_levels=COLOR_LEVELS
    )

    # Show helpful information on the screen.
    print("")
    # Show helpful information on the screen.
    print("Saved colored RoboDK scan OBJ:")
    # Show helpful information on the screen.
    print(COLORED_SCAN_OBJ_FOR_ROBODK)

    # Show helpful information on the screen.
    print("Saved colored RoboDK scan MTL:")
    # Show helpful information on the screen.
    print(COLORED_SCAN_MTL_FOR_ROBODK)

    # Show helpful information on the screen.
    print("")
    # Show helpful information on the screen.
    print("Loading aligned CAD STL:")
    # Show helpful information on the screen.
    print(ALIGNED_CAD_STL)

    # Run this line as one small step in the program.
    save_scaled_cad_stl(
        # Add this value to the current group.
        ALIGNED_CAD_STL,
        # Run this line as one small step in the program.
        CAD_STL_FOR_ROBODK
    )

    # Show helpful information on the screen.
    print("")
    # Show helpful information on the screen.
    print("=" * 70)
    # Show helpful information on the screen.
    print("DONE")
    # Show helpful information on the screen.
    print("=" * 70)
    # Show helpful information on the screen.
    print("Import these files into RoboDK:")
    # Show helpful information on the screen.
    print("")
    # Show helpful information on the screen.
    print("Best option for visible colors:")
    # Show helpful information on the screen.
    print(COLORED_SCAN_OBJ_FOR_ROBODK)
    # Show helpful information on the screen.
    print("")
    # Show helpful information on the screen.
    print("Backup option:")
    # Show helpful information on the screen.
    print(COLORED_SCAN_PLY_FOR_ROBODK)
    # Show helpful information on the screen.
    print("")
    # Show helpful information on the screen.
    print("CAD file:")
    # Show helpful information on the screen.
    print(CAD_STL_FOR_ROBODK)
    # Show helpful information on the screen.
    print("")
    # Show helpful information on the screen.
    print("Important:")
    # Show helpful information on the screen.
    print("Keep the OBJ and MTL files in the same folder.")


# Only start the program automatically when this file is run directly.
if __name__ == "__main__":
    # Run this line as one small step in the program.
    main()
