# Bring in copy so this file can use it.
import copy
# Bring in open3d so this file can use it.
import open3d as o3d


# Create the Visualizer class, which groups related code together.
class Visualizer:


    # Create the colorize function.
    def colorize(self, point_cloud, color):
        # Make a safe copy so the original object does not change.
        colored_point_cloud = copy.deepcopy(point_cloud)
        # Give the whole point cloud one color.
        colored_point_cloud.paint_uniform_color(color)
        # Send this result back to the part of the code that asked for it.
        return colored_point_cloud

    # Create the show before icp function.
    def show_before_icp(self, scan_structured, cad_initial):
        # Save a value in geometries.
        geometries = [
            # Add this value to the current group.
            self.colorize(scan_structured, [0.1, 0.7, 1.0]),
            # Add this value to the current group.
            self.colorize(cad_initial, [1.0, 0.0, 0.0]),
        ]

        # Open a 3D window to show the scan and CAD model.
        o3d.visualization.draw_geometries(
            # Add this value to the current group.
            geometries,
            # Save a value in window name.
            window_name="Structured Scan vs CAD Before ICP"
        )

    # Create the show final result function.
    def show_final_result(self, scan_filtered, cad_final):
        # Save a value in geometries.
        geometries = [
            # Add this value to the current group.
            self.colorize(scan_filtered, [0.1, 0.7, 1.0]),
            # Add this value to the current group.
            self.colorize(cad_final, [1.0, 0.0, 0.0]),
        ]

        # Open a 3D window to show the scan and CAD model.
        o3d.visualization.draw_geometries(
            # Add this value to the current group.
            geometries,
            # Save a value in window name.
            window_name="Cleaned Scan Inside CAD Bounds"
        )
