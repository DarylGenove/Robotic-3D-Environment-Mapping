import copy
import sys
from pathlib import Path

# ============================================================
# PROJECT PATH FIX FOR ROBODK / TEMP EXECUTION
# ============================================================

REPOSITORY_FOLDER_NAME = "Robotic-3D-Environment-Mapping"

PROJECT_RELATIVE_FOLDER = (
    Path("1. Final Product")
    / "Python Code"
    / "2. robodk_scan_alignment"
)

REQUIRED_PROJECT_FILES = [
    "config.py",
    "point_cloud_processor.py",
    "plane_detector.py",
    "scan_aligner.py",
    "scan_filter.py",
    "deviation_reporter.py",
    "visualizer.py",
    "edge_deviation_plotter.py",
]


def is_correct_project_folder(folder: Path) -> bool:
    """
    Checks if this is the actual Python project folder.
    """

    if not folder.is_dir():
        return False

    return all(
        (folder / file_name).exists()
        for file_name in REQUIRED_PROJECT_FILES
    )


def is_repository_folder(folder: Path) -> bool:
    """
    Checks if this is the repository/root folder.

    Required structure:

    Robotic-3D-Environment-Mapping
    |-- Point Cloud Testing Folder
    |-- CAD Model
    |-- 1. Final Product
    """

    if not folder.is_dir():
        return False

    has_point_cloud_folder = (folder / "Point Cloud Testing Folder").is_dir()
    has_cad_model_folder = (folder / "CAD Model").is_dir()

    return has_point_cloud_folder and has_cad_model_folder


def find_project_folder() -> Path:
    """
    Finds the correct project folder even when RoboDK runs this file
    from AppData/Local/Temp.

    It searches for:

    Robotic-3D-Environment-Mapping
    |-- Point Cloud Testing Folder
    |-- CAD Model
    |-- 1. Final Product
        |-- Python Code
            |-- 2. robodk_scan_alignment
    """

    current_file = Path(__file__).resolve()
    current_folder = current_file.parent

    # ------------------------------------------------------------
    # 1. Search upward from the current file location.
    # This works if the file is already inside the repository.
    # ------------------------------------------------------------
    for folder in [current_folder, *current_folder.parents]:
        if folder.name == REPOSITORY_FOLDER_NAME and is_repository_folder(folder):
            project_folder = folder / PROJECT_RELATIVE_FOLDER

            if is_correct_project_folder(project_folder):
                return project_folder.resolve()

    # ------------------------------------------------------------
    # 2. Allow repository folder rename.
    # As long as it has Point Cloud Testing Folder and CAD Model,
    # we can still use it.
    # ------------------------------------------------------------
    for folder in [current_folder, *current_folder.parents]:
        if is_repository_folder(folder):
            project_folder = folder / PROJECT_RELATIVE_FOLDER

            if is_correct_project_folder(project_folder):
                return project_folder.resolve()

    # ------------------------------------------------------------
    # 3. RoboDK usually runs from Temp, so search common locations.
    # Important:
    # Search for the repository folder first, not just the project folder.
    # This avoids accidentally using:
    # C:/Users/daryl/Desktop/1. Final Product/...
    # ------------------------------------------------------------
    home_folder = Path.home()

    search_locations = [
        home_folder / "Desktop",
        home_folder / "OneDrive" / "Desktop",
        home_folder / "Documents",
        home_folder / "Downloads",
        home_folder,
    ]

    for search_location in search_locations:
        if not search_location.exists():
            continue

        # Direct check:
        # Desktop/Robotic-3D-Environment-Mapping
        direct_repository = search_location / REPOSITORY_FOLDER_NAME
        direct_project = direct_repository / PROJECT_RELATIVE_FOLDER

        if is_repository_folder(direct_repository) and is_correct_project_folder(direct_project):
            return direct_project.resolve()

        # Recursive check:
        # Desktop/.../.../Robotic-3D-Environment-Mapping
        try:
            for repository_candidate in search_location.rglob(REPOSITORY_FOLDER_NAME):
                project_folder = repository_candidate / PROJECT_RELATIVE_FOLDER

                if is_repository_folder(repository_candidate) and is_correct_project_folder(project_folder):
                    return project_folder.resolve()

        except PermissionError:
            continue

    raise FileNotFoundError(
        "Could not find the correct RoboDK scan alignment project folder.\n\n"
        "Expected repository structure:\n"
        f"{REPOSITORY_FOLDER_NAME}\\Point Cloud Testing Folder\n"
        f"{REPOSITORY_FOLDER_NAME}\\CAD Model\n"
        f"{REPOSITORY_FOLDER_NAME}\\1. Final Product\\Python Code\\2. robodk_scan_alignment\n\n"
        "Example correct path:\n"
        "C:\\Users\\daryl\\Desktop\\Robotic D Environment Mapping\\"
        "Robotic-3D-Environment-Mapping\\1. Final Product\\Python Code\\2. robodk_scan_alignment\n\n"
        "Problem:\n"
        "A duplicate project folder may exist here:\n"
        "C:\\Users\\daryl\\Desktop\\1. Final Product\\Python Code\\2. robodk_scan_alignment\n\n"
        "Fix:\n"
        "Use the project inside Robotic-3D-Environment-Mapping, or remove/rename the duplicate folder."
    )


PROJECT_FOLDER = find_project_folder()

# Remove old project paths from sys.path
cleaned_sys_path = []

for path in sys.path:
    try:
        if Path(path).resolve() != PROJECT_FOLDER:
            cleaned_sys_path.append(path)
    except Exception:
        cleaned_sys_path.append(path)

sys.path = cleaned_sys_path

# Force Python to import modules from the correct project folder first
sys.path.insert(0, str(PROJECT_FOLDER))

# Clear cached imports so RoboDK does not reuse old config.py
for module_name in [
    "config",
    "point_cloud_processor",
    "plane_detector",
    "scan_aligner",
    "scan_filter",
    "deviation_reporter",
    "visualizer",
    "edge_deviation_plotter",
]:
    sys.modules.pop(module_name, None)

print("")
print("=" * 70)
print("Using project folder:")
print(PROJECT_FOLDER)
print("=" * 70)
print("")


# ============================================================
# NORMAL IMPORTS
# ============================================================

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


# ============================================================
# HELPER FUNCTIONS
# ============================================================

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
    export_folder = PROJECT_FOLDER / "RoboDK Export"
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


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():
    config = Config()

    # This avoids crashing if an old config.py is accidentally loaded.
    # But if your config.py has print_paths(), it will print all paths.
    if hasattr(config, "print_paths"):
        config.print_paths()
    else:
        print("")
        print("=" * 70)
        print("CONFIG PATH CHECK")
        print("=" * 70)
        print("Repository folder:", config.REPOSITORY_FOLDER)
        print("Point cloud folder:", config.POINT_CLOUD_TESTING_FOLDER)
        print("CAD model folder:", config.CAD_MODEL_FOLDER)
        print("Scan file:", config.SCAN_FILE)
        print("Scan exists:", config.SCAN_FILE.exists())
        print("CAD file:", config.CAD_FILE)
        print("CAD exists:", config.CAD_FILE.exists())
        print("=" * 70)
        print("")

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

        print("")
        print("Saved cleaned scan inside STL/CAD range to:")
        print(config.CLEANED_SCAN_FILE)

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