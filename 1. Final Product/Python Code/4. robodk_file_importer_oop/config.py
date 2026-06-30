# Bring in Path so the code can work with folder and file paths.
from pathlib import Path


# Store the expected name of the main project folder.
REPOSITORY_FOLDER_NAME = "Robotic-3D-Environment-Mapping"


# Create the is repository folder function.
def is_repository_folder(folder):


    # Check if this folder is missing or not really a folder.
    if not folder.exists() or not folder.is_dir():
        # Say no because this folder did not pass the check.
        return False

    # Check if the folder contains the final product folder.
    has_final_product = (folder / "1. Final Product").is_dir()
    # Check if the folder contains the CAD model folder.
    has_cad_model = (folder / "CAD Model").is_dir()

    # Return true only if the important repository folders exist.
    return has_final_product and has_cad_model


# Create the find repository folder function.
def find_repository_folder():


    # Save the full path of this Python file.
    current_file = Path(__file__).resolve()
    # Save the folder where this Python file is located.
    current_folder = current_file.parent


    # Look at each folder in this list of possible folders.
    for folder in [current_folder, *current_folder.parents]:
        # Check this condition before choosing the next step.
        if folder.name == REPOSITORY_FOLDER_NAME and is_repository_folder(folder):
            # Return the full clean path to this folder.
            return folder.resolve()


    # Look at each folder in this list of possible folders.
    for folder in [current_folder, *current_folder.parents]:
        # Check if this folder looks like the real project repository.
        if is_repository_folder(folder):
            # Return the full clean path to this folder.
            return folder.resolve()


    # Save the user's home folder.
    home_folder = Path.home()

    # Make a list of common places to search for the project.
    search_locations = [
        # Add this common Windows folder to the search list.
        home_folder / "Desktop",
        # Add this common Windows folder to the search list.
        home_folder / "OneDrive" / "Desktop",
        # Add this common Windows folder to the search list.
        home_folder / "Documents",
        # Add this common Windows folder to the search list.
        home_folder / "Downloads",
        # Add this value to the current list or function call.
        home_folder,
    ]

    # Try each common place where the project might be stored.
    for search_location in search_locations:
        # Skip this search place if the folder does not exist.
        if not search_location.exists():
            # Skip to the next item in the loop.
            continue

        # Build a direct path to the expected repository folder.
        direct_repository = search_location / REPOSITORY_FOLDER_NAME

        # Check if this folder looks like the real project repository.
        if is_repository_folder(direct_repository):
            # Run this line as one small step in the program.
            return direct_repository.resolve()

        # Try this code because it might fail on some folders.
        try:
            # Search inside this place for a repository folder with the expected name.
            for repository_candidate in search_location.rglob(REPOSITORY_FOLDER_NAME):
                # Check if this folder looks like the real project repository.
                if is_repository_folder(repository_candidate):
                    # Run this line as one small step in the program.
                    return repository_candidate.resolve()

        # Ignore folders that Windows does not allow this script to read.
        except PermissionError:
            # Skip to the next item in the loop.
            continue

    # Stop the program because an important file or folder is missing.
    raise FileNotFoundError(
        # Run this line as one small step in the program.
        "Could not find the main repository folder.\n\n"
        # Run this line as one small step in the program.
        "Expected a folder that contains:\n"
        # Run this line as one small step in the program.
        "- 1. Final Product\n"
        # Run this line as one small step in the program.
        "- CAD Model\n\n"
        # Run this line as one small step in the program.
        "Example correct path:\n"
        # Run this line as one small step in the program.
        "C:\\Users\\daryl\\Desktop\\Robotic D Environment Mapping\\"
        # Run this line as one small step in the program.
        "Robotic-3D-Environment-Mapping"
    )


# Create the find robodk export folder function.
def find_robodk_export_folder(repository_folder):


    # Store the expected colored OBJ filename.
    colored_scan_obj = "02_scan_cleaned_inside_stl_range_ROBODK_MM_COLORED.obj"
    # Store the expected colored PLY filename.
    colored_scan_ply = "02_scan_cleaned_inside_stl_range_ROBODK_MM_COLORED.ply"
    # Store the expected aligned CAD STL filename.
    aligned_cad_stl = "04_aligned_cabinet_ROBODK_MM.stl"

    # Build the path to the Python Code folder.
    python_code_folder = (
        # Run this line as one small step in the program.
        repository_folder
        # Join this folder name onto the path.
        / "1. Final Product"
        # Join this folder name onto the path.
        / "Python Code"
    )

    # List the folders where the RoboDK export files might be.
    candidate_folders = [
        # Build a path inside the repository folder.
        repository_folder / "RoboDK Export",
        # Add this value to the current list or function call.
        python_code_folder / "2. robodk_scan_alignment" / "RoboDK Export",
        # Add this value to the current list or function call.
        python_code_folder / "3. robodk_export_converter" / "RoboDK Export",
    ]

    # Look at each folder in this list of possible folders.
    for folder in candidate_folders:
        # Check if this folder contains a colored scan file.
        has_colored_scan = (
            # Run this line as one small step in the program.
            (folder / colored_scan_obj).exists()
            # Also accept this second option as part of the same check.
            or (folder / colored_scan_ply).exists()
        )

        # Check if this folder contains the aligned CAD file.
        has_aligned_cad = (folder / aligned_cad_stl).exists()

        # Accept this folder if it has both the scan and CAD files.
        if has_colored_scan and has_aligned_cad:
            # Return the full clean path to this folder.
            return folder.resolve()

    # Stop the program because an important file or folder is missing.
    raise FileNotFoundError(
        # Run this line as one small step in the program.
        "Could not find the RoboDK Export folder.\n\n"
        # Run this line as one small step in the program.
        "Expected these files:\n"
        # Run this line as one small step in the program.
        f"- {colored_scan_obj} or {colored_scan_ply}\n"
        # Run this line as one small step in the program.
        f"- {aligned_cad_stl}\n\n"
        # Run this line as one small step in the program.
        "Checked folders:\n"
        # Add this text to the error message.
        + "\n".join(str(folder) for folder in candidate_folders)
        # Add this text to the error message.
        + "\n\n"
        # Run this line as one small step in the program.
        "Fix:\n"
        # Run this line as one small step in the program.
        "Run the third script first: 3. robodk_export_converter. "
        # Run this line as one small step in the program.
        "That script creates the colored OBJ/PLY and millimeter STL files."
    )


# Create the Config class to group related steps together.
class Config:


    # Find and save the main repository folder.
    REPOSITORY_FOLDER = find_repository_folder()

    # Find and save the folder that contains files ready for RoboDK.
    ROBODK_EXPORT_FOLDER = find_robodk_export_folder(REPOSITORY_FOLDER)


    # Save the path to the colored scan OBJ file.
    COLORED_SCAN_OBJ_FILE = (
        # Save this important path as a setting.
        ROBODK_EXPORT_FOLDER
        # Join this folder name onto the path.
        / "02_scan_cleaned_inside_stl_range_ROBODK_MM_COLORED.obj"
    )

    # Save the path to the color material file used by the OBJ file.
    COLORED_SCAN_MTL_FILE = (
        # Save this important path as a setting.
        ROBODK_EXPORT_FOLDER
        # Join this folder name onto the path.
        / "02_scan_cleaned_inside_stl_range_ROBODK_MM_COLORED.mtl"
    )

    # Save the path to the colored scan PLY backup file.
    COLORED_SCAN_PLY_FILE = (
        # Save this important path as a setting.
        ROBODK_EXPORT_FOLDER
        # Join this folder name onto the path.
        / "02_scan_cleaned_inside_stl_range_ROBODK_MM_COLORED.ply"
    )

    # Save the path to the aligned CAD STL file.
    ALIGNED_CAD_STL_FILE = (
        # Save this important path as a setting.
        ROBODK_EXPORT_FOLDER
        # Join this folder name onto the path.
        / "04_aligned_cabinet_ROBODK_MM.stl"
    )


    # Choose the name RoboDK will show for the scan item.
    SCAN_ITEM_NAME = "Robot Base - Colored Cleaned Scan Mesh"
    # Choose the name RoboDK will show for the CAD item.
    CAD_ITEM_NAME = "Robot Base - Aligned Cabinet STL"


    # Set the CAD color to transparent red.
    CAD_COLOR = [1.0, 0.0, 0.0, 0.35]


    # Create the print paths function.
    def print_paths(self):
        # Show this helpful message on the screen.
        print("")
        # Show this helpful message on the screen.
        print("=" * 70)
        # Show this helpful message on the screen.
        print("CONFIG PATH CHECK")
        # Show this helpful message on the screen.
        print("=" * 70)

        # Show this helpful message on the screen.
        print("Repository folder:")
        # Show this helpful message on the screen.
        print(self.REPOSITORY_FOLDER)
        # Show this helpful message on the screen.
        print("Exists:", self.REPOSITORY_FOLDER.exists())

        # Show this helpful message on the screen.
        print("")
        # Show this helpful message on the screen.
        print("RoboDK Export folder:")
        # Show this helpful message on the screen.
        print(self.ROBODK_EXPORT_FOLDER)
        # Show this helpful message on the screen.
        print("Exists:", self.ROBODK_EXPORT_FOLDER.exists())

        # Show this helpful message on the screen.
        print("")
        # Show this helpful message on the screen.
        print("Colored scan OBJ:")
        # Show this helpful message on the screen.
        print(self.COLORED_SCAN_OBJ_FILE)
        # Show this helpful message on the screen.
        print("Exists:", self.COLORED_SCAN_OBJ_FILE.exists())

        # Show this helpful message on the screen.
        print("")
        # Show this helpful message on the screen.
        print("Colored scan MTL:")
        # Show this helpful message on the screen.
        print(self.COLORED_SCAN_MTL_FILE)
        # Show this helpful message on the screen.
        print("Exists:", self.COLORED_SCAN_MTL_FILE.exists())

        # Show this helpful message on the screen.
        print("")
        # Show this helpful message on the screen.
        print("Colored scan PLY:")
        # Show this helpful message on the screen.
        print(self.COLORED_SCAN_PLY_FILE)
        # Show this helpful message on the screen.
        print("Exists:", self.COLORED_SCAN_PLY_FILE.exists())

        # Show this helpful message on the screen.
        print("")
        # Show this helpful message on the screen.
        print("Aligned CAD STL:")
        # Show this helpful message on the screen.
        print(self.ALIGNED_CAD_STL_FILE)
        # Show this helpful message on the screen.
        print("Exists:", self.ALIGNED_CAD_STL_FILE.exists())

        # Show this helpful message on the screen.
        print("=" * 70)
        # Show this helpful message on the screen.
        print("")
