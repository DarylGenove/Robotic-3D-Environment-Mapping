import sys
from pathlib import Path


PROJECT_FOLDER = Path(
    r"C:\Users\daryl\Desktop\Robotic D Environment Mapping\Robotic-3D-Environment-Mapping\1. Final Product\Python Code\3. robodk_export_converter"
)

CURRENT_FOLDER = Path(__file__).resolve().parent

if PROJECT_FOLDER.exists():
    sys.path.insert(0, str(PROJECT_FOLDER))
else:
    sys.path.insert(0, str(CURRENT_FOLDER))

from cad_exporter import CadExporter
from colored_scan_exporter import ColoredScanExporter
from colored_voxel_obj_writer import ColoredVoxelObjWriter
from color_material_service import ColorMaterialService
from config import Config
from point_cloud_scaler import PointCloudScaler
from robodk_conversion_service import RoboDKConversionService


def main():
    config = Config()

    point_cloud_scaler = PointCloudScaler()
    color_material_service = ColorMaterialService()

    colored_voxel_obj_writer = ColoredVoxelObjWriter(
        color_material_service
    )

    colored_scan_exporter = ColoredScanExporter(
        point_cloud_scaler,
        colored_voxel_obj_writer
    )

    cad_exporter = CadExporter(
        point_cloud_scaler
    )

    conversion_service = RoboDKConversionService(
        config,
        colored_scan_exporter,
        cad_exporter
    )

    conversion_service.run()


if __name__ == "__main__":
    main()
