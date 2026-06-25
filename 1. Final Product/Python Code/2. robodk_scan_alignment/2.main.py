import copy
import sys
from pathlib import Path

PROJECT_FOLDER = Path(
    r"C:\Users\daryl\Desktop\Robotic D Environment Mapping\Robotic-3D-Environment-Mapping\1. Final Product\Python Code\2. robodk_scan_alignment"
)

CURRENT_FOLDER = Path(__file__).resolve().parent

if (PROJECT_FOLDER / "config.py").exists():
    sys.path.insert(0, str(PROJECT_FOLDER))
elif (CURRENT_FOLDER / "config.py").exists():
    sys.path.insert(0, str(CURRENT_FOLDER))
else:
    raise FileNotFoundError(
        "config.py was not found.\n\n"
        "RoboDK is running this script from Temp, so Python cannot find your other files.\n\n"
        "Fix this by changing PROJECT_FOLDER at the top of this file to the real folder that contains:\n"
        "- config.py\n"
        "- point_cloud_processor.py\n"
        "- plane_detector.py\n"
        "- scan_aligner.py\n"
        "- scan_filter.py\n"
        "- deviation_reporter.py\n"
        "- visualizer.py\n"
        "- edge_deviation_plotter.py\n\n"
        f"Current PROJECT_FOLDER:\n{PROJECT_FOLDER}\n\n"
        f"Current script folder:\n{CURRENT_FOLDER}"
    )

import numpy as np
import open3d as o3d

from config import Config
from point_cloud_processor import PointCloudProcessor
from plane_detector import PlaneDetector
from scan_aligner import ScanAligner
from scan_filter import ScanFilter
from deviation_reporter import DeviationReporter
from visualizer import Visualizer
from edge_deviation_plotter import EdgeDeviationPlotter


def print_cloud_extent(name, cloud):
    bounding_box = cloud.get_axis_aligned_bounding_box()

    print("")
    print("=" * 70)
    print(name)
    print("=" * 70)
    print("Min bound:", np.round(bounding_box.get_min_bound(), 4))
    print("Max bound:", np.round(bounding_box.get_max_bound(), 4))
    print("Center   :", np.round(bounding_box.get_center(), 4))
    print("Extent   :", np.round(bounding_box.get_extent(), 4))
    print("Points   :", len(cloud.points))


def colorize(point_cloud, color):
    colored_point_cloud = copy.deepcopy(point_cloud)
    colored_point_cloud.paint_uniform_color(color)
    return colored_point_cloud


def show_alignment_result(scan_cloud, cad_cloud, window_name):
    scan_colored = colorize(scan_cloud, [0.1, 0.7, 1.0])
    cad_colored = colorize(cad_cloud, [1.0, 0.0, 0.0])

    o3d.visualization.draw_geometries(
        [scan_colored, cad_colored],
        window_name=window_name
    )


def load_cad_mesh_for_export(config):
    cad_mesh = o3d.io.read_triangle_mesh(str(config.CAD_FILE))

    if cad_mesh.is_empty():
        raise Exception(f"CAD mesh is empty or could not be read: {config.CAD_FILE}")

    cad_mesh.scale(
        config.CAD_SCALE,
        center=(0.0, 0.0, 0.0)
    )

    rx = np.radians(config.CAD_EXTRA_RX_DEG)
    ry = np.radians(config.CAD_EXTRA_RY_DEG)
    rz = np.radians(config.CAD_EXTRA_RZ_DEG)

    rotation_matrix = cad_mesh.get_rotation_matrix_from_xyz(
        (rx, ry, rz)
    )

    cad_mesh.rotate(
        rotation_matrix,
        center=cad_mesh.get_center()
    )

    cad_mesh.compute_vertex_normals()

    return cad_mesh


def export_robot_base_files_for_robodk(
    config,
    scan_raw,
    scan_filtered,
    cad_final,
    cad_to_scan_transform
):
    export_folder = Path(
        r"C:/Users/daryl/Desktop/Robotic D Environment Mapping/"
        r"Robotic-3D-Environment-Mapping/RoboDK Export"
    )

    export_folder.mkdir(parents=True, exist_ok=True)

    raw_scan_robot_base_file = export_folder / "01_raw_merged_scan_robot_base.pcd"
    cleaned_scan_robot_base_file = export_folder / "02_scan_cleaned_inside_stl_range_ROBODK.pcd"
    aligned_cad_pcd_robot_base_file = export_folder / "03_aligned_cabinet_ROBODK.pcd"
    aligned_cad_stl_robot_base_file = export_folder / "04_aligned_cabinet_ROBODK.stl"
    cad_to_robot_base_transform_file = export_folder / "05_cad_to_robot_base_transform.txt"

    cad_mesh_robot_base = load_cad_mesh_for_export(config)
    cad_mesh_robot_base.transform(cad_to_scan_transform)
    cad_mesh_robot_base.compute_vertex_normals()

    o3d.io.write_point_cloud(
        str(raw_scan_robot_base_file),
        scan_raw
    )

    o3d.io.write_point_cloud(
        str(cleaned_scan_robot_base_file),
        scan_filtered
    )

    o3d.io.write_point_cloud(
        str(aligned_cad_pcd_robot_base_file),
        cad_final
    )

    o3d.io.write_triangle_mesh(
        str(aligned_cad_stl_robot_base_file),
        cad_mesh_robot_base
    )

    np.savetxt(
        str(cad_to_robot_base_transform_file),
        cad_to_scan_transform,
        fmt="%.10f"
    )

    print("")
    print("=" * 70)
    print("ROBOT BASE EXPORT FOR ROBODK")
    print("=" * 70)
    print("Raw merged scan:")
    print(raw_scan_robot_base_file)
    print("")
    print("Cleaned scan in robot base frame:")
    print(cleaned_scan_robot_base_file)
    print("")
    print("Aligned CAD point cloud in robot base frame:")
    print(aligned_cad_pcd_robot_base_file)
    print("")
    print("Aligned cabinet STL in robot base frame:")
    print(aligned_cad_stl_robot_base_file)
    print("")
    print("CAD-to-robot-base transform:")
    print(cad_to_robot_base_transform_file)
    print("")
    print(cad_to_scan_transform)
    print("=" * 70)


def main():
    config = Config()

    processor = PointCloudProcessor(config)
    plane_detector = PlaneDetector(config)
    aligner = ScanAligner(config, plane_detector)
    scan_filter = ScanFilter(config)
    deviation_reporter = DeviationReporter(plane_detector)
    visualizer = Visualizer()
    edge_plotter = EdgeDeviationPlotter(scale_to_mm=True)

    scan_raw = processor.load_scan()

    print_cloud_extent(
        "Step 1 - Raw Scan Loaded From PCD",
        scan_raw
    )

    o3d.visualization.draw_geometries(
        [scan_raw],
        window_name="Step 1 - Raw Scan Loaded From PCD"
    )

    scan_down = processor.preprocess(scan_raw)

    print_cloud_extent(
        "Step 2 - Scan After Light Preprocessing",
        scan_down
    )

    o3d.visualization.draw_geometries(
        [scan_down],
        window_name="Step 2 - Scan After Light Preprocessing"
    )

    cad_raw = processor.load_cad_as_point_cloud()

    print_cloud_extent(
        "Step 3 - CAD After Scale",
        cad_raw
    )

    o3d.visualization.draw_geometries(
        [cad_raw],
        window_name="Step 3 - CAD After Scale"
    )

    cad_down = processor.preprocess(cad_raw)

    print_cloud_extent(
        "Step 4 - CAD After Light Preprocessing",
        cad_down
    )

    o3d.visualization.draw_geometries(
        [cad_down],
        window_name="Step 4 - CAD After Light Preprocessing"
    )

    scan_structured, structured_transform = aligner.structure_scan(scan_down)

    print_cloud_extent(
        "Step 5 - Scan Kept In Robot Base Frame",
        scan_structured
    )

    cad_structured, cad_structure_transform = aligner.structure_cad_to_floor(
        cad_down
    )

    print_cloud_extent(
        "Step 6 - CAD Before Orientation Search",
        cad_structured
    )

    (
        cad_initial,
        cad_final,
        cad_to_scan_transform,
        orientation_transform,
        center_transform,
        icp_transform,
    ) = aligner.align_cad_to_scan_by_orientation_search(
        scan_structured,
        cad_structured
    )

    print_cloud_extent(
        "Step 7 - CAD After Best Initial Alignment",
        cad_initial
    )

    show_alignment_result(
        scan_structured,
        cad_initial,
        "Step 7 - Scan vs CAD Before Final ICP"
    )

    print_cloud_extent(
        "Step 8 - CAD After Best ICP Alignment",
        cad_final
    )

    show_alignment_result(
        scan_structured,
        cad_final,
        "Step 8 - Scan vs CAD After ICP Before Noise Removal"
    )

    print("")
    print("=" * 70)
    print("Noise removal starts AFTER scan and CAD are aligned")
    print("=" * 70)

    if config.USE_CAD_BOUND_FILTER:
        scan_filter.preview_cad_range_filter(
            scan_structured,
            cad_final
        )

        scan_filtered = scan_filter.remove_scan_points_outside_cad_bounds(
            scan_structured,
            cad_final
        )
    else:
        print("CAD-bound filtering disabled. Keeping full structured scan.")
        scan_filtered = scan_structured

    print_cloud_extent(
        "Step 9 - Final Scan After CAD-Bound Noise Removal",
        scan_filtered
    )

    deviation_reporter.print_edge_deviation_report(
        scan_filtered,
        cad_final
    )

    edge_plotter.show_edge_deviation(
        deviation_reporter,
        scan_filtered,
        cad_final
    )

    if config.SAVE_CLEANED_SCAN:
        o3d.io.write_point_cloud(
            str(config.CLEANED_SCAN_FILE),
            scan_filtered
        )
        print("Saved cleaned scan inside STL/CAD range to:", config.CLEANED_SCAN_FILE)

    visualizer.show_final_result(
        scan_filtered,
        cad_final
    )

    print("")
    print("=" * 70)
    print("Final CAD-to-scan / CAD-to-robot-base transform")
    print("=" * 70)
    print(cad_to_scan_transform)

    print("")
    print("Orientation transform:")
    print(orientation_transform)

    print("")
    print("Center transform:")
    print(center_transform)

    print("")
    print("ICP transform:")
    print(icp_transform)

    export_robot_base_files_for_robodk(
        config=config,
        scan_raw=scan_raw,
        scan_filtered=scan_filtered,
        cad_final=cad_final,
        cad_to_scan_transform=cad_to_scan_transform
    )


if __name__ == "__main__":
    main()