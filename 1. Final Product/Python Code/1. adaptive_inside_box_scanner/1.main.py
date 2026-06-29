import sys
from pathlib import Path

PROJECT_FOLDER = Path(
    r"C:\Users\daryl\OneDrive\Desktop\Robotic D Environment Mapping\Robotic-3D-Environment-Mapping\1. Final Product\Python Code\1. adaptive_inside_box_scanner"
).resolve()

if not PROJECT_FOLDER.exists():
    raise FileNotFoundError(f"Project folder not found: {PROJECT_FOLDER}")

project_folder_string = str(PROJECT_FOLDER)

if project_folder_string in sys.path:
    sys.path.remove(project_folder_string)

sys.path.insert(0, project_folder_string)

wrong_config_module = sys.modules.get("config")

if wrong_config_module is not None:
    loaded_from = getattr(wrong_config_module, "__file__", "")

    if loaded_from:
        loaded_from_path = Path(loaded_from).resolve()
        correct_config_path = PROJECT_FOLDER / "config.py"

        if loaded_from_path != correct_config_path:
            del sys.modules["config"]

from config import Config
from scanning_service import AdaptiveInsideBoxScanner


def main():
    config = Config()
    scanner = AdaptiveInsideBoxScanner(config)
    scanner.run()


if __name__ == "__main__":
    main()