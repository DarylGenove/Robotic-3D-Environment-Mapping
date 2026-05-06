import copy
import open3d as o3d


class Visualizer:
    """
    Handles Open3D visualization.
    """

    def colorize(self, point_cloud, color):
        colored_point_cloud = copy.deepcopy(point_cloud)
        colored_point_cloud.paint_uniform_color(color)
        return colored_point_cloud

    def show_before_icp(self, scan_structured, cad_initial):
        geometries = [
            self.colorize(scan_structured, [0.1, 0.7, 1.0]),
            self.colorize(cad_initial, [1.0, 0.0, 0.0]),
        ]

        o3d.visualization.draw_geometries(
            geometries,
            window_name="Structured Scan vs CAD Before ICP"
        )

    def show_final_result(self, scan_filtered, cad_final):
        geometries = [
            self.colorize(scan_filtered, [0.1, 0.7, 1.0]),
            self.colorize(cad_final, [1.0, 0.0, 0.0]),
        ]

        o3d.visualization.draw_geometries(
            geometries,
            window_name="Cleaned Scan Inside CAD Bounds"
        )