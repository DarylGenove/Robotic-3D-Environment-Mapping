import sys  # Loads sys so the code can change where Python looks for files.
from pathlib import Path  # Loads Path so file and folder paths are easier to handle.

PROJECT_FOLDER = Path(  # Stores PROJECT FOLDER for use in the next steps.
    r"C:\Users\daryl\OneDrive\Desktop\Robotic D Environment Mapping\Robotic-3D-Environment-Mapping\1. Final Product\Python Code\1. adaptive_inside_box_scanner"  # Runs this line as one small step in the program.
).resolve()  # Turns the path into a full absolute path.

if not PROJECT_FOLDER.exists():  # Checks if this condition is not true.
    raise FileNotFoundError(f"Project folder not found: {PROJECT_FOLDER}")  # Stops the program because something important went wrong.

project_folder_string = str(PROJECT_FOLDER)  # Stores the project folder path as text.

if project_folder_string in sys.path:  # Checks a condition before running the next indented lines.
    sys.path.remove(project_folder_string)  # Removes an old project folder from Python search paths.

sys.path.insert(0, project_folder_string)  # Adds the project folder to the front of Python search paths.

wrong_config_module = sys.modules.get("config")  # Stores wrong config module for use in the next steps.

if wrong_config_module is not None:  # Checks if this value exists before using it.
    loaded_from = getattr(wrong_config_module, "__file__", "")  # Stores the file path of the config module Python already loaded.

    if loaded_from:  # Checks a condition before running the next indented lines.
        loaded_from_path = Path(loaded_from).resolve()  # Stores that config path as a Path object.
        correct_config_path = PROJECT_FOLDER / "config.py"  # Stores the config path this project should use.

        if loaded_from_path != correct_config_path:  # Checks a condition before running the next indented lines.
            del sys.modules["config"]  # Deletes this saved value so Python can load the correct one later.

from config import Config  # Gets Config from config so this file can use it.
from scanning_service import AdaptiveInsideBoxScanner  # Gets AdaptiveInsideBoxScanner from scanning_service so this file can use it.


def main():  # Starts the scanner program.
    config = Config()  # Stores the scanner settings so the program can use them.
    scanner = AdaptiveInsideBoxScanner(config)  # Creates the scanner object that controls the whole scan.
    scanner.run()  # Runs this line as one small step in the program.


if __name__ == "__main__":  # Runs main only when this file is started directly.
    main()  # Runs this line as one small step in the program.
