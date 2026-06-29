from pathlib import Path


REPOSITORY_FOLDER_NAME = "Robotic-3D-Environment-Mapping"


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


def find_repository_folder():
    """
    Finds the main repository folder.

    This works on different computers as long as the folder structure stays the same.
    """

    current_file = Path(__file__).resolve()
    current_folder = current_file.parent

    # ------------------------------------------------------------
    # 1. Search upward from config.py
    # ------------------------------------------------------------
    for folder in [current_folder, *current_folder.parents]:
        if folder.name == REPOSITORY_FOLDER_NAME and is_repository_folder(folder):
            return folder.resolve()

    # ------------------------------------------------------------
    # 2. Allow renamed repository folder
    # ------------------------------------------------------------
    for folder in [current_folder, *current_folder.parents]:
        if is_repository_folder(folder):
            return folder.resolve()

    # ------------------------------------------------------------
    # 3. Fallback search in common user locations
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

        direct_repository = search_location / REPOSITORY_FOLDER_NAME

        if is_repository_folder(direct_repository):
            return direct_repository.resolve()

        try:
            for repository_candidate in search_location.rglob(REPOSITORY_FOLDER_NAME):
                if is_repository_folder(repository_candidate):
                    return repository_candidate.resolve()

        except PermissionError:
            continue

    raise FileNotFoundError(
        "Could not find the main repository folder.\n\n"
        "Expected a folder that contains:\n"
        "- 1. Final Product\n"
        "- CAD Model\n\n"
        "Example correct path:\n"
        "C:\\Users\\daryl\\Desktop\\Robotic D Environment Mapping\\"
        "Robotic-3D-Environment-Mapping"
    )


def find_robodk_export_folder(repository_folder):
    """
    Finds the RoboDK Export folder that contains files created by:

    3. robodk_export_converter

    Required files:
    - colored OBJ or colored PLY
    - millimeter CAD STL
    """

    colored_scan_obj = "02_scan_cleaned_inside_stl_range_ROBODK_MM_COLORED.obj"
    colored_scan_ply = "02_scan_cleaned_inside_stl_range_ROBODK_MM_COLORED.ply"
    aligned_cad_stl = "04_aligned_cabinet_ROBODK_MM.stl"

    python_code_folder = (
        repository_folder
        / "1. Final Product"
        / "Python Code"
    )

    candidate_folders = [
        repository_folder / "RoboDK Export",
        python_code_folder / "2. robodk_scan_alignment" / "RoboDK Export",
        python_code_folder / "3. robodk_export_converter" / "RoboDK Export",
    ]

    for folder in candidate_folders:
        has_colored_scan = (
            (folder / colored_scan_obj).exists()
            or (folder / colored_scan_ply).exists()
        )

        has_aligned_cad = (folder / aligned_cad_stl).exists()

        if has_colored_scan and has_aligned_cad:
            return folder.resolve()

    raise FileNotFoundError(
        "Could not find the RoboDK Export folder.\n\n"
        "Expected these files:\n"
        f"- {colored_scan_obj} or {colored_scan_ply}\n"
        f"- {aligned_cad_stl}\n\n"
        "Checked folders:\n"
        + "\n".join(str(folder) for folder in candidate_folders)
        + "\n\n"
        "Fix:\n"
        "Run the third script first: 3. robodk_export_converter. "
        "That script creates the colored OBJ/PLY and millimeter STL files."
    )


class Config:
    # ------------------------------------------------------------
    # Main folders
    # ------------------------------------------------------------
    REPOSITORY_FOLDER = find_repository_folder()

    ROBODK_EXPORT_FOLDER = find_robodk_export_folder(REPOSITORY_FOLDER)

    # ------------------------------------------------------------
    # Input files for RoboDK import
    # ------------------------------------------------------------
    COLORED_SCAN_OBJ_FILE = (
        ROBODK_EXPORT_FOLDER
        / "02_scan_cleaned_inside_stl_range_ROBODK_MM_COLORED.obj"
    )

    COLORED_SCAN_MTL_FILE = (
        ROBODK_EXPORT_FOLDER
        / "02_scan_cleaned_inside_stl_range_ROBODK_MM_COLORED.mtl"
    )

    COLORED_SCAN_PLY_FILE = (
        ROBODK_EXPORT_FOLDER
        / "02_scan_cleaned_inside_stl_range_ROBODK_MM_COLORED.ply"
    )

    ALIGNED_CAD_STL_FILE = (
        ROBODK_EXPORT_FOLDER
        / "04_aligned_cabinet_ROBODK_MM.stl"
    )

    # ------------------------------------------------------------
    # RoboDK item names
    # ------------------------------------------------------------
    SCAN_ITEM_NAME = "Robot Base - Colored Cleaned Scan Mesh"
    CAD_ITEM_NAME = "Robot Base - Aligned Cabinet STL"

    # Red with transparency
    CAD_COLOR = [1.0, 0.0, 0.0, 0.35]

    # ------------------------------------------------------------
    # Debug path printer
    # ------------------------------------------------------------
    def print_paths(self):
        print("")
        print("=" * 70)
        print("CONFIG PATH CHECK")
        print("=" * 70)

        print("Repository folder:")
        print(self.REPOSITORY_FOLDER)
        print("Exists:", self.REPOSITORY_FOLDER.exists())

        print("")
        print("RoboDK Export folder:")
        print(self.ROBODK_EXPORT_FOLDER)
        print("Exists:", self.ROBODK_EXPORT_FOLDER.exists())

        print("")
        print("Colored scan OBJ:")
        print(self.COLORED_SCAN_OBJ_FILE)
        print("Exists:", self.COLORED_SCAN_OBJ_FILE.exists())

        print("")
        print("Colored scan MTL:")
        print(self.COLORED_SCAN_MTL_FILE)
        print("Exists:", self.COLORED_SCAN_MTL_FILE.exists())

        print("")
        print("Colored scan PLY:")
        print(self.COLORED_SCAN_PLY_FILE)
        print("Exists:", self.COLORED_SCAN_PLY_FILE.exists())

        print("")
        print("Aligned CAD STL:")
        print(self.ALIGNED_CAD_STL_FILE)
        print("Exists:", self.ALIGNED_CAD_STL_FILE.exists())

        print("=" * 70)
        print("")