import numpy as np
import open3d as o3d

from config import Config
from point_cloud_processor import PointCloudProcessor
from plane_detector import PlaneDetector
from scan_aligner import ScanAligner
from scan_filter import ScanFilter
from deviation_reporter import DeviationReporter
from visualizer import Visualizer


def main():
    config = Config()

    processor = PointCloudProcessor(config)
    plane_detector = PlaneDetector(config)
    aligner = ScanAligner(config, plane_detector)
    scan_filter = ScanFilter(config)
    deviation_reporter = DeviationReporter(plane_detector)
    visualizer = Visualizer()

    scan_raw = processor.load_scan()
    scan_down = processor.preprocess(scan_raw)

    cad_raw = processor.load_cad_as_point_cloud()
    cad_down = processor.preprocess(cad_raw)

    scan_structured, structured_transform = aligner.structure_scan(scan_down)

    cad_initial, center_transform = aligner.center_align_cad(
        scan_structured,
        cad_down
    )

    visualizer.show_before_icp(scan_structured, cad_initial)

    cad_final, icp_transform = aligner.run_icp(
        cad_initial,
        scan_structured
    )

    print("Removing scan points outside CAD outer bounds...")

    scan_filtered = scan_filter.remove_scan_points_outside_cad_bounds(
        scan_structured,
        cad_final
    )

    deviation_reporter.print_room_deviation_report(
        scan_filtered,
        cad_final
    )

    if config.SAVE_CLEANED_SCAN:
        o3d.io.write_point_cloud(config.CLEANED_SCAN_FILE, scan_filtered)
        print("Cleaned scan saved to:", config.CLEANED_SCAN_FILE)

    visualizer.show_final_result(scan_filtered, cad_final)

    final_transform = icp_transform @ center_transform

    print("Final CAD-to-structured-scan transform:")
    print(final_transform)


if __name__ == "__main__":
    main()