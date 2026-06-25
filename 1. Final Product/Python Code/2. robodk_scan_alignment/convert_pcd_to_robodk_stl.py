from pathlib import Path

import numpy as np
import open3d as o3d


EXPORT_FOLDER = Path(
    r"C:/Users/daryl/Desktop/Robotic D Environment Mapping/"
    r"Robotic-3D-Environment-Mapping/RoboDK Export"
)

CLEANED_SCAN_PCD = EXPORT_FOLDER / "02_scan_cleaned_inside_stl_range_ROBODK.pcd"
ALIGNED_CAD_STL = EXPORT_FOLDER / "04_aligned_cabinet_ROBODK.stl"

COLORED_SCAN_PLY_FOR_ROBODK = (
    EXPORT_FOLDER / "02_scan_cleaned_inside_stl_range_ROBODK_MM_COLORED.ply"
)

COLORED_SCAN_OBJ_FOR_ROBODK = (
    EXPORT_FOLDER / "02_scan_cleaned_inside_stl_range_ROBODK_MM_COLORED.obj"
)

COLORED_SCAN_MTL_FOR_ROBODK = (
    EXPORT_FOLDER / "02_scan_cleaned_inside_stl_range_ROBODK_MM_COLORED.mtl"
)

CAD_STL_FOR_ROBODK = EXPORT_FOLDER / "04_aligned_cabinet_ROBODK_MM.stl"

VOXEL_SIZE_M = 0.01
COLOR_LEVELS = 12


def scale_point_cloud_from_meters_to_millimeters(point_cloud):
    scaled_point_cloud = o3d.geometry.PointCloud(point_cloud)

    scaled_point_cloud.scale(
        1000.0,
        center=(0.0, 0.0, 0.0)
    )

    return scaled_point_cloud


def scale_mesh_from_meters_to_millimeters(mesh):
    mesh.scale(
        1000.0,
        center=(0.0, 0.0, 0.0)
    )

    return mesh


def quantize_color(color, levels=12):
    color = np.clip(color, 0.0, 1.0)

    quantized_color = np.round(color * (levels - 1)) / (levels - 1)

    return tuple(quantized_color.tolist())


def create_material_name(material_index):
    return f"scan_color_{material_index:04d}"


def write_colored_voxel_obj(
    point_cloud,
    obj_file,
    mtl_file,
    voxel_size_m=0.01,
    color_levels=12
):
    if len(point_cloud.points) == 0:
        raise Exception("Point cloud is empty.")

    if not point_cloud.has_colors():
        raise Exception(
            "The cleaned scan PCD does not contain color data. "
            "The color was already lost before this conversion step."
        )

    point_cloud = point_cloud.voxel_down_sample(voxel_size_m)

    if len(point_cloud.points) == 0:
        raise Exception("Point cloud became empty after voxel downsampling.")

    if not point_cloud.has_colors():
        raise Exception("Point cloud lost color after voxel downsampling.")

    points = np.asarray(point_cloud.points)
    colors = np.asarray(point_cloud.colors)

    voxel_size_mm = voxel_size_m * 1000.0
    half_size_mm = voxel_size_mm / 2.0

    cube_offsets = np.array(
        [
            [-half_size_mm, -half_size_mm, -half_size_mm],
            [half_size_mm, -half_size_mm, -half_size_mm],
            [half_size_mm, half_size_mm, -half_size_mm],
            [-half_size_mm, half_size_mm, -half_size_mm],
            [-half_size_mm, -half_size_mm, half_size_mm],
            [half_size_mm, -half_size_mm, half_size_mm],
            [half_size_mm, half_size_mm, half_size_mm],
            [-half_size_mm, half_size_mm, half_size_mm],
        ],
        dtype=np.float64
    )

    cube_faces = [
        [1, 2, 3, 4],
        [5, 8, 7, 6],
        [1, 5, 6, 2],
        [2, 6, 7, 3],
        [3, 7, 8, 4],
        [4, 8, 5, 1],
    ]

    material_by_color = {}
    material_lines = []
    obj_lines = []

    obj_lines.append(f"mtllib {mtl_file.name}")
    obj_lines.append("o Colored_Cleaned_Scan")

    vertex_index = 1

    for point, color in zip(points, colors):
        point_mm = point * 1000.0
        quantized_color = quantize_color(color, levels=color_levels)

        if quantized_color not in material_by_color:
            material_name = create_material_name(len(material_by_color))
            material_by_color[quantized_color] = material_name

            red, green, blue = quantized_color

            material_lines.append(f"newmtl {material_name}")
            material_lines.append(f"Ka {red:.6f} {green:.6f} {blue:.6f}")
            material_lines.append(f"Kd {red:.6f} {green:.6f} {blue:.6f}")
            material_lines.append("Ks 0.000000 0.000000 0.000000")
            material_lines.append("Ns 10.000000")
            material_lines.append("d 1.000000")
            material_lines.append("illum 1")
            material_lines.append("")

        material_name = material_by_color[quantized_color]

        for offset in cube_offsets:
            vertex = point_mm + offset

            obj_lines.append(
                f"v {vertex[0]:.6f} {vertex[1]:.6f} {vertex[2]:.6f}"
            )

        obj_lines.append(f"usemtl {material_name}")

        for face in cube_faces:
            face_indices = [
                vertex_index + local_index - 1
                for local_index in face
            ]

            obj_lines.append(
                "f " + " ".join(str(face_index) for face_index in face_indices)
            )

        vertex_index += 8

    obj_file.write_text("\n".join(obj_lines), encoding="utf-8")
    mtl_file.write_text("\n".join(material_lines), encoding="utf-8")

    print("OBJ voxel points used:", len(points))
    print("OBJ material count:", len(material_by_color))


def save_colored_point_cloud_ply(point_cloud, output_file):
    if len(point_cloud.points) == 0:
        raise Exception("Point cloud is empty.")

    if not point_cloud.has_colors():
        raise Exception(
            "The cleaned scan PCD does not contain color data. "
            "Cannot save colored PLY."
        )

    scaled_point_cloud = scale_point_cloud_from_meters_to_millimeters(point_cloud)

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


def save_scaled_cad_stl(input_file, output_file):
    cad_mesh = o3d.io.read_triangle_mesh(str(input_file))

    if cad_mesh.is_empty():
        raise Exception("Aligned CAD STL is empty.")

    cad_mesh.compute_vertex_normals()
    cad_mesh = scale_mesh_from_meters_to_millimeters(cad_mesh)

    o3d.io.write_triangle_mesh(
        str(output_file),
        cad_mesh
    )

    print("")
    print("Saved RoboDK CAD STL:")
    print(output_file)


def main():
    EXPORT_FOLDER.mkdir(parents=True, exist_ok=True)

    if not CLEANED_SCAN_PCD.exists():
        raise FileNotFoundError(
            f"Cleaned scan PCD not found: {CLEANED_SCAN_PCD}"
        )

    if not ALIGNED_CAD_STL.exists():
        raise FileNotFoundError(
            f"Aligned CAD STL not found: {ALIGNED_CAD_STL}"
        )

    print("")
    print("=" * 70)
    print("CONVERTING COLORED PCD AND CAD FILES FOR ROBODK")
    print("=" * 70)
    print("")

    print("Loading cleaned scan PCD:")
    print(CLEANED_SCAN_PCD)

    scan_pcd = o3d.io.read_point_cloud(str(CLEANED_SCAN_PCD))

    if len(scan_pcd.points) == 0:
        raise Exception("Cleaned scan PCD is empty.")

    print("Scan points:", len(scan_pcd.points))
    print("Scan has colors:", scan_pcd.has_colors())
    print("Scan color count:", len(scan_pcd.colors))

    if not scan_pcd.has_colors():
        raise Exception(
            "The cleaned scan PCD has no RGB color data. "
            "Fix the RealSense/Open3D scanning export first."
        )

    print("")
    print("Saving colored PLY point cloud for RoboDK...")
    save_colored_point_cloud_ply(
        scan_pcd,
        COLORED_SCAN_PLY_FOR_ROBODK
    )

    print("")
    print("Writing colored OBJ/MTL voxel mesh for RoboDK...")
    print("This file is more likely to preserve visible color in RoboDK.")

    write_colored_voxel_obj(
        scan_pcd,
        COLORED_SCAN_OBJ_FOR_ROBODK,
        COLORED_SCAN_MTL_FOR_ROBODK,
        voxel_size_m=VOXEL_SIZE_M,
        color_levels=COLOR_LEVELS
    )

    print("")
    print("Saved colored RoboDK scan OBJ:")
    print(COLORED_SCAN_OBJ_FOR_ROBODK)

    print("Saved colored RoboDK scan MTL:")
    print(COLORED_SCAN_MTL_FOR_ROBODK)

    print("")
    print("Loading aligned CAD STL:")
    print(ALIGNED_CAD_STL)

    save_scaled_cad_stl(
        ALIGNED_CAD_STL,
        CAD_STL_FOR_ROBODK
    )

    print("")
    print("=" * 70)
    print("DONE")
    print("=" * 70)
    print("Import these files into RoboDK:")
    print("")
    print("Best option for visible colors:")
    print(COLORED_SCAN_OBJ_FOR_ROBODK)
    print("")
    print("Backup option:")
    print(COLORED_SCAN_PLY_FOR_ROBODK)
    print("")
    print("CAD file:")
    print(CAD_STL_FOR_ROBODK)
    print("")
    print("Important:")
    print("Keep the OBJ and MTL files in the same folder.")


if __name__ == "__main__":
    main()