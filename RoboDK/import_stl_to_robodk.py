import sys
from pathlib import Path

sys.path.append("C:/RoboDK/Python")

from robodk.robolink import *


ROBOTDK_EXPORT_FOLDER = Path(
    r"C:/Users/daryl/Desktop/Robotic D Environment Mapping/"
    r"Robotic-3D-Environment-Mapping/RoboDK Export"
)

CLEANED_SCAN_STL_FILE = (
    ROBOTDK_EXPORT_FOLDER / "02_scan_cleaned_inside_stl_range_ROBODK_MM.stl"
)

ALIGNED_CAD_STL_FILE = (
    ROBOTDK_EXPORT_FOLDER / "04_aligned_cabinet_ROBODK_MM.stl"
)


def import_file_to_robodk(rdk, file_path, item_name):
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    item = rdk.AddFile(str(file_path))

    if not item.Valid():
        raise Exception(f"Could not import file into RoboDK: {file_path}")

    item.setName(item_name)
    item.setVisible(True)

    return item


def main():
    rdk = Robolink()

    cleaned_scan = import_file_to_robodk(
        rdk,
        CLEANED_SCAN_STL_FILE,
        "Robot Base - Cleaned Scan Mesh"
    )

    aligned_cad = import_file_to_robodk(
        rdk,
        ALIGNED_CAD_STL_FILE,
        "Robot Base - Aligned Cabinet STL"
    )

    print("")
    print("=" * 70)
    print("IMPORTED INTO ROBODK")
    print("=" * 70)
    print(cleaned_scan.Name())
    print(aligned_cad.Name())
    print("")
    print("These STL files are scaled to millimeters for RoboDK.")
    print("They should appear in the robot base coordinate position.")


if __name__ == "__main__":
    main()