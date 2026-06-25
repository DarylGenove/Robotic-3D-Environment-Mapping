from pathlib import Path


class Config:
    ROBOTDK_EXPORT_FOLDER = Path(
        r"C:/Users/daryl/Desktop/Robotic D Environment Mapping/"
        r"Robotic-3D-Environment-Mapping/RoboDK Export"
    )

    COLORED_SCAN_OBJ_FILE = (
        ROBOTDK_EXPORT_FOLDER / "02_scan_cleaned_inside_stl_range_ROBODK_MM_COLORED.obj"
    )

    COLORED_SCAN_MTL_FILE = (
        ROBOTDK_EXPORT_FOLDER / "02_scan_cleaned_inside_stl_range_ROBODK_MM_COLORED.mtl"
    )

    COLORED_SCAN_PLY_FILE = (
        ROBOTDK_EXPORT_FOLDER / "02_scan_cleaned_inside_stl_range_ROBODK_MM_COLORED.ply"
    )

    ALIGNED_CAD_STL_FILE = (
        ROBOTDK_EXPORT_FOLDER / "04_aligned_cabinet_ROBODK_MM.stl"
    )

    SCAN_ITEM_NAME = "Robot Base - Colored Cleaned Scan Mesh"
    CAD_ITEM_NAME = "Robot Base - Aligned Cabinet STL"

    CAD_COLOR = [1.0, 0.0, 0.0, 0.35]
