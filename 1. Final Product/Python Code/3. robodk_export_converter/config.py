from pathlib import Path


REPOSITORY_FOLDER_NAME = "Robotic-3D-Environment-Mapping"


def is_repository_folder(folder: Path) -> bool:
    """
    Checks if this is the repository/root folder.

    Expected structure:

    Robotic-3D-Environment-Mapping
    |-- 1. Final Product
    |-- CAD Model
    |-- RoboDK Export
    """

    if not folder.is_dir():
        return False

    has_final_product = (folder / "1. Final Product").is_dir()
    has_cad_model = (folder / "CAD Model").is_dir()

    return has_final_product and has_cad_model


def find_repository_folder() -> Path:
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


def find_export_folder(repository_folder: Path) -> Path:
    """
    Finds the RoboDK Export folder that contains the converted alignment output.

    Required files:
    - 02_scan_cleaned_inside_stl_range_ROBODK.pcd
    - 04_aligned_cabinet_ROBODK.stl
    """

    required_files = [
        "02_scan_cleaned_inside_stl_range_ROBODK.pcd",
        "04_aligned_cabinet_ROBODK.stl",
    ]

    python_code_folder = (
        repository_folder
        / "1. Final Product"
        / "Python Code"
    )

    candidate_folders = [
        repository_folder / "RoboDK Export",
        python_code_folder / "2. robodk_scan_alignment" / "RoboDK Export",
    ]

    for folder in candidate_folders:
        if all((folder / file_name).exists() for file_name in required_files):
            return folder.resolve()

    raise FileNotFoundError(
        "Could not find the RoboDK Export folder.\n\n"
        "The folder must contain:\n"
        + "\n".join(f"- {file_name}" for file_name in required_files)
        + "\n\nChecked folders:\n"
        + "\n".join(str(folder) for folder in candidate_folders)
        + "\n\nFix:\n"
        "Run the scan alignment code first so it creates these files, "
        "or copy the required files into the repository RoboDK Export folder."
    )


class Config:
    # ------------------------------------------------------------
    # Main folders
    # ------------------------------------------------------------
    REPOSITORY_FOLDER = find_repository_folder()

    EXPORT_FOLDER = find_export_folder(REPOSITORY_FOLDER)

    # ------------------------------------------------------------
    # Input files from RoboDK Export
    # ------------------------------------------------------------
    CLEANED_SCAN_PCD = (
        EXPORT_FOLDER
        / "02_scan_cleaned_inside_stl_range_ROBODK.pcd"
    )

    ALIGNED_CAD_STL = (
        EXPORT_FOLDER
        / "04_aligned_cabinet_ROBODK.stl"
    )

    # ------------------------------------------------------------
    # Output files for RoboDK
    # ------------------------------------------------------------
    COLORED_SCAN_PLY_FOR_ROBODK = (
        EXPORT_FOLDER
        / "02_scan_cleaned_inside_stl_range_ROBODK_MM_COLORED.ply"
    )

    COLORED_SCAN_OBJ_FOR_ROBODK = (
        EXPORT_FOLDER
        / "02_scan_cleaned_inside_stl_range_ROBODK_MM_COLORED.obj"
    )

    COLORED_SCAN_MTL_FOR_ROBODK = (
        EXPORT_FOLDER
        / "02_scan_cleaned_inside_stl_range_ROBODK_MM_COLORED.mtl"
    )

    CAD_STL_FOR_ROBODK = (
        EXPORT_FOLDER
        / "04_aligned_cabinet_ROBODK_MM.stl"
    )

    # ------------------------------------------------------------
    # Conversion settings
    # ------------------------------------------------------------
    VOXEL_SIZE_M = 0.01
    COLOR_LEVELS = 12

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
        print("Export folder:")
        print(self.EXPORT_FOLDER)
        print("Exists:", self.EXPORT_FOLDER.exists())

        print("")
        print("Cleaned scan PCD:")
        print(self.CLEANED_SCAN_PCD)
        print("Exists:", self.CLEANED_SCAN_PCD.exists())

        print("")
        print("Aligned CAD STL:")
        print(self.ALIGNED_CAD_STL)
        print("Exists:", self.ALIGNED_CAD_STL.exists())

        print("")
        print("Colored scan PLY output:")
        print(self.COLORED_SCAN_PLY_FOR_ROBODK)

        print("")
        print("Colored scan OBJ output:")
        print(self.COLORED_SCAN_OBJ_FOR_ROBODK)

        print("")
        print("Colored scan MTL output:")
        print(self.COLORED_SCAN_MTL_FOR_ROBODK)

        print("")
        print("CAD STL output:")
        print(self.CAD_STL_FOR_ROBODK)

        print("=" * 70)
        print("")