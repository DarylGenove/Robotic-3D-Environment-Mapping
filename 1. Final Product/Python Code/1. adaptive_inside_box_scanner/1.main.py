import sys
from pathlib import Path

# Change this path to the real Windows folder where you save these OOP files.
# RoboDK sometimes runs main.py from AppData\Local\Temp, so this path helps
# Python find config.py and the other class files.
PROJECT_FOLDER = Path(
    r"C:\Users\daryl\Desktop\Robotic D Environment Mapping\Robotic-3D-Environment-Mapping\1. Final Product\Python Code\1. adaptive_inside_box_scanner"
)

if PROJECT_FOLDER.exists():
    sys.path.insert(0, str(PROJECT_FOLDER))
else:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import Config
from scanning_service import AdaptiveInsideBoxScanner


def main():
    config = Config()
    scanner = AdaptiveInsideBoxScanner(config)
    scanner.run()


if __name__ == "__main__":
    main()
