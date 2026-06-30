# Bring in copy so this file can use it.
import copy
# Bring in sys so this file can use it.
import sys
# Bring in needed tools from pathlib.
from pathlib import Path


# Set the REPOSITORY_FOLDER_NAME setting.
REPOSITORY_FOLDER_NAME = "Robotic-3D-Environment-Mapping"

# Set the PROJECT_RELATIVE_FOLDER setting.
PROJECT_RELATIVE_FOLDER = (
    # Run this line as one small step in the program.
    Path("1. Final Product")
    # Run this line as one small step in the program.
    / "Python Code"
    # Run this line as one small step in the program.
    / "2. robodk_scan_alignment"
)

# Set the REQUIRED_PROJECT_FILES setting.
REQUIRED_PROJECT_FILES = [
    # Add this value to the current group.
    "config.py",
    # Add this value to the current group.
    "point_cloud_processor.py",
    # Add this value to the current group.
    "plane_detector.py",
    # Add this value to the current group.
    "scan_aligner.py",
    # Add this value to the current group.
    "scan_filter.py",
    # Add this value to the current group.
    "deviation_reporter.py",
    # Add this value to the current group.
    "visualizer.py",
    # Add this value to the current group.
    "edge_deviation_plotter.py",
]


# Create the is correct project folder function.
def is_correct_project_folder(folder: Path) -> bool:


    # Check this condition before choosing what happens next.
    if not folder.is_dir():
        # Send this result back to the part of the code that asked for it.
        return False

    # Send this result back to the part of the code that asked for it.
    return all(
        # Start a group of values.
        (folder / file_name).exists()
        # Repeat this code for every item in the group.
        for file_name in REQUIRED_PROJECT_FILES
    )


# Create the is repository folder function.
def is_repository_folder(folder: Path) -> bool:


    # Check this condition before choosing what happens next.
    if not folder.is_dir():
        # Send this result back to the part of the code that asked for it.
        return False

    # Save a value in has point cloud folder.
    has_point_cloud_folder = (folder / "Point Cloud Testing Folder").is_dir()
    # Save a value in has cad model folder.
    has_cad_model_folder = (folder / "CAD Model").is_dir()

    # Send this result back to the part of the code that asked for it.
    return has_point_cloud_folder and has_cad_model_folder


# Create the find project folder function.
def find_project_folder() -> Path:


    # Find the folder where this Python file is stored.
    current_file = Path(__file__).resolve()
    # Save a value in current folder.
    current_folder = current_file.parent


    # Repeat this code for every item in the group.
    for folder in [current_folder, *current_folder.parents]:
        # Check this condition before choosing what happens next.
        if folder.name == REPOSITORY_FOLDER_NAME and is_repository_folder(folder):
            # Save a value in project folder.
            project_folder = folder / PROJECT_RELATIVE_FOLDER

            # Check this condition before choosing what happens next.
            if is_correct_project_folder(project_folder):
                # Send this result back to the part of the code that asked for it.
                return project_folder.resolve()


    # Repeat this code for every item in the group.
    for folder in [current_folder, *current_folder.parents]:
        # Check this condition before choosing what happens next.
        if is_repository_folder(folder):
            # Save a value in project folder.
            project_folder = folder / PROJECT_RELATIVE_FOLDER

            # Check this condition before choosing what happens next.
            if is_correct_project_folder(project_folder):
                # Send this result back to the part of the code that asked for it.
                return project_folder.resolve()


    # Find the current user's home folder.
    home_folder = Path.home()

    # Save a value in search locations.
    search_locations = [
        # Add this value to the current group.
        home_folder / "Desktop",
        # Add this value to the current group.
        home_folder / "OneDrive" / "Desktop",
        # Add this value to the current group.
        home_folder / "Documents",
        # Add this value to the current group.
        home_folder / "Downloads",
        # Add this value to the current group.
        home_folder,
    ]

    # Repeat this code for every item in the group.
    for search_location in search_locations:
        # Check this condition before choosing what happens next.
        if not search_location.exists():
            # Skip the rest of this loop and go to the next item.
            continue


        # Save a value in direct repository.
        direct_repository = search_location / REPOSITORY_FOLDER_NAME
        # Save a value in direct project.
        direct_project = direct_repository / PROJECT_RELATIVE_FOLDER

        # Check this condition before choosing what happens next.
        if is_repository_folder(direct_repository) and is_correct_project_folder(direct_project):
            # Send this result back to the part of the code that asked for it.
            return direct_project.resolve()


        # Try this code, but be ready if something goes wrong.
        try:
            # Search inside folders to find the project folder.
            for repository_candidate in search_location.rglob(REPOSITORY_FOLDER_NAME):
                # Save a value in project folder.
                project_folder = repository_candidate / PROJECT_RELATIVE_FOLDER

                # Check this condition before choosing what happens next.
                if is_repository_folder(repository_candidate) and is_correct_project_folder(project_folder):
                    # Send this result back to the part of the code that asked for it.
                    return project_folder.resolve()

        # Handle the error so the program can continue or explain it.
        except PermissionError:
            # Skip the rest of this loop and go to the next item.
            continue

    # Stop the program because an important file or folder is missing.
    raise FileNotFoundError(
        # Run this line as one small step in the program.
        "Could not find the correct RoboDK scan alignment project folder.\n\n"
        # Run this line as one small step in the program.
        "Expected repository structure:\n"
        # Run this line as one small step in the program.
        f"{REPOSITORY_FOLDER_NAME}\\Point Cloud Testing Folder\n"
        # Run this line as one small step in the program.
        f"{REPOSITORY_FOLDER_NAME}\\CAD Model\n"
        # Run this line as one small step in the program.
        f"{REPOSITORY_FOLDER_NAME}\\1. Final Product\\Python Code\\2. robodk_scan_alignment\n\n"
        # Run this line as one small step in the program.
        "Example correct path:\n"
        # Run this line as one small step in the program.
        "C:\\Users\\daryl\\Desktop\\Robotic D Environment Mapping\\"
        # Run this line as one small step in the program.
        "Robotic-3D-Environment-Mapping\\1. Final Product\\Python Code\\2. robodk_scan_alignment\n\n"
        # Run this line as one small step in the program.
        "Problem:\n"
        # Run this line as one small step in the program.
        "A duplicate project folder may exist here:\n"
        # Run this line as one small step in the program.
        "C:\\Users\\daryl\\Desktop\\1. Final Product\\Python Code\\2. robodk_scan_alignment\n\n"
        # Run this line as one small step in the program.
        "Fix:\n"
        # Run this line as one small step in the program.
        "Use the project inside Robotic-3D-Environment-Mapping, or remove/rename the duplicate folder."
    )


# Set the PROJECT_FOLDER setting.
PROJECT_FOLDER = find_project_folder()


# Save a value in cleaned sys path.
cleaned_sys_path = []

# Repeat this code for every item in the group.
for path in sys.path:
    # Try this code, but be ready if something goes wrong.
    try:
        # Check this condition before choosing what happens next.
        if Path(path).resolve() != PROJECT_FOLDER:
            # Add this item to the list.
            cleaned_sys_path.append(path)
    # Handle the error so the program can continue or explain it.
    except Exception:
        # Add this item to the list.
        cleaned_sys_path.append(path)

# Save a value in sys.path.
sys.path = cleaned_sys_path


# Put the project folder first so Python imports the correct files.
sys.path.insert(0, str(PROJECT_FOLDER))


# Repeat this code for every item in the group.
for module_name in [
    # Add this value to the current group.
    "config",
    # Add this value to the current group.
    "point_cloud_processor",
    # Add this value to the current group.
    "plane_detector",
    # Add this value to the current group.
    "scan_aligner",
    # Add this value to the current group.
    "scan_filter",
    # Add this value to the current group.
    "deviation_reporter",
    # Add this value to the current group.
    "visualizer",
    # Add this value to the current group.
    "edge_deviation_plotter",
# Run this line as one small step in the program.
]:
    # Forget an old import so Python loads the fresh file.
    sys.modules.pop(module_name, None)

# Show helpful information on the screen.
print("")
# Show helpful information on the screen.
print("=" * 70)
# Show helpful information on the screen.
print("Using project folder:")
# Show helpful information on the screen.
print(PROJECT_FOLDER)
# Show helpful information on the screen.
print("=" * 70)
# Show helpful information on the screen.
print("")


# Bring in numpy so this file can use it.
import numpy as np
# Bring in open3d so this file can use it.
import open3d as o3d

# Bring in needed tools from config.
from config import Config
# Bring in needed tools from point_cloud_processor.
from point_cloud_processor import PointCloudProcessor
# Bring in needed tools from plane_detector.
from plane_detector import PlaneDetector
# Bring in needed tools from scan_aligner.
from scan_aligner import ScanAligner
# Bring in needed tools from scan_filter.
from scan_filter import ScanFilter
# Bring in needed tools from deviation_reporter.
from deviation_reporter import DeviationReporter
# Bring in needed tools from visualizer.
from visualizer import Visualizer
# Bring in needed tools from edge_deviation_plotter.
from edge_deviation_plotter import EdgeDeviationPlotter


# Create the print cloud extent function.
def print_cloud_extent(name, cloud):
    # Create a simple box around the object.
    bounding_box = cloud.get_axis_aligned_bounding_box()

    # Show helpful information on the screen.
    print("")
    # Show helpful information on the screen.
    print("=" * 70)
    # Show helpful information on the screen.
    print(name)
    # Show helpful information on the screen.
    print("=" * 70)
    # Round the numbers so they are easier to read.
    print("Min bound:", np.round(bounding_box.get_min_bound(), 4))
    # Round the numbers so they are easier to read.
    print("Max bound:", np.round(bounding_box.get_max_bound(), 4))
    # Round the numbers so they are easier to read.
    print("Center   :", np.round(bounding_box.get_center(), 4))
    # Round the numbers so they are easier to read.
    print("Extent   :", np.round(bounding_box.get_extent(), 4))
    # Count how many points are inside this object.
    print("Points   :", len(cloud.points))


# Create the colorize function.
def colorize(point_cloud, color):
    # Make a safe copy so the original object does not change.
    colored_point_cloud = copy.deepcopy(point_cloud)
    # Give the whole point cloud one color.
    colored_point_cloud.paint_uniform_color(color)
    # Send this result back to the part of the code that asked for it.
    return colored_point_cloud


# Create the show alignment result function.
def show_alignment_result(scan_cloud, cad_cloud, window_name):
    # Save a value in scan colored.
    scan_colored = colorize(scan_cloud, [0.1, 0.7, 1.0])
    # Save a value in cad colored.
    cad_colored = colorize(cad_cloud, [1.0, 0.0, 0.0])

    # Open a 3D window to show the scan and CAD model.
    o3d.visualization.draw_geometries(
        # Start a group of values.
        [scan_colored, cad_colored],
        # Save a value in window name.
        window_name=window_name
    )


# Create the load cad mesh for export function.
def load_cad_mesh_for_export(config):
    # Load the CAD/STL mesh so the program can compare it with the scan.
    cad_mesh = o3d.io.read_triangle_mesh(str(config.CAD_FILE))

    # Check if the loaded CAD model has no usable shape.
    if cad_mesh.is_empty():
        # Stop the program and show a clear error message.
        raise Exception(f"CAD mesh is empty or could not be read: {config.CAD_FILE}")

    # Resize the 3D object.
    cad_mesh.scale(
        # Add this value to the current group.
        config.CAD_SCALE,
        # Save a value in center.
        center=(0.0, 0.0, 0.0)
    )

    # Save a value in rx.
    rx = np.radians(config.CAD_EXTRA_RX_DEG)
    # Save a value in ry.
    ry = np.radians(config.CAD_EXTRA_RY_DEG)
    # Save a value in rz.
    rz = np.radians(config.CAD_EXTRA_RZ_DEG)

    # Save a value in rotation matrix.
    rotation_matrix = cad_mesh.get_rotation_matrix_from_xyz(
        # Start a group of values.
        (rx, ry, rz)
    )

    # Rotate the CAD model around its center.
    cad_mesh.rotate(
        # Add this value to the current group.
        rotation_matrix,
        # Save a value in center.
        center=cad_mesh.get_center()
    )

    # Prepare the CAD surface so it displays correctly.
    cad_mesh.compute_vertex_normals()

    # Send this result back to the part of the code that asked for it.
    return cad_mesh


# Create the export robot base files for robodk function.
def export_robot_base_files_for_robodk(
    # Add this value to the current group.
    config,
    # Add this value to the current group.
    scan_raw,
    # Add this value to the current group.
    scan_filtered,
    # Add this value to the current group.
    cad_final,
    # Run this line as one small step in the program.
    cad_to_scan_transform
# Run this line as one small step in the program.
):
    # Save a value in export folder.
    export_folder = PROJECT_FOLDER / "RoboDK Export"
    # Create this folder if it is missing.
    export_folder.mkdir(parents=True, exist_ok=True)

    # Save a value in raw scan robot base file.
    raw_scan_robot_base_file = export_folder / "01_raw_merged_scan_robot_base.pcd"
    # Save a value in cleaned scan robot base file.
    cleaned_scan_robot_base_file = export_folder / "02_scan_cleaned_inside_stl_range_ROBODK.pcd"
    # Save a value in aligned cad pcd robot base file.
    aligned_cad_pcd_robot_base_file = export_folder / "03_aligned_cabinet_ROBODK.pcd"
    # Save a value in aligned cad stl robot base file.
    aligned_cad_stl_robot_base_file = export_folder / "04_aligned_cabinet_ROBODK.stl"
    # Save a value in cad to robot base transform file.
    cad_to_robot_base_transform_file = export_folder / "05_cad_to_robot_base_transform.txt"

    # Save a value in cad mesh robot base.
    cad_mesh_robot_base = load_cad_mesh_for_export(config)
    # Move or rotate the 3D object using a transform matrix.
    cad_mesh_robot_base.transform(cad_to_scan_transform)
    # Prepare the CAD surface so it displays correctly.
    cad_mesh_robot_base.compute_vertex_normals()

    # Save a point cloud file to the computer.
    o3d.io.write_point_cloud(
        # Add this value to the current group.
        str(raw_scan_robot_base_file),
        # Run this line as one small step in the program.
        scan_raw
    )

    # Save a point cloud file to the computer.
    o3d.io.write_point_cloud(
        # Add this value to the current group.
        str(cleaned_scan_robot_base_file),
        # Run this line as one small step in the program.
        scan_filtered
    )

    # Save a point cloud file to the computer.
    o3d.io.write_point_cloud(
        # Add this value to the current group.
        str(aligned_cad_pcd_robot_base_file),
        # Run this line as one small step in the program.
        cad_final
    )

    # Save a mesh file to the computer.
    o3d.io.write_triangle_mesh(
        # Add this value to the current group.
        str(aligned_cad_stl_robot_base_file),
        # Run this line as one small step in the program.
        cad_mesh_robot_base
    )

    # Run this line as one small step in the program.
    np.savetxt(
        # Add this value to the current group.
        str(cad_to_robot_base_transform_file),
        # Add this value to the current group.
        cad_to_scan_transform,
        # Save a value in fmt.
        fmt="%.10f"
    )

    # Show helpful information on the screen.
    print("")
    # Show helpful information on the screen.
    print("=" * 70)
    # Show helpful information on the screen.
    print("ROBOT BASE EXPORT FOR ROBODK")
    # Show helpful information on the screen.
    print("=" * 70)

    # Show helpful information on the screen.
    print("Raw merged scan:")
    # Show helpful information on the screen.
    print(raw_scan_robot_base_file)

    # Show helpful information on the screen.
    print("")
    # Show helpful information on the screen.
    print("Cleaned scan in robot base frame:")
    # Show helpful information on the screen.
    print(cleaned_scan_robot_base_file)

    # Show helpful information on the screen.
    print("")
    # Show helpful information on the screen.
    print("Aligned CAD point cloud in robot base frame:")
    # Show helpful information on the screen.
    print(aligned_cad_pcd_robot_base_file)

    # Show helpful information on the screen.
    print("")
    # Show helpful information on the screen.
    print("Aligned cabinet STL in robot base frame:")
    # Show helpful information on the screen.
    print(aligned_cad_stl_robot_base_file)

    # Show helpful information on the screen.
    print("")
    # Show helpful information on the screen.
    print("CAD-to-robot-base transform:")
    # Show helpful information on the screen.
    print(cad_to_robot_base_transform_file)

    # Show helpful information on the screen.
    print("")
    # Show helpful information on the screen.
    print(cad_to_scan_transform)
    # Show helpful information on the screen.
    print("=" * 70)


# Create the main function that starts the program.
def main():
    # Save a value in config.
    config = Config()


    # Check this condition before choosing what happens next.
    if hasattr(config, "print_paths"):
        # Run this line as one small step in the program.
        config.print_paths()
    # Use this path when the earlier checks were false.
    else:
        # Show helpful information on the screen.
        print("")
        # Show helpful information on the screen.
        print("=" * 70)
        # Show helpful information on the screen.
        print("CONFIG PATH CHECK")
        # Show helpful information on the screen.
        print("=" * 70)
        # Show helpful information on the screen.
        print("Repository folder:", config.REPOSITORY_FOLDER)
        # Show helpful information on the screen.
        print("Point cloud folder:", config.POINT_CLOUD_TESTING_FOLDER)
        # Show helpful information on the screen.
        print("CAD model folder:", config.CAD_MODEL_FOLDER)
        # Show helpful information on the screen.
        print("Scan file:", config.SCAN_FILE)
        # Show helpful information on the screen.
        print("Scan exists:", config.SCAN_FILE.exists())
        # Show helpful information on the screen.
        print("CAD file:", config.CAD_FILE)
        # Show helpful information on the screen.
        print("CAD exists:", config.CAD_FILE.exists())
        # Show helpful information on the screen.
        print("=" * 70)
        # Show helpful information on the screen.
        print("")

    # Save a value in processor.
    processor = PointCloudProcessor(config)
    # Save a value in plane detector.
    plane_detector = PlaneDetector(config)
    # Save a value in aligner.
    aligner = ScanAligner(config, plane_detector)
    # Save a value in scan filter.
    scan_filter = ScanFilter(config)
    # Save a value in deviation reporter.
    deviation_reporter = DeviationReporter(plane_detector)
    # Save a value in visualizer.
    visualizer = Visualizer()
    # Save a value in edge plotter.
    edge_plotter = EdgeDeviationPlotter(scale_to_mm=True)

    # Save a value in scan raw.
    scan_raw = processor.load_scan()

    # Run this line as one small step in the program.
    print_cloud_extent(
        # Add this value to the current group.
        "Step 1 - Raw Scan Loaded From PCD",
        # Run this line as one small step in the program.
        scan_raw
    )

    # Open a 3D window to show the scan and CAD model.
    o3d.visualization.draw_geometries(
        # Start a group of values.
        [scan_raw],
        # Save a value in window name.
        window_name="Step 1 - Raw Scan Loaded From PCD"
    )

    # Save a value in scan down.
    scan_down = processor.preprocess(scan_raw)

    # Run this line as one small step in the program.
    print_cloud_extent(
        # Add this value to the current group.
        "Step 2 - Scan After Light Preprocessing",
        # Run this line as one small step in the program.
        scan_down
    )

    # Open a 3D window to show the scan and CAD model.
    o3d.visualization.draw_geometries(
        # Start a group of values.
        [scan_down],
        # Save a value in window name.
        window_name="Step 2 - Scan After Light Preprocessing"
    )

    # Save a value in cad raw.
    cad_raw = processor.load_cad_as_point_cloud()

    # Run this line as one small step in the program.
    print_cloud_extent(
        # Add this value to the current group.
        "Step 3 - CAD After Scale",
        # Run this line as one small step in the program.
        cad_raw
    )

    # Open a 3D window to show the scan and CAD model.
    o3d.visualization.draw_geometries(
        # Start a group of values.
        [cad_raw],
        # Save a value in window name.
        window_name="Step 3 - CAD After Scale"
    )

    # Save a value in cad down.
    cad_down = processor.preprocess(cad_raw)

    # Run this line as one small step in the program.
    print_cloud_extent(
        # Add this value to the current group.
        "Step 4 - CAD After Light Preprocessing",
        # Run this line as one small step in the program.
        cad_down
    )

    # Open a 3D window to show the scan and CAD model.
    o3d.visualization.draw_geometries(
        # Start a group of values.
        [cad_down],
        # Save a value in window name.
        window_name="Step 4 - CAD After Light Preprocessing"
    )

    # Save several results into separate variable names.
    scan_structured, structured_transform = aligner.structure_scan(scan_down)

    # Run this line as one small step in the program.
    print_cloud_extent(
        # Add this value to the current group.
        "Step 5 - Scan Kept In Robot Base Frame",
        # Run this line as one small step in the program.
        scan_structured
    )

    # Save several results into separate variable names.
    cad_structured, cad_structure_transform = aligner.structure_cad_to_floor(
        # Run this line as one small step in the program.
        cad_down
    )

    # Run this line as one small step in the program.
    print_cloud_extent(
        # Add this value to the current group.
        "Step 6 - CAD Before Orientation Search",
        # Run this line as one small step in the program.
        cad_structured
    )

    # Start a group of values.
    (
        # Add this value to the current group.
        cad_initial,
        # Add this value to the current group.
        cad_final,
        # Add this value to the current group.
        cad_to_scan_transform,
        # Add this value to the current group.
        orientation_transform,
        # Add this value to the current group.
        center_transform,
        # Add this value to the current group.
        icp_transform,
    # Save a value in ).
    ) = aligner.align_cad_to_scan_by_orientation_search(
        # Add this value to the current group.
        scan_structured,
        # Run this line as one small step in the program.
        cad_structured
    )

    # Run this line as one small step in the program.
    print_cloud_extent(
        # Add this value to the current group.
        "Step 7 - CAD After Best Initial Alignment",
        # Run this line as one small step in the program.
        cad_initial
    )

    # Run this line as one small step in the program.
    show_alignment_result(
        # Add this value to the current group.
        scan_structured,
        # Add this value to the current group.
        cad_initial,
        # Run this line as one small step in the program.
        "Step 7 - Scan vs CAD Before Final ICP"
    )

    # Run this line as one small step in the program.
    print_cloud_extent(
        # Add this value to the current group.
        "Step 8 - CAD After Best ICP Alignment",
        # Run this line as one small step in the program.
        cad_final
    )

    # Run this line as one small step in the program.
    show_alignment_result(
        # Add this value to the current group.
        scan_structured,
        # Add this value to the current group.
        cad_final,
        # Run this line as one small step in the program.
        "Step 8 - Scan vs CAD After ICP Before Noise Removal"
    )

    # Show helpful information on the screen.
    print("")
    # Show helpful information on the screen.
    print("=" * 70)
    # Show helpful information on the screen.
    print("Noise removal starts AFTER scan and CAD are aligned")
    # Show helpful information on the screen.
    print("=" * 70)

    # Check this condition before choosing what happens next.
    if config.USE_CAD_BOUND_FILTER:
        # Run this line as one small step in the program.
        scan_filter.preview_cad_range_filter(
            # Add this value to the current group.
            scan_structured,
            # Run this line as one small step in the program.
            cad_final
        )

        # Save a value in scan filtered.
        scan_filtered = scan_filter.remove_scan_points_outside_cad_bounds(
            # Add this value to the current group.
            scan_structured,
            # Run this line as one small step in the program.
            cad_final
        )
    # Use this path when the earlier checks were false.
    else:
        # Show helpful information on the screen.
        print("CAD-bound filtering disabled. Keeping full structured scan.")
        # Save a value in scan filtered.
        scan_filtered = scan_structured

    # Run this line as one small step in the program.
    print_cloud_extent(
        # Add this value to the current group.
        "Step 9 - Final Scan After CAD-Bound Noise Removal",
        # Run this line as one small step in the program.
        scan_filtered
    )

    # Run this line as one small step in the program.
    deviation_reporter.print_edge_deviation_report(
        # Add this value to the current group.
        scan_filtered,
        # Run this line as one small step in the program.
        cad_final
    )

    # Run this line as one small step in the program.
    edge_plotter.show_edge_deviation(
        # Add this value to the current group.
        deviation_reporter,
        # Add this value to the current group.
        scan_filtered,
        # Run this line as one small step in the program.
        cad_final
    )

    # Check this condition before choosing what happens next.
    if config.SAVE_CLEANED_SCAN:
        # Save a point cloud file to the computer.
        o3d.io.write_point_cloud(
            # Add this value to the current group.
            str(config.CLEANED_SCAN_FILE),
            # Run this line as one small step in the program.
            scan_filtered
        )

        # Show helpful information on the screen.
        print("")
        # Show helpful information on the screen.
        print("Saved cleaned scan inside STL/CAD range to:")
        # Show helpful information on the screen.
        print(config.CLEANED_SCAN_FILE)

    # Run this line as one small step in the program.
    visualizer.show_final_result(
        # Add this value to the current group.
        scan_filtered,
        # Run this line as one small step in the program.
        cad_final
    )

    # Show helpful information on the screen.
    print("")
    # Show helpful information on the screen.
    print("=" * 70)
    # Show helpful information on the screen.
    print("Final CAD-to-scan / CAD-to-robot-base transform")
    # Show helpful information on the screen.
    print("=" * 70)
    # Show helpful information on the screen.
    print(cad_to_scan_transform)

    # Show helpful information on the screen.
    print("")
    # Show helpful information on the screen.
    print("Orientation transform:")
    # Show helpful information on the screen.
    print(orientation_transform)

    # Show helpful information on the screen.
    print("")
    # Show helpful information on the screen.
    print("Center transform:")
    # Show helpful information on the screen.
    print(center_transform)

    # Show helpful information on the screen.
    print("")
    # Show helpful information on the screen.
    print("ICP transform:")
    # Show helpful information on the screen.
    print(icp_transform)

    # Run this line as one small step in the program.
    export_robot_base_files_for_robodk(
        # Save a value in config.
        config=config,
        # Save a value in scan raw.
        scan_raw=scan_raw,
        # Save a value in scan filtered.
        scan_filtered=scan_filtered,
        # Save a value in cad final.
        cad_final=cad_final,
        # Save a value in cad to scan transform.
        cad_to_scan_transform=cad_to_scan_transform
    )


# Only start the program automatically when this file is run directly.
if __name__ == "__main__":
    # Run this line as one small step in the program.
    main()
