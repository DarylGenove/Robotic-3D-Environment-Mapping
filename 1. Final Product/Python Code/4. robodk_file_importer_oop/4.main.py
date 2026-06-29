import sys
from pathlib import Path


# ============================================================
# PROJECT PATH FIX FOR ROBODK / TEMP EXECUTION
# ============================================================

REPOSITORY_FOLDER_NAME = "Robotic-3D-Environment-Mapping"

PROJECT_FOLDER_NAME = "4. robodk_file_importer_oop"

PROJECT_RELATIVE_FOLDER = (
    Path("1. Final Product")
    / "Python Code"
    / PROJECT_FOLDER_NAME
)

REQUIRED_PROJECT_FILES = [
    "config.py",
    "file_validator.py",
    "robodk_import_service.py",
    "robodk_item_service.py",
]


def is_correct_project_folder(folder):
    """
    Checks if this is the actual Python project folder.
    """

    if not folder.exists() or not folder.is_dir():
        return False

    return all(
        (folder / file_name).exists()
        for file_name in REQUIRED_PROJECT_FILES
    )


def is_repository_folder(folder):
    """
    Checks if this is the repository/root folder.

    Expected structure:

    Robotic-3D-Environment-Mapping
    |-- 1. Final Product
    |-- CAD Model
    |-- RoboDK Export
    """

    if not folder.exists() or not folder.is_dir():
        return False

    has_final_product = (folder / "1. Final Product").is_dir()
    has_cad_model = (folder / "CAD Model").is_dir()

    return has_final_product and has_cad_model


def get_project_folder_from_repository(repository_folder):
    return repository_folder / PROJECT_RELATIVE_FOLDER


def find_repository_from_folder(start_folder):
    """
    Searches upward from a folder until it finds the repository/root folder.
    """

    for folder in [start_folder, *start_folder.parents]:
        if is_repository_folder(folder):
            return folder.resolve()

    return None


def find_project_folder():
    """
    Finds the correct project folder even when RoboDK runs from:

    C:/Users/.../AppData/Local/Temp

    It avoids accidentally using duplicate folders outside the real repository.
    """

    current_file = Path(__file__).resolve()
    current_folder = current_file.parent
    working_folder = Path.cwd().resolve()
    home_folder = Path.home()

    # ------------------------------------------------------------
    # 1. Search upward from current file location
    # ------------------------------------------------------------
    repository_folder = find_repository_from_folder(current_folder)

    if repository_folder is not None:
        project_folder = get_project_folder_from_repository(repository_folder)

        if is_correct_project_folder(project_folder):
            return project_folder.resolve()

    # ------------------------------------------------------------
    # 2. Search upward from working directory
    # ------------------------------------------------------------
    repository_folder = find_repository_from_folder(working_folder)

    if repository_folder is not None:
        project_folder = get_project_folder_from_repository(repository_folder)

        if is_correct_project_folder(project_folder):
            return project_folder.resolve()

    # ------------------------------------------------------------
    # 3. Search common Windows user locations
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
    # Search for project folder name, but only accept it if it is
    # inside a valid repository folder.
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
        "Could not find the correct RoboDK file importer project folder.\n\n"
        "Expected repository structure:\n"
        f"{REPOSITORY_FOLDER_NAME}\\1. Final Product\\Python Code\\{PROJECT_FOLDER_NAME}\n"
        f"{REPOSITORY_FOLDER_NAME}\\CAD Model\n"
        f"{REPOSITORY_FOLDER_NAME}\\RoboDK Export\n\n"
        "Example correct path:\n"
        "C:\\Users\\daryl\\Desktop\\Robotic D Environment Mapping\\"
        "Robotic-3D-Environment-Mapping\\1. Final Product\\Python Code\\"
        f"{PROJECT_FOLDER_NAME}\n\n"
        "Fix:\n"
        "Use the project inside Robotic-3D-Environment-Mapping, not a duplicate folder outside it."
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
    "file_validator",
    "robodk_import_service",
    "robodk_item_service",
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

from config import Config
from file_validator import FileValidator
from robodk_import_service import RoboDKImportService
from robodk_item_service import RoboDKItemService


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():
    config = Config()

    if hasattr(config, "print_paths"):
        config.print_paths()

    file_validator = FileValidator()
    robodk_item_service = RoboDKItemService()

    robodk_import_service = RoboDKImportService(
        config,
        file_validator,
        robodk_item_service
    )

    robodk_import_service.run()


if __name__ == "__main__":
    main()