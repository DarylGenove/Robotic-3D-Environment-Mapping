from pathlib import Path


class Config:
    EXPORT_FOLDER = Path(
        r"C:/Users/daryl/Desktop/Robotic D Environment Mapping/"
        r"Robotic-3D-Environment-Mapping/RoboDK Export"
    )

    CLEANED_SCAN_PCD = EXPORT_FOLDER / "02_scan_cleaned_inside_stl_range_ROBODK.pcd"
    ALIGNED_CAD_STL = EXPORT_FOLDER / "04_aligned_cabinet_ROBODK.stl"

    COLORED_SCAN_PLY_FOR_ROBODK = (
        EXPORT_FOLDER / "02_scan_cleaned_inside_stl_range_ROBODK_MM_COLORED.ply"
    )

    COLORED_SCAN_OBJ_FOR_ROBODK = (
        EXPORT_FOLDER / "02_scan_cleaned_inside_stl_range_ROBODK_MM_COLORED.obj"
    )

    COLORED_SCAN_MTL_FOR_ROBODK = (
        EXPORT_FOLDER / "02_scan_cleaned_inside_stl_range_ROBODK_MM_COLORED.mtl"
    )

    CAD_STL_FOR_ROBODK = EXPORT_FOLDER / "04_aligned_cabinet_ROBODK_MM.stl"

    VOXEL_SIZE_M = 0.01
    COLOR_LEVELS = 12
