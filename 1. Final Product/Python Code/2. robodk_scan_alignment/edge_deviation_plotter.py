# Import NumPy.
# NumPy is used here for working with arrays and calculating min/max axis ranges.
import numpy as np

# Import Matplotlib's pyplot module.
# This is used to create and display the 3D graph.
import matplotlib.pyplot as plt

# Import Poly3DCollection.
# This is used to draw 3D polygon surfaces, such as transparent box faces.
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


# Define a class called EdgeDeviationPlotter.
# This class is responsible for visualizing the difference between
# a CAD/STL model and a scanned PCD point cloud.
class EdgeDeviationPlotter:
    """
    Creates a 3D visual explanation of the edge/corner deviation between
    the CAD/STL model and the PCD scan.

    Blue wireframe  = PCD/scan edges
    Black wireframe = CAD/STL edges
    Red arrows      = difference between CAD corners and scan corners
    """

    # Constructor method.
    # This runs when an EdgeDeviationPlotter object is created.
    def __init__(self, scale_to_mm=True):
        # Store whether points should be converted from metres to millimetres.
        # By default, this is True.
        self.scale_to_mm = scale_to_mm

    # Method for scaling a point.
    # This is used to convert point coordinates from metres to millimetres.
    def scale_point(self, point):
        # If scale_to_mm is True, convert the point from metres to millimetres.
        if self.scale_to_mm:
            # Multiply the whole point by 1000.
            # Example: 0.5 m becomes 500 mm.
            return point * 1000.0

        # If scale_to_mm is False, return the original point without conversion.
        return point

    # Method for building the 6 faces of a box from 8 corner points.
    # The input "corners" is a dictionary containing the 8 box corners.
    def build_box_faces(self, corners):
        # Return a list of 6 faces.
        # Each face is made from 4 corner points.
        return [
            # Face 1: bottom face of the box.
            # All points have Z-min, so they are on the bottom plane.0
            # The order 1 → 2 → 4 → 3 goes around the rectangle correctly.
            [
                corners["1. X-min Y-min Z-min"],
                corners["2. X-max Y-min Z-min"],
                corners["4. X-max Y-max Z-min"],
                corners["3. X-min Y-max Z-min"],
            ],

            # Face 2: top face of the box.
            # All points have Z-max, so they are on the top plane.
            [
                corners["5. X-min Y-min Z-max"],
                corners["6. X-max Y-min Z-max"],
                corners["8. X-max Y-max Z-max"],
                corners["7. X-min Y-max Z-max"],
            ],

            # Face 3: side face at Y-min.
            # This connects the bottom Y-min edge to the top Y-min edge.
            [
                corners["1. X-min Y-min Z-min"],
                corners["2. X-max Y-min Z-min"],
                corners["6. X-max Y-min Z-max"],
                corners["5. X-min Y-min Z-max"],
            ],

            # Face 4: side face at Y-max.
            # This connects the bottom Y-max edge to the top Y-max edge.
            [
                corners["3. X-min Y-max Z-min"],
                corners["4. X-max Y-max Z-min"],
                corners["8. X-max Y-max Z-max"],
                corners["7. X-min Y-max Z-max"],
            ],

            # Face 5: side face at X-min.
            # This connects the bottom X-min edge to the top X-min edge.
            [
                corners["1. X-min Y-min Z-min"],
                corners["3. X-min Y-max Z-min"],
                corners["7. X-min Y-max Z-max"],
                corners["5. X-min Y-min Z-max"],
            ],

            # Face 6: side face at X-max.
            # This connects the bottom X-max edge to the top X-max edge.
            [
                corners["2. X-max Y-min Z-min"],
                corners["4. X-max Y-max Z-min"],
                corners["8. X-max Y-max Z-max"],
                corners["6. X-max Y-min Z-max"],
            ],
        ]

    # Method for drawing edge lines in the 3D graph.
    # It can draw either CAD edges or PCD scan edges.
    def plot_edges(self, ax, edges, color, line_style, label):
        # This variable is used to make sure the legend label is only added once.
        # Without this, every edge would create a duplicate legend entry.
        first_line = True

        # Loop through every edge in the edges dictionary.
        # The underscore "_" means we do not use the edge name.
        # We only need the edge start and end points.
        for _, edge in edges.items():
            # Get the first point of the edge and scale it if needed.
            start_point = self.scale_point(edge[0])

            # Get the second point of the edge and scale it if needed.
            end_point = self.scale_point(edge[1])

            # Draw one 3D line between the start point and end point.
            ax.plot(
                # X coordinates: start X to end X.
                [start_point[0], end_point[0]],

                # Y coordinates: start Y to end Y.
                [start_point[1], end_point[1]],

                # Z coordinates: start Z to end Z.
                [start_point[2], end_point[2]],

                # Set the line color.
                # Example: black for CAD, blue for PCD.
                color=color,

                # Set the line style.
                # Example: "-" for solid, "--" for dashed.
                linestyle=line_style,

                # Set the line thickness.
                linewidth=2,

                # Add the label only for the first line.
                # This avoids duplicate labels in the legend.
                label=label if first_line else None
            )

            # After the first edge is drawn, set first_line to False.
            # The remaining edges will not add another legend label.
            first_line = False

    # Method for drawing corner points in the 3D graph.
    # It can draw either CAD corners or PCD scan corners.
    def plot_corners(self, ax, corners, color):
        # Loop through every corner in the corners dictionary.
        # The underscore "_" means we do not use the corner label here.
        for _, corner in corners.items():
            # Scale the corner point if needed.
            point = self.scale_point(corner)

            # Draw the corner as a visible dot in the 3D plot.
            ax.scatter(
                # X coordinate of the point.
                point[0],

                # Y coordinate of the point.
                point[1],

                # Z coordinate of the point.
                point[2],

                # Color of the corner point.
                # Example: yellow for CAD, cyan for PCD.
                color=color,

                # Size of the point.
                s=45,

                # Add a black border around the point so it is easier to see.
                edgecolors="black",

                # Draw the point above other objects.
                zorder=5
            )

    # Method for drawing red arrows between CAD corners and PCD scan corners.
    # These arrows show the corner deviation.
    def plot_corner_arrows(self, ax, scan_corners, cad_corners):
        # This variable is used to make sure the legend label is only added once.
        first_arrow = True

        # Loop through each CAD corner label.
        # The same label is used to find the matching scan corner.
        for corner_label in cad_corners:
            # Get the CAD corner and scale it if needed.
            cad_corner = self.scale_point(cad_corners[corner_label])

            # Get the matching scan corner and scale it if needed.
            scan_corner = self.scale_point(scan_corners[corner_label])

            # Calculate the difference between the scan corner and CAD corner.
            # This gives the direction and size of the deviation.
            # Formula: deviation vector = scan corner - CAD corner.
            direction = scan_corner - cad_corner

            # Draw a 3D arrow from the CAD corner to the scan corner.
            ax.quiver(
                # Starting X position of the arrow.
                cad_corner[0],

                # Starting Y position of the arrow.
                cad_corner[1],

                # Starting Z position of the arrow.
                cad_corner[2],

                # Arrow direction in X.
                direction[0],

                # Arrow direction in Y.
                direction[1],

                # Arrow direction in Z.
                direction[2],

                # Set the arrow color to red.
                color="red",

                # Control the size of the arrow head.
                arrow_length_ratio=0.25,

                # Set the arrow line thickness.
                linewidth=2,

                # Add the label only for the first arrow.
                label="Corner deviation" if first_arrow else None
            )

            # After the first arrow is drawn, set first_arrow to False.
            # The remaining arrows will not add duplicate legend labels.
            first_arrow = False

    # Method for drawing transparent box surfaces.
    # It uses the 8 corners to build 6 faces and draws them as transparent polygons.
    def plot_transparent_faces(self, ax, corners, color, alpha):
        # Build the 6 box faces from the 8 corners.
        faces = self.build_box_faces(corners)

        # Create an empty list to store the scaled faces.
        scaled_faces = []

        # Loop through every face.
        for face in faces:
            # Scale every point in the current face.
            scaled_face = [self.scale_point(point) for point in face]

            # Add the scaled face to the list.
            scaled_faces.append(scaled_face)

        # Create a 3D polygon collection from the scaled faces.
        collection = Poly3DCollection(
            # The list of 3D faces.
            scaled_faces,

            # Transparency value.
            # Lower value means more transparent.
            alpha=alpha,

            # Surface color.
            # Example: cyan for scan, yellow for CAD.
            facecolor=color,

            # Border color of the faces.
            edgecolor="black",

            # Border line thickness.
            linewidths=0.5
        )

        # Add the transparent 3D faces to the graph.
        ax.add_collection3d(collection)

    # Method for making the X, Y, and Z axes use the same scale.
    # This prevents the 3D graph from looking stretched or misleading.
    def set_equal_axes(self, ax, all_points):
        # Scale all points if needed and convert them into a NumPy array.
        points = np.array([self.scale_point(point) for point in all_points])

        # Find the minimum and maximum X values.
        x_limits = [points[:, 0].min(), points[:, 0].max()]

        # Find the minimum and maximum Y values.
        y_limits = [points[:, 1].min(), points[:, 1].max()]

        # Find the minimum and maximum Z values.
        z_limits = [points[:, 2].min(), points[:, 2].max()]

        # Calculate the full X range.
        x_range = x_limits[1] - x_limits[0]

        # Calculate the full Y range.
        y_range = y_limits[1] - y_limits[0]

        # Calculate the full Z range.
        z_range = z_limits[1] - z_limits[0]

        # Find the largest range among X, Y, and Z.
        # This largest range will be used for all axes.
        max_range = max(x_range, y_range, z_range)

        # Find the center position of the X axis.
        x_center = sum(x_limits) / 2.0

        # Find the center position of the Y axis.
        y_center = sum(y_limits) / 2.0

        # Find the center position of the Z axis.
        z_center = sum(z_limits) / 2.0

        # Set the X-axis limit using the same max range.
        ax.set_xlim(x_center - max_range / 2.0, x_center + max_range / 2.0)

        # Set the Y-axis limit using the same max range.
        ax.set_ylim(y_center - max_range / 2.0, y_center + max_range / 2.0)

        # Set the Z-axis limit using the same max range.
        ax.set_zlim(z_center - max_range / 2.0, z_center + max_range / 2.0)

    # Main method of this class.
    # This method controls the full visualization process.
    def show_edge_deviation(self, deviation_reporter, scan_pcd, cad_pcd):
        # Ask the deviation reporter to calculate the edge deviation report.
        # scan_pcd is the scanned point cloud.
        # cad_pcd is the CAD/STL model converted into a point cloud.
        report = deviation_reporter.calculate_edge_deviation_report(
            scan_pcd,
            cad_pcd
        )

        # Build the 8 bounding-box corners for the scan/PCD.
        # These are created from the scan minimum and maximum bounds.
        scan_corners = deviation_reporter.build_corners(
            report["scan_min_bound"],
            report["scan_max_bound"]
        )

        # Build the 8 bounding-box corners for the CAD/STL model.
        # These are created from the CAD minimum and maximum bounds.
        cad_corners = deviation_reporter.build_corners(
            report["cad_min_bound"],
            report["cad_max_bound"]
        )

        # Build the 12 edges of the scan box from the scan corners.
        scan_edges = deviation_reporter.build_edges(scan_corners)

        # Build the 12 edges of the CAD box from the CAD corners.
        cad_edges = deviation_reporter.build_edges(cad_corners)

        # Create a Matplotlib figure with size 12 by 9.
        fig = plt.figure(figsize=(12, 9))

        # Add a 3D subplot to the figure.
        ax = fig.add_subplot(111, projection="3d")

        # Draw the scan/PCD bounding box as transparent cyan faces.
        self.plot_transparent_faces(
            ax,
            scan_corners,
            color="cyan",
            alpha=0.25
        )

        # Draw the CAD/STL bounding box as transparent yellow faces.
        self.plot_transparent_faces(
            ax,
            cad_corners,
            color="yellow",
            alpha=0.25
        )

        # Draw the CAD/STL edges.
        # These are black solid lines.
        self.plot_edges(
            ax,
            cad_edges,
            color="black",
            line_style="-",
            label="CAD/STL edges"
        )

        # Draw the scan/PCD edges.
        # These are blue dashed lines.
        self.plot_edges(
            ax,
            scan_edges,
            color="blue",
            line_style="--",
            label="PCD/scan edges"
        )

        # Draw the CAD/STL corners as yellow points.
        self.plot_corners(
            ax,
            cad_corners,
            color="yellow"
        )

        # Draw the scan/PCD corners as cyan points.
        self.plot_corners(
            ax,
            scan_corners,
            color="cyan"
        )

        # Draw red arrows from CAD corners to matching scan corners.
        # These arrows represent the deviation.
        self.plot_corner_arrows(
            ax,
            scan_corners,
            cad_corners
        )

        # Create an empty list to store all corner points.
        all_points = []

        # Add all scan corner points to the list.
        for corner in scan_corners.values():
            all_points.append(corner)

        # Add all CAD corner points to the list.
        for corner in cad_corners.values():
            all_points.append(corner)

        # Set equal scaling for the X, Y, and Z axes.
        # This prevents the graph from looking stretched.
        self.set_equal_axes(ax, all_points)

        # Decide which unit label should be shown on the axes.
        # If scale_to_mm is True, use mm.
        # Otherwise, use m.
        unit = "mm" if self.scale_to_mm else "m"

        # Set the title of the 3D graph.
        ax.set_title("CAD/STL vs PCD Corner Deviation")

        # Set the X-axis label.
        ax.set_xlabel(f"X ({unit})")

        # Set the Y-axis label.
        ax.set_ylabel(f"Y ({unit})")

        # Set the Z-axis label.
        ax.set_zlabel(f"Z ({unit})")

        # Show the graph legend.
        ax.legend()

        # Show grid lines in the graph.
        ax.grid(True)

        # Adjust the layout so labels and graph fit better.
        plt.tight_layout()

        # Display the final 3D graph.
        plt.show()