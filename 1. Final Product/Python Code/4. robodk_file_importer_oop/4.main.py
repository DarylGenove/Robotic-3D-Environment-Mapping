# Bring in sys so Python can change where it looks for project files.
import sys
# Bring in Path so the code can work with folder and file paths.
from pathlib import Path


# Store the expected name of the main project folder.
REPOSITORY_FOLDER_NAME = "Robotic-3D-Environment-Mapping"

# Store the name of this Python project folder.
PROJECT_FOLDER_NAME = "4. robodk_file_importer_oop"

# Build the path from the repository folder to this script folder.
PROJECT_RELATIVE_FOLDER = (
    # Run this line as one small step in the program.
    Path("1. Final Product")
    # Join this folder name onto the path.
    / "Python Code"
    # Join this folder name onto the path.
    / PROJECT_FOLDER_NAME
)

# List the files that must exist before this folder is accepted.
REQUIRED_PROJECT_FILES = [
    # Add this value to the current list or function call.
    "config.py",
    # Add this value to the current list or function call.
    "file_validator.py",
    # Add this value to the current list or function call.
    "robodk_import_service.py",
    # Add this value to the current list or function call.
    "robodk_item_service.py",
]


# Create the is correct project folder function.
def is_correct_project_folder(folder):


    # Check if this folder is missing or not really a folder.
    if not folder.exists() or not folder.is_dir():
        # Say no because this folder did not pass the check.
        return False

    # Return true only if every required file exists.
    return all(
        # Run this line as one small step in the program.
        (folder / file_name).exists()
        # Run this line as one small step in the program.
        for file_name in REQUIRED_PROJECT_FILES
    )


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


# Create the get project folder from repository function.
def get_project_folder_from_repository(repository_folder):
    # Return the project folder inside the repository.
    return repository_folder / PROJECT_RELATIVE_FOLDER


# Create the find repository from folder function.
def find_repository_from_folder(start_folder):


    # Look at each folder in this list of possible folders.
    for folder in [start_folder, *start_folder.parents]:
        # Check if this folder looks like the real project repository.
        if is_repository_folder(folder):
            # Return the full clean path to this folder.
            return folder.resolve()

    # Say that nothing useful was found.
    return None


# Create the find project folder function.
def find_project_folder():


    # Save the full path of this Python file.
    current_file = Path(__file__).resolve()
    # Save the folder where this Python file is located.
    current_folder = current_file.parent
    # Save the folder where Python is currently running.
    working_folder = Path.cwd().resolve()
    # Save the user's home folder.
    home_folder = Path.home()


    # Search upward from this folder to find the repository.
    repository_folder = find_repository_from_folder(current_folder)

    # Check if a repository folder was found.
    if repository_folder is not None:
        # Build the expected project folder path from the repository.
        project_folder = get_project_folder_from_repository(repository_folder)

        # Check if this folder contains the correct Python files.
        if is_correct_project_folder(project_folder):
            # Return the full clean path to the project folder.
            return project_folder.resolve()


    # Search upward from this folder to find the repository.
    repository_folder = find_repository_from_folder(working_folder)

    # Check if a repository folder was found.
    if repository_folder is not None:
        # Build the expected project folder path from the repository.
        project_folder = get_project_folder_from_repository(repository_folder)

        # Check if this folder contains the correct Python files.
        if is_correct_project_folder(project_folder):
            # Return the full clean path to the project folder.
            return project_folder.resolve()


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
        # Build a direct path to this project folder.
        direct_project = get_project_folder_from_repository(direct_repository)

        # Check if this folder looks like the real project repository.
        if is_repository_folder(direct_repository) and is_correct_project_folder(direct_project):
            # Return the direct project folder because it is correct.
            return direct_project.resolve()


        # Try this code because it might fail on some folders.
        try:
            # Search inside this place for a repository folder with the expected name.
            for repository_candidate in search_location.rglob(REPOSITORY_FOLDER_NAME):
                # Build the expected project folder path from the repository.
                project_folder = get_project_folder_from_repository(repository_candidate)

                # Check if this folder looks like the real project repository.
                if is_repository_folder(repository_candidate) and is_correct_project_folder(project_folder):
                    # Return the full clean path to the project folder.
                    return project_folder.resolve()

        # Ignore folders that Windows does not allow this script to read.
        except PermissionError:
            # Skip to the next item in the loop.
            continue


    # Try each common place where the project might be stored.
    for search_location in search_locations:
        # Skip this search place if the folder does not exist.
        if not search_location.exists():
            # Skip to the next item in the loop.
            continue

        # Try this code because it might fail on some folders.
        try:
            # Search inside this place for a matching project folder.
            for project_candidate in search_location.rglob(PROJECT_FOLDER_NAME):
                # Check this condition before choosing the next step.
                if not is_correct_project_folder(project_candidate):
                    # Skip to the next item in the loop.
                    continue

                # Search upward from this folder to find the repository.
                repository_folder = find_repository_from_folder(project_candidate)

                # Check if no repository folder was found for this candidate.
                if repository_folder is None:
                    # Skip to the next item in the loop.
                    continue

                # Build the project path that should match the candidate.
                expected_project_folder = get_project_folder_from_repository(repository_folder)

                # Check if this candidate is exactly the expected project folder.
                if project_candidate.resolve() == expected_project_folder.resolve():
                    # Return this found project folder because it is correct.
                    return project_candidate.resolve()

        # Ignore folders that Windows does not allow this script to read.
        except PermissionError:
            # Skip to the next item in the loop.
            continue

    # Stop the program because an important file or folder is missing.
    raise FileNotFoundError(
        # Run this line as one small step in the program.
        "Could not find the correct RoboDK file importer project folder.\n\n"
        # Run this line as one small step in the program.
        "Expected repository structure:\n"
        # Run this line as one small step in the program.
        f"{REPOSITORY_FOLDER_NAME}\\1. Final Product\\Python Code\\{PROJECT_FOLDER_NAME}\n"
        # Run this line as one small step in the program.
        f"{REPOSITORY_FOLDER_NAME}\\CAD Model\n"
        # Run this line as one small step in the program.
        f"{REPOSITORY_FOLDER_NAME}\\RoboDK Export\n\n"
        # Run this line as one small step in the program.
        "Example correct path:\n"
        # Run this line as one small step in the program.
        "C:\\Users\\daryl\\Desktop\\Robotic D Environment Mapping\\"
        # Run this line as one small step in the program.
        "Robotic-3D-Environment-Mapping\\1. Final Product\\Python Code\\"
        # Run this line as one small step in the program.
        f"{PROJECT_FOLDER_NAME}\n\n"
        # Run this line as one small step in the program.
        "Fix:\n"
        # Run this line as one small step in the program.
        "Use the project inside Robotic-3D-Environment-Mapping, not a duplicate folder outside it."
    )


# Find and save the correct project folder.
PROJECT_FOLDER = find_project_folder()


# Start a clean list of Python import folders.
cleaned_sys_path = []

# Go through every folder where Python currently searches for imports.
for path in sys.path:
    # Try this code because it might fail on some folders.
    try:
        # Keep paths that are not the selected project folder.
        if Path(path).resolve() != PROJECT_FOLDER:
            # Run this line as one small step in the program.
            cleaned_sys_path.append(path)
    # Handle any path problem without stopping the cleanup.
    except Exception:
        # Run this line as one small step in the program.
        cleaned_sys_path.append(path)

# Replace Python's search list with the cleaned one.
sys.path = cleaned_sys_path
# Put the correct project folder first for imports.
sys.path.insert(0, str(PROJECT_FOLDER))


# Go through each module name that might be cached from an old run.
for module_name in [
    # Add this value to the current list or function call.
    "config",
    # Add this value to the current list or function call.
    "file_validator",
    # Add this value to the current list or function call.
    "robodk_import_service",
    # Add this value to the current list or function call.
    "robodk_item_service",
# Run this line as one small step in the program.
]:
    # Forget this old module so Python loads the correct file again.
    sys.modules.pop(module_name, None)

# Show this helpful message on the screen.
print("")
# Show this helpful message on the screen.
print("=" * 70)
# Show this helpful message on the screen.
print("Using project folder:")
# Show this helpful message on the screen.
print(PROJECT_FOLDER)
# Show this helpful message on the screen.
print("=" * 70)
# Show this helpful message on the screen.
print("")


# Bring in the settings class from config.py.
from config import Config
# Bring in the helper that checks if needed files exist.
from file_validator import FileValidator
# Bring in the service that imports the scan and CAD into RoboDK.
from robodk_import_service import RoboDKImportService
# Bring in the helper that creates, deletes, and colors RoboDK items.
from robodk_item_service import RoboDKItemService


# Create the main function that starts the whole script.
def main():
    # Create the settings object.
    config = Config()

    # Check if the config object has a path-printing helper.
    if hasattr(config, "print_paths"):
        # Print all important paths so the user can check them.
        config.print_paths()

    # Create the helper that checks input files.
    file_validator = FileValidator()
    # Create the helper that talks to RoboDK items.
    robodk_item_service = RoboDKItemService()

    # Create the main service that performs the import.
    robodk_import_service = RoboDKImportService(
        # Add this value to the current list or function call.
        config,
        # Add this value to the current list or function call.
        file_validator,
        # Run this line as one small step in the program.
        robodk_item_service
    )

    # Start the import process.
    robodk_import_service.run()


# Run main only when this file is started directly.
if __name__ == "__main__":
    # Run this line as one small step in the program.
    main()
