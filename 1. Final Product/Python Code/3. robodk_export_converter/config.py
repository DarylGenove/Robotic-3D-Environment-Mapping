# Use Path so file and folder paths are easier to work with.
from pathlib import Path


# Store an important setting named REPOSITORY_FOLDER_NAME.
REPOSITORY_FOLDER_NAME = "Robotic-3D-Environment-Mapping"


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


# Create the find_repository_folder function.
def find_repository_folder() -> Path:

    # Store the file path in current_file.
    current_file = Path(__file__).resolve()
    # Store the folder path in current_folder.
    current_folder = current_file.parent

    # Repeat this code for each item.
    for folder in [current_folder, *current_folder.parents]:
        # Check if this condition is true.
        if folder.name == REPOSITORY_FOLDER_NAME and is_repository_folder(folder):
            # Give this value back to the code that asked for it.
            return folder.resolve()

    # Repeat this code for each item.
    for folder in [current_folder, *current_folder.parents]:
        # Check if this condition is true.
        if is_repository_folder(folder):
            # Give this value back to the code that asked for it.
            return folder.resolve()

    # Store the folder path in home_folder.
    home_folder = Path.home()

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

        # Check if this condition is true.
        if is_repository_folder(direct_repository):
            # Give this value back to the code that asked for it.
            return direct_repository.resolve()

        # Try this code, because it might fail.
        try:
            # Repeat this code for each item.
            for repository_candidate in search_location.rglob(REPOSITORY_FOLDER_NAME):
                # Check if this condition is true.
                if is_repository_folder(repository_candidate):
                    # Give this value back to the code that asked for it.
                    return repository_candidate.resolve()

        # Handle folders that Python is not allowed to open.
        except PermissionError:
            # Skip the rest of this loop and move to the next item.
            continue

    # Stop the program and say that a needed file or folder is missing.
    raise FileNotFoundError(
        # Add this text value.
        "Could not find the main repository folder.\n\n"
        # Add this text value.
        "Expected a folder that contains:\n"
        # Add this text value.
        "- 1. Final Product\n"
        # Add this text value.
        "- CAD Model\n\n"
        # Add this text value.
        "Example correct path:\n"
        # Add this text value.
        "C:\\Users\\daryl\\Desktop\\Robotic D Environment Mapping\\"
        # Add this text value.
        "Robotic-3D-Environment-Mapping"
    )


# Create the find_export_folder function.
def find_export_folder(repository_folder: Path) -> Path:

    # Store this value in required_files.
    required_files = [
        # Add this text value.
        "02_scan_cleaned_inside_stl_range_ROBODK.pcd",
        # Add this text value.
        "04_aligned_cabinet_ROBODK.stl",
    ]

    # Store the folder path in python_code_folder.
    python_code_folder = (
        # This line helps the program do the next small step.
        repository_folder
        # Continue building the path or value.
        / "1. Final Product"
        # Continue building the path or value.
        / "Python Code"
    )

    # Store this value in candidate_folders.
    candidate_folders = [
        # Add this value to the list or function call.
        repository_folder / "RoboDK Export",
        # Add this value to the list or function call.
        python_code_folder / "2. robodk_scan_alignment" / "RoboDK Export",
    ]

    # Repeat this code for each item.
    for folder in candidate_folders:
        # Check if this condition is true.
        if all((folder / file_name).exists() for file_name in required_files):
            # Give this value back to the code that asked for it.
            return folder.resolve()

    # Stop the program and say that a needed file or folder is missing.
    raise FileNotFoundError(
        # Add this text value.
        "Could not find the RoboDK Export folder.\n\n"
        # Add this text value.
        "The folder must contain:\n"
        # Call this function to do one job.
        + "\n".join(f"- {file_name}" for file_name in required_files)
        # This line helps the program do the next small step.
        + "\n\nChecked folders:\n"
        # Call this function to do one job.
        + "\n".join(str(folder) for folder in candidate_folders)
        # This line helps the program do the next small step.
        + "\n\nFix:\n"
        # Add this text value.
        "Run the scan alignment code first so it creates these files, "
        # Add this text value.
        "or copy the required files into the repository RoboDK Export folder."
    )


# Create the Config class to group related code together.
class Config:
    # Store an important setting named REPOSITORY_FOLDER.
    REPOSITORY_FOLDER = find_repository_folder()

    # Store an important setting named EXPORT_FOLDER.
    EXPORT_FOLDER = find_export_folder(REPOSITORY_FOLDER)

    # Store an important setting named CLEANED_SCAN_PCD.
    CLEANED_SCAN_PCD = (
        # This line helps the program do the next small step.
        EXPORT_FOLDER
        # Continue building the path or value.
        / "02_scan_cleaned_inside_stl_range_ROBODK.pcd"
    )

    # Store an important setting named ALIGNED_CAD_STL.
    ALIGNED_CAD_STL = (
        # This line helps the program do the next small step.
        EXPORT_FOLDER
        # Continue building the path or value.
        / "04_aligned_cabinet_ROBODK.stl"
    )

    # Store an important setting named COLORED_SCAN_PLY_FOR_ROBODK.
    COLORED_SCAN_PLY_FOR_ROBODK = (
        # This line helps the program do the next small step.
        EXPORT_FOLDER
        # Continue building the path or value.
        / "02_scan_cleaned_inside_stl_range_ROBODK_MM_COLORED.ply"
    )

    # Store an important setting named COLORED_SCAN_OBJ_FOR_ROBODK.
    COLORED_SCAN_OBJ_FOR_ROBODK = (
        # This line helps the program do the next small step.
        EXPORT_FOLDER
        # Continue building the path or value.
        / "02_scan_cleaned_inside_stl_range_ROBODK_MM_COLORED.obj"
    )

    # Store an important setting named COLORED_SCAN_MTL_FOR_ROBODK.
    COLORED_SCAN_MTL_FOR_ROBODK = (
        # This line helps the program do the next small step.
        EXPORT_FOLDER
        # Continue building the path or value.
        / "02_scan_cleaned_inside_stl_range_ROBODK_MM_COLORED.mtl"
    )

    # Store an important setting named CAD_STL_FOR_ROBODK.
    CAD_STL_FOR_ROBODK = (
        # This line helps the program do the next small step.
        EXPORT_FOLDER
        # Continue building the path or value.
        / "04_aligned_cabinet_ROBODK_MM.stl"
    )

    # Store an important setting named VOXEL_SIZE_M.
    VOXEL_SIZE_M = 0.01
    # Store an important setting named COLOR_LEVELS.
    COLOR_LEVELS = 12

    # Create the print_paths function.
    def print_paths(self):
        # Show a message on the screen.
        print("")
        # Show a message on the screen.
        print("=" * 70)
        # Show a message on the screen.
        print("CONFIG PATH CHECK")
        # Show a message on the screen.
        print("=" * 70)

        # Show a message on the screen.
        print("Repository folder:")
        # Show a message on the screen.
        print(self.REPOSITORY_FOLDER)
        # Show a message on the screen.
        print("Exists:", self.REPOSITORY_FOLDER.exists())

        # Show a message on the screen.
        print("")
        # Show a message on the screen.
        print("Export folder:")
        # Show a message on the screen.
        print(self.EXPORT_FOLDER)
        # Show a message on the screen.
        print("Exists:", self.EXPORT_FOLDER.exists())

        # Show a message on the screen.
        print("")
        # Show a message on the screen.
        print("Cleaned scan PCD:")
        # Show a message on the screen.
        print(self.CLEANED_SCAN_PCD)
        # Show a message on the screen.
        print("Exists:", self.CLEANED_SCAN_PCD.exists())

        # Show a message on the screen.
        print("")
        # Show a message on the screen.
        print("Aligned CAD STL:")
        # Show a message on the screen.
        print(self.ALIGNED_CAD_STL)
        # Show a message on the screen.
        print("Exists:", self.ALIGNED_CAD_STL.exists())

        # Show a message on the screen.
        print("")
        # Show a message on the screen.
        print("Colored scan PLY output:")
        # Show a message on the screen.
        print(self.COLORED_SCAN_PLY_FOR_ROBODK)

        # Show a message on the screen.
        print("")
        # Show a message on the screen.
        print("Colored scan OBJ output:")
        # Show a message on the screen.
        print(self.COLORED_SCAN_OBJ_FOR_ROBODK)

        # Show a message on the screen.
        print("")
        # Show a message on the screen.
        print("Colored scan MTL output:")
        # Show a message on the screen.
        print(self.COLORED_SCAN_MTL_FOR_ROBODK)

        # Show a message on the screen.
        print("")
        # Show a message on the screen.
        print("CAD STL output:")
        # Show a message on the screen.
        print(self.CAD_STL_FOR_ROBODK)

        # Show a message on the screen.
        print("=" * 70)
        # Show a message on the screen.
        print("")
