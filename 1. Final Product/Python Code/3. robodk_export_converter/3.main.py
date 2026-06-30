# Use sys so the program can control where Python looks for files.
import sys
# Use Path so file and folder paths are easier to work with.
from pathlib import Path


# Store an important setting named REPOSITORY_FOLDER_NAME.
REPOSITORY_FOLDER_NAME = "Robotic-3D-Environment-Mapping"

# Store an important setting named PROJECT_FOLDER_NAME.
PROJECT_FOLDER_NAME = "3. robodk_export_converter"

# Store an important setting named PROJECT_RELATIVE_FOLDER.
PROJECT_RELATIVE_FOLDER = (
    # Call this function to do one job.
    Path("1. Final Product")
    # Continue building the path or value.
    / "Python Code"
    # Continue building the path or value.
    / PROJECT_FOLDER_NAME
)

# Store an important setting named REQUIRED_PROJECT_FILES.
REQUIRED_PROJECT_FILES = [
    # Add this text value.
    "config.py",
    # Add this text value.
    "cad_exporter.py",
    # Add this text value.
    "colored_scan_exporter.py",
    # Add this text value.
    "colored_voxel_obj_writer.py",
    # Add this text value.
    "color_material_service.py",
    # Add this text value.
    "point_cloud_scaler.py",
    # Add this text value.
    "robodk_conversion_service.py",
]


# Create the is_correct_project_folder function.
def is_correct_project_folder(folder: Path) -> bool:

    # Check if this condition is true.
    if not folder.is_dir():
        # Give this value back to the code that asked for it.
        return False

    # Give this value back to the code that asked for it.
    return all(
        # Check if this file or folder exists.
        (folder / file_name).exists()
        # Repeat this code for each item.
        for file_name in REQUIRED_PROJECT_FILES
    )


# Create the is_repository_folder function.
def is_repository_folder(folder: Path) -> bool:

    # Check if this condition is true.
    if not folder.is_dir():
        # Give this value back to the code that asked for it.
        return False

    # Store this value in has_final_product.
    has_final_product = (folder / "1. Final Product").is_dir()
    # Store this value in has_cad_model.
    has_cad_model = (folder / "CAD Model").is_dir()

    # Give this value back to the code that asked for it.
    return has_final_product and has_cad_model


# Create the get_project_folder_from_repository function.
def get_project_folder_from_repository(repository_folder: Path) -> Path:
    # Give this value back to the code that asked for it.
    return repository_folder / PROJECT_RELATIVE_FOLDER


# Create the find_repository_from_folder function.
def find_repository_from_folder(start_folder: Path) -> Path | None:

    # Repeat this code for each item.
    for folder in [start_folder, *start_folder.parents]:
        # Check if this condition is true.
        if is_repository_folder(folder):
            # Give this value back to the code that asked for it.
            return folder.resolve()

    # Give this value back to the code that asked for it.
    return None


# Create the find_project_folder function.
def find_project_folder() -> Path:

    # Store the file path in current_file.
    current_file = Path(__file__).resolve()
    # Store the folder path in current_folder.
    current_folder = current_file.parent
    # Store the folder path in working_folder.
    working_folder = Path.cwd().resolve()
    # Store the folder path in home_folder.
    home_folder = Path.home()

    # Store the folder path in repository_folder.
    repository_folder = find_repository_from_folder(current_folder)

    # Check if this condition is true.
    if repository_folder is not None:
        # Store the folder path in project_folder.
        project_folder = get_project_folder_from_repository(repository_folder)

        # Check if this condition is true.
        if is_correct_project_folder(project_folder):
            # Give this value back to the code that asked for it.
            return project_folder.resolve()

    # Store the folder path in repository_folder.
    repository_folder = find_repository_from_folder(working_folder)

    # Check if this condition is true.
    if repository_folder is not None:
        # Store the folder path in project_folder.
        project_folder = get_project_folder_from_repository(repository_folder)

        # Check if this condition is true.
        if is_correct_project_folder(project_folder):
            # Give this value back to the code that asked for it.
            return project_folder.resolve()

    # Store this value in search_locations.
    search_locations = [
        # Add this value to the list or function call.
        home_folder / "Desktop",
        # Add this value to the list or function call.
        home_folder / "OneDrive" / "Desktop",
        # Add this value to the list or function call.
        home_folder / "Documents",
        # Add this value to the list or function call.
        home_folder / "Downloads",
        # Add this value to the list or function call.
        home_folder,
    ]

    # Repeat this code for each item.
    for search_location in search_locations:
        # Check if this condition is true.
        if not search_location.exists():
            # Skip the rest of this loop and move to the next item.
            continue

        # Store this value in direct_repository.
        direct_repository = search_location / REPOSITORY_FOLDER_NAME
        # Store this value in direct_project.
        direct_project = get_project_folder_from_repository(direct_repository)

        # Check if this condition is true.
        if is_repository_folder(direct_repository) and is_correct_project_folder(direct_project):
            # Give this value back to the code that asked for it.
            return direct_project.resolve()

        # Try this code, because it might fail.
        try:
            # Repeat this code for each item.
            for repository_candidate in search_location.rglob(REPOSITORY_FOLDER_NAME):
                # Store the folder path in project_folder.
                project_folder = get_project_folder_from_repository(repository_candidate)

                # Check if this condition is true.
                if is_repository_folder(repository_candidate) and is_correct_project_folder(project_folder):
                    # Give this value back to the code that asked for it.
                    return project_folder.resolve()

        # Handle folders that Python is not allowed to open.
        except PermissionError:
            # Skip the rest of this loop and move to the next item.
            continue

    # Repeat this code for each item.
    for search_location in search_locations:
        # Check if this condition is true.
        if not search_location.exists():
            # Skip the rest of this loop and move to the next item.
            continue

        # Try this code, because it might fail.
        try:
            # Repeat this code for each item.
            for project_candidate in search_location.rglob(PROJECT_FOLDER_NAME):
                # Check if this condition is true.
                if not is_correct_project_folder(project_candidate):
                    # Skip the rest of this loop and move to the next item.
                    continue

                # Store the folder path in repository_folder.
                repository_folder = find_repository_from_folder(project_candidate)

                # Check if this condition is true.
                if repository_folder is None:
                    # Skip the rest of this loop and move to the next item.
                    continue

                # Store the folder path in expected_project_folder.
                expected_project_folder = get_project_folder_from_repository(repository_folder)

                # Check if this condition is true.
                if project_candidate.resolve() == expected_project_folder.resolve():
                    # Give this value back to the code that asked for it.
                    return project_candidate.resolve()

        # Handle folders that Python is not allowed to open.
        except PermissionError:
            # Skip the rest of this loop and move to the next item.
            continue

    # Stop the program and say that a needed file or folder is missing.
    raise FileNotFoundError(
        # Add this text value.
        "Could not find the correct RoboDK export converter project folder.\n\n"
        # Add this text value.
        "Expected repository structure:\n"
        # Add this text value.
        f"{REPOSITORY_FOLDER_NAME}\\1. Final Product\\Python Code\\{PROJECT_FOLDER_NAME}\n"
        # Add this text value.
        f"{REPOSITORY_FOLDER_NAME}\\CAD Model\n"
        # Add this text value.
        f"{REPOSITORY_FOLDER_NAME}\\RoboDK Export\n\n"
        # Add this text value.
        "Example correct path:\n"
        # Add this text value.
        "C:\\Users\\daryl\\Desktop\\Robotic D Environment Mapping\\"
        # Add this text value.
        "Robotic-3D-Environment-Mapping\\1. Final Product\\Python Code\\"
        # Add this text value.
        f"{PROJECT_FOLDER_NAME}\n\n"
        # Add this text value.
        "Problem:\n"
        # Add this text value.
        "A duplicate project folder may exist outside the real repository.\n\n"
        # Add this text value.
        "Fix:\n"
        # Add this text value.
        "Use the project inside Robotic-3D-Environment-Mapping, or remove/rename the duplicate folder."
    )


# Store an important setting named PROJECT_FOLDER.
PROJECT_FOLDER = find_project_folder()

# Store this value in cleaned_sys_path.
cleaned_sys_path = []

# Repeat this code for each item.
for path in sys.path:
    # Try this code, because it might fail.
    try:
        # Check if this condition is true.
        if Path(path).resolve() != PROJECT_FOLDER:
            # Call this function to do one job.
            cleaned_sys_path.append(path)
    # Handle any error so the program can continue safely.
    except Exception:
        # Call this function to do one job.
        cleaned_sys_path.append(path)

# Store this value in sys.path.
sys.path = cleaned_sys_path
# Call this function to do one job.
sys.path.insert(0, str(PROJECT_FOLDER))

# Repeat this code for each item.
for module_name in [
    # Add this text value.
    "config",
    # Add this text value.
    "cad_exporter",
    # Add this text value.
    "colored_scan_exporter",
    # Add this text value.
    "colored_voxel_obj_writer",
    # Add this text value.
    "color_material_service",
    # Add this text value.
    "point_cloud_scaler",
    # Add this text value.
    "robodk_conversion_service",
# This line helps the program do the next small step.
]:
    # Call this function to do one job.
    sys.modules.pop(module_name, None)

# Show a message on the screen.
print("")
# Show a message on the screen.
print("=" * 70)
# Show a message on the screen.
print("Using project folder:")
# Show a message on the screen.
print(PROJECT_FOLDER)
# Show a message on the screen.
print("=" * 70)
# Show a message on the screen.
print("")


# Import the needed tool from cad_exporter.
from cad_exporter import CadExporter
# Import the needed tool from colored_scan_exporter.
from colored_scan_exporter import ColoredScanExporter
# Import the needed tool from colored_voxel_obj_writer.
from colored_voxel_obj_writer import ColoredVoxelObjWriter
# Import the needed tool from color_material_service.
from color_material_service import ColorMaterialService
# Import the needed tool from config.
from config import Config
# Import the needed tool from point_cloud_scaler.
from point_cloud_scaler import PointCloudScaler
# Import the needed tool from robodk_conversion_service.
from robodk_conversion_service import RoboDKConversionService


# Start the main steps of the program.
def main():
    # Store this value in config.
    config = Config()

    # Check if this condition is true.
    if hasattr(config, "print_paths"):
        # Call this function to do one job.
        config.print_paths()

    # Store this value in point_cloud_scaler.
    point_cloud_scaler = PointCloudScaler()
    # Create the service object named color_material_service.
    color_material_service = ColorMaterialService()

    # Create the writer object named colored_voxel_obj_writer.
    colored_voxel_obj_writer = ColoredVoxelObjWriter(
        # This line helps the program do the next small step.
        color_material_service
    )

    # Create the exporter object named colored_scan_exporter.
    colored_scan_exporter = ColoredScanExporter(
        # Add this value to the list or function call.
        point_cloud_scaler,
        # This line helps the program do the next small step.
        colored_voxel_obj_writer
    )

    # Create the exporter object named cad_exporter.
    cad_exporter = CadExporter(
        # This line helps the program do the next small step.
        point_cloud_scaler
    )

    # Create the service object named conversion_service.
    conversion_service = RoboDKConversionService(
        # Add this value to the list or function call.
        config,
        # Add this value to the list or function call.
        colored_scan_exporter,
        # This line helps the program do the next small step.
        cad_exporter
    )

    # Call this function to do one job.
    conversion_service.run()


# Run the main function only when this file is started directly.
if __name__ == "__main__":
    # Call this function to do one job.
    main()
