import sys
from pathlib import Path


PROJECT_FOLDER = Path(
    r"C:\Users\daryl\Desktop\Robotic D Environment Mapping\Robotic-3D-Environment-Mapping\1. Final Product\Python Code\4. robodk_file_importer_oop"
)

CURRENT_FOLDER = Path(__file__).resolve().parent

if PROJECT_FOLDER.exists():
    sys.path.insert(0, str(PROJECT_FOLDER))
else:
    sys.path.insert(0, str(CURRENT_FOLDER))

from config import Config
from file_validator import FileValidator
from robodk_import_service import RoboDKImportService
from robodk_item_service import RoboDKItemService


def main():
    config = Config()

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
