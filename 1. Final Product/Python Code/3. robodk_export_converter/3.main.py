import sys
from pathlib import Path


# ============================================================
# PROJECT PATH FIX FOR ROBODK / TEMP EXECUTION
# ============================================================

REPOSITORY_FOLDER_NAME = "Robotic-3D-Environment-Mapping"

PROJECT_FOLDER_NAME = "3. robodk_export_converter"

PROJECT_RELATIVE_FOLDER = (
    Path("1. Final Product")
    / "Python Code"
    / PROJECT_FOLDER_NAME
)

REQUIRED_PROJECT_FILES = [
    "config.py",
    "cad_exporter.py",
    "colored_scan_exporter.py",
    "colored_voxel_obj_writer.py",
    "color_material_service.py",
    "point_cloud_scaler.py",
    "robodk_conversion_service.py",
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

    Expected structure:

    Robotic-3D-Environment-Mapping
    |-- 1. Final Product
    |-- CAD Model
    |-- Point Cloud Testing Folder
    |-- RoboDK Export
    """

    if not folder.is_dir():
        return False

    has_final_product = (folder / "1. Final Product").is_dir()
    has_cad_model = (folder / "CAD Model").is_dir()

    return has_final_product and has_cad_model


def get_project_folder_from_repository(repository_folder: Path) -> Path:
    return repository_folder / PROJECT_RELATIVE_FOLDER


def find_repository_from_folder(start_folder: Path) -> Path | None:
    """
    Searches upward from a folder until it finds the repository/root folder.
    """

    for folder in [start_folder, *start_folder.parents]:
        if is_repository_folder(folder):
            return folder.resolve()

    return None


def find_project_folder() -> Path:
    """
    Finds the correct project folder even when RoboDK runs from:

    C:/Users/.../AppData/Local/Temp

    It avoids accidentally using a duplicate folder such as:

    C:/Users/daryl/Desktop/1. Final Product/Python Code/3. robodk_export_converter
    """

    current_file = Path(__file__).resolve()
    current_folder = current_file.parent
    working_folder = Path.cwd().resolve()
    home_folder = Path.home()

    # ------------------------------------------------------------
    # 1. If this file is already inside the real repository,
    # search upward from current file.
    # ------------------------------------------------------------
    repository_folder = find_repository_from_folder(current_folder)

    if repository_folder is not None:
        project_folder = get_project_folder_from_repository(repository_folder)

        if is_correct_project_folder(project_folder):
            return project_folder.resolve()

    # ------------------------------------------------------------
    # 2. Search upward from current working directory.
    # RoboDK often sets cwd to Temp, but this still helps sometimes.
    # ------------------------------------------------------------
    repository_folder = find_repository_from_folder(working_folder)

    if repository_folder is not None:
        project_folder = get_project_folder_from_repository(repository_folder)

        if is_correct_project_folder(project_folder):
            return project_folder.resolve()

    # ------------------------------------------------------------
    # 3. Search common Windows user locations.
    # Important:
    # Search for the repository folder first, not only the project folder.
    # ------------------------------------------------------------
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
        direct_project = get_project_folder_from_repository(direct_repository)

        if is_repository_folder(direct_repository) and is_correct_project_folder(direct_project):
            return direct_project.resolve()

        # Recursive check:
        # Desktop/.../.../Robotic-3D-Environment-Mapping
        try:
            for repository_candidate in search_location.rglob(REPOSITORY_FOLDER_NAME):
                project_folder = get_project_folder_from_repository(repository_candidate)

                if is_repository_folder(repository_candidate) and is_correct_project_folder(project_folder):
                    return project_folder.resolve()

        except PermissionError:
            continue

    # ------------------------------------------------------------
    # 4. Fallback:
    # Search for the project folder name, but only accept it if one
    # of its parent folders is a valid repository.
    # This also works if the repository folder was renamed.
    # ------------------------------------------------------------
    for search_location in search_locations:
        if not search_location.exists():
            continue

        try:
            for project_candidate in search_location.rglob(PROJECT_FOLDER_NAME):
                if not is_correct_project_folder(project_candidate):
                    continue

                repository_folder = find_repository_from_folder(project_candidate)

                if repository_folder is None:
                    continue

                expected_project_folder = get_project_folder_from_repository(repository_folder)

                if project_candidate.resolve() == expected_project_folder.resolve():
                    return project_candidate.resolve()

        except PermissionError:
            continue

    raise FileNotFoundError(
        "Could not find the correct RoboDK export converter project folder.\n\n"
        "Expected repository structure:\n"
        f"{REPOSITORY_FOLDER_NAME}\\1. Final Product\\Python Code\\{PROJECT_FOLDER_NAME}\n"
        f"{REPOSITORY_FOLDER_NAME}\\CAD Model\n"
        f"{REPOSITORY_FOLDER_NAME}\\RoboDK Export\n\n"
        "Example correct path:\n"
        "C:\\Users\\daryl\\Desktop\\Robotic D Environment Mapping\\"
        "Robotic-3D-Environment-Mapping\\1. Final Product\\Python Code\\"
        f"{PROJECT_FOLDER_NAME}\n\n"
        "Problem:\n"
        "A duplicate project folder may exist outside the real repository.\n\n"
        "Fix:\n"
        "Use the project inside Robotic-3D-Environment-Mapping, or remove/rename the duplicate folder."
    )


PROJECT_FOLDER = find_project_folder()

# ------------------------------------------------------------
# Force Python to import from the correct project folder
# ------------------------------------------------------------
cleaned_sys_path = []

for path in sys.path:
    try:
        if Path(path).resolve() != PROJECT_FOLDER:
            cleaned_sys_path.append(path)
    except Exception:
        cleaned_sys_path.append(path)

sys.path = cleaned_sys_path
sys.path.insert(0, str(PROJECT_FOLDER))

# Clear cached modules so RoboDK does not reuse old files
for module_name in [
    "config",
    "cad_exporter",
    "colored_scan_exporter",
    "colored_voxel_obj_writer",
    "color_material_service",
    "point_cloud_scaler",
    "robodk_conversion_service",
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

from cad_exporter import CadExporter
from colored_scan_exporter import ColoredScanExporter
from colored_voxel_obj_writer import ColoredVoxelObjWriter
from color_material_service import ColorMaterialService
from config import Config
from point_cloud_scaler import PointCloudScaler
from robodk_conversion_service import RoboDKConversionService


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():
    config = Config()

    if hasattr(config, "print_paths"):
        config.print_paths()

    point_cloud_scaler = PointCloudScaler()
    color_material_service = ColorMaterialService()

    colored_voxel_obj_writer = ColoredVoxelObjWriter(
        color_material_service
    )

    colored_scan_exporter = ColoredScanExporter(
        point_cloud_scaler,
        colored_voxel_obj_writer
    )

    cad_exporter = CadExporter(
        point_cloud_scaler
    )

    conversion_service = RoboDKConversionService(
        config,
        colored_scan_exporter,
        cad_exporter
    )

    conversion_service.run()


if __name__ == "__main__":
    main()