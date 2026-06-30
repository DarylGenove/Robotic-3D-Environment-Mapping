# Bring in numpy so this file can use it.
import numpy as np


# Bring in matplotlib.pyplot so this file can use it.
import matplotlib.pyplot as plt


# Bring in needed tools from mpl_toolkits.mplot3d.art3d.
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


# Create the EdgeDeviationPlotter class, which groups related code together.
class EdgeDeviationPlotter:


    # Create the setup function that runs when this object is made.
    def __init__(self, scale_to_mm=True):


        # Save this value inside the object for later.
        self.scale_to_mm = scale_to_mm


    # Create the scale point function.
    def scale_point(self, point):

        # Check this condition before choosing what happens next.
        if self.scale_to_mm:


            # Send this result back to the part of the code that asked for it.
            return point * 1000.0


        # Send this result back to the part of the code that asked for it.
        return point


    # Create the build box faces function.
    def build_box_faces(self, corners):


        # Send this result back to the part of the code that asked for it.
        return [


            # Start a group of values.
            [
                # Add this value to the current group.
                corners["1. X-min Y-min Z-min"],
                # Add this value to the current group.
                corners["2. X-max Y-min Z-min"],
                # Add this value to the current group.
                corners["4. X-max Y-max Z-min"],
                # Add this value to the current group.
                corners["3. X-min Y-max Z-min"],
            ],


            # Start a group of values.
            [
                # Add this value to the current group.
                corners["5. X-min Y-min Z-max"],
                # Add this value to the current group.
                corners["6. X-max Y-min Z-max"],
                # Add this value to the current group.
                corners["8. X-max Y-max Z-max"],
                # Add this value to the current group.
                corners["7. X-min Y-max Z-max"],
            ],


            # Start a group of values.
            [
                # Add this value to the current group.
                corners["1. X-min Y-min Z-min"],
                # Add this value to the current group.
                corners["2. X-max Y-min Z-min"],
                # Add this value to the current group.
                corners["6. X-max Y-min Z-max"],
                # Add this value to the current group.
                corners["5. X-min Y-min Z-max"],
            ],


            # Start a group of values.
            [
                # Add this value to the current group.
                corners["3. X-min Y-max Z-min"],
                # Add this value to the current group.
                corners["4. X-max Y-max Z-min"],
                # Add this value to the current group.
                corners["8. X-max Y-max Z-max"],
                # Add this value to the current group.
                corners["7. X-min Y-max Z-max"],
            ],


            # Start a group of values.
            [
                # Add this value to the current group.
                corners["1. X-min Y-min Z-min"],
                # Add this value to the current group.
                corners["3. X-min Y-max Z-min"],
                # Add this value to the current group.
                corners["7. X-min Y-max Z-max"],
                # Add this value to the current group.
                corners["5. X-min Y-min Z-max"],
            ],


            # Start a group of values.
            [
                # Add this value to the current group.
                corners["2. X-max Y-min Z-min"],
                # Add this value to the current group.
                corners["4. X-max Y-max Z-min"],
                # Add this value to the current group.
                corners["8. X-max Y-max Z-max"],
                # Add this value to the current group.
                corners["6. X-max Y-min Z-max"],
            ],
        ]


    # Create the plot edges function.
    def plot_edges(self, ax, edges, color, line_style, label):


        # Save a value in first line.
        first_line = True


        # Repeat this code for every item in the group.
        for _, edge in edges.items():

            # Save a value in start point.
            start_point = self.scale_point(edge[0])


            # Save a value in end point.
            end_point = self.scale_point(edge[1])


            # Run this line as one small step in the program.
            ax.plot(

                # Start a group of values.
                [start_point[0], end_point[0]],


                # Start a group of values.
                [start_point[1], end_point[1]],


                # Start a group of values.
                [start_point[2], end_point[2]],


                # Save a value in color.
                color=color,


                # Save a value in linestyle.
                linestyle=line_style,


                # Save a value in linewidth.
                linewidth=2,


                # Save a value in label.
                label=label if first_line else None
            )


            # Save a value in first line.
            first_line = False


    # Create the plot corners function.
    def plot_corners(self, ax, corners, color):


        # Repeat this code for every item in the group.
        for _, corner in corners.items():

            # Save a value in point.
            point = self.scale_point(corner)


            # Run this line as one small step in the program.
            ax.scatter(

                # Add this value to the current group.
                point[0],


                # Add this value to the current group.
                point[1],


                # Add this value to the current group.
                point[2],


                # Save a value in color.
                color=color,


                # Save a value in s.
                s=45,


                # Save a value in edgecolors.
                edgecolors="black",


                # Save a value in zorder.
                zorder=5
            )


    # Create the plot corner arrows function.
    def plot_corner_arrows(self, ax, scan_corners, cad_corners):

        # Save a value in first arrow.
        first_arrow = True


        # Repeat this code for every item in the group.
        for corner_label in cad_corners:

            # Save a value in cad corner.
            cad_corner = self.scale_point(cad_corners[corner_label])


            # Save a value in scan corner.
            scan_corner = self.scale_point(scan_corners[corner_label])


            # Save a value in direction.
            direction = scan_corner - cad_corner


            # Run this line as one small step in the program.
            ax.quiver(

                # Add this value to the current group.
                cad_corner[0],


                # Add this value to the current group.
                cad_corner[1],


                # Add this value to the current group.
                cad_corner[2],


                # Add this value to the current group.
                direction[0],


                # Add this value to the current group.
                direction[1],


                # Add this value to the current group.
                direction[2],


                # Save a value in color.
                color="red",


                # Save a value in arrow length ratio.
                arrow_length_ratio=0.25,


                # Save a value in linewidth.
                linewidth=2,


                # Save a value in label.
                label="Corner deviation" if first_arrow else None
            )


            # Save a value in first arrow.
            first_arrow = False


    # Create the plot transparent faces function.
    def plot_transparent_faces(self, ax, corners, color, alpha):

        # Save a value in faces.
        faces = self.build_box_faces(corners)


        # Save a value in scaled faces.
        scaled_faces = []


        # Repeat this code for every item in the group.
        for face in faces:

            # Save a value in scaled face.
            scaled_face = [self.scale_point(point) for point in face]


            # Add this item to the list.
            scaled_faces.append(scaled_face)


        # Save a value in collection.
        collection = Poly3DCollection(

            # Add this value to the current group.
            scaled_faces,


            # Save a value in alpha.
            alpha=alpha,


            # Save a value in facecolor.
            facecolor=color,


            # Save a value in edgecolor.
            edgecolor="black",


            # Save a value in linewidths.
            linewidths=0.5
        )


        # Run this line as one small step in the program.
        ax.add_collection3d(collection)


    # Create the set equal axes function.
    def set_equal_axes(self, ax, all_points):

        # Put these numbers into a NumPy array.
        points = np.array([self.scale_point(point) for point in all_points])


        # Save a value in x limits.
        x_limits = [points[:, 0].min(), points[:, 0].max()]


        # Save a value in y limits.
        y_limits = [points[:, 1].min(), points[:, 1].max()]


        # Save a value in z limits.
        z_limits = [points[:, 2].min(), points[:, 2].max()]


        # Save a value in x range.
        x_range = x_limits[1] - x_limits[0]


        # Save a value in y range.
        y_range = y_limits[1] - y_limits[0]


        # Save a value in z range.
        z_range = z_limits[1] - z_limits[0]


        # Save a value in max range.
        max_range = max(x_range, y_range, z_range)


        # Save a value in x center.
        x_center = sum(x_limits) / 2.0


        # Save a value in y center.
        y_center = sum(y_limits) / 2.0


        # Save a value in z center.
        z_center = sum(z_limits) / 2.0


        # Run this line as one small step in the program.
        ax.set_xlim(x_center - max_range / 2.0, x_center + max_range / 2.0)


        # Run this line as one small step in the program.
        ax.set_ylim(y_center - max_range / 2.0, y_center + max_range / 2.0)


        # Run this line as one small step in the program.
        ax.set_zlim(z_center - max_range / 2.0, z_center + max_range / 2.0)


    # Create the show edge deviation function.
    def show_edge_deviation(self, deviation_reporter, scan_pcd, cad_pcd):


        # Save a value in report.
        report = deviation_reporter.calculate_edge_deviation_report(
            # Add this value to the current group.
            scan_pcd,
            # Run this line as one small step in the program.
            cad_pcd
        )


        # Save a value in scan corners.
        scan_corners = deviation_reporter.build_corners(
            # Add this value to the current group.
            report["scan_min_bound"],
            # Run this line as one small step in the program.
            report["scan_max_bound"]
        )


        # Save a value in cad corners.
        cad_corners = deviation_reporter.build_corners(
            # Add this value to the current group.
            report["cad_min_bound"],
            # Run this line as one small step in the program.
            report["cad_max_bound"]
        )


        # Save a value in scan edges.
        scan_edges = deviation_reporter.build_edges(scan_corners)


        # Save a value in cad edges.
        cad_edges = deviation_reporter.build_edges(cad_corners)


        # Save a value in fig.
        fig = plt.figure(figsize=(12, 9))


        # Save a value in ax.
        ax = fig.add_subplot(111, projection="3d")


        # Run this line as one small step in the program.
        self.plot_transparent_faces(
            # Add this value to the current group.
            ax,
            # Add this value to the current group.
            scan_corners,
            # Save a value in color.
            color="cyan",
            # Save a value in alpha.
            alpha=0.25
        )


        # Run this line as one small step in the program.
        self.plot_transparent_faces(
            # Add this value to the current group.
            ax,
            # Add this value to the current group.
            cad_corners,
            # Save a value in color.
            color="yellow",
            # Save a value in alpha.
            alpha=0.25
        )


        # Run this line as one small step in the program.
        self.plot_edges(
            # Add this value to the current group.
            ax,
            # Add this value to the current group.
            cad_edges,
            # Save a value in color.
            color="black",
            # Save a value in line style.
            line_style="-",
            # Save a value in label.
            label="CAD/STL edges"
        )


        # Run this line as one small step in the program.
        self.plot_edges(
            # Add this value to the current group.
            ax,
            # Add this value to the current group.
            scan_edges,
            # Save a value in color.
            color="blue",
            # Save a value in line style.
            line_style="--",
            # Save a value in label.
            label="PCD/scan edges"
        )


        # Run this line as one small step in the program.
        self.plot_corners(
            # Add this value to the current group.
            ax,
            # Add this value to the current group.
            cad_corners,
            # Save a value in color.
            color="yellow"
        )


        # Run this line as one small step in the program.
        self.plot_corners(
            # Add this value to the current group.
            ax,
            # Add this value to the current group.
            scan_corners,
            # Save a value in color.
            color="cyan"
        )


        # Run this line as one small step in the program.
        self.plot_corner_arrows(
            # Add this value to the current group.
            ax,
            # Add this value to the current group.
            scan_corners,
            # Run this line as one small step in the program.
            cad_corners
        )


        # Save a value in all points.
        all_points = []


        # Repeat this code for every item in the group.
        for corner in scan_corners.values():
            # Add this item to the list.
            all_points.append(corner)


        # Repeat this code for every item in the group.
        for corner in cad_corners.values():
            # Add this item to the list.
            all_points.append(corner)


        # Run this line as one small step in the program.
        self.set_equal_axes(ax, all_points)


        # Save a value in unit.
        unit = "mm" if self.scale_to_mm else "m"


        # Run this line as one small step in the program.
        ax.set_title("CAD/STL vs PCD Corner Deviation")


        # Run this line as one small step in the program.
        ax.set_xlabel(f"X ({unit})")


        # Run this line as one small step in the program.
        ax.set_ylabel(f"Y ({unit})")


        # Run this line as one small step in the program.
        ax.set_zlabel(f"Z ({unit})")


        # Run this line as one small step in the program.
        ax.legend()


        # Run this line as one small step in the program.
        ax.grid(True)


        # Run this line as one small step in the program.
        plt.tight_layout()


        # Run this line as one small step in the program.
        plt.show()
