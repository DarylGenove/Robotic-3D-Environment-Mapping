# Import NumPy.
# NumPy helps us work with numbers, points, arrays, and 3D math.
import numpy as np


class DeviationReporter:
    """
    This class creates reports that compare two 3D models:

    1. The PCD scan:
       - This is the real scanned point cloud from the camera.

    2. The STL/CAD model:
       - This is the clean digital 3D model.

    The goal is to check:
    "How different is the scan from the CAD model?"

    This class can make two kinds of reports:

    1. Room plane deviation report:
       - Compares big flat surfaces.
       - Example:
         floor compared with floor,
         wall compared with wall.

    2. Edge deviation report:
       - Compares the 12 edges of the scanned box/room/cabinet
         with the 12 edges of the CAD model.
       - It checks:
         start point difference,
         end point difference,
         midpoint difference,
         X difference,
         Y difference,
         Z difference,
         and edge length difference.
    """

    def __init__(self, plane_detector=None, lower_percentile=1.0, upper_percentile=99.0):
        """
        This function runs automatically when we create DeviationReporter.

        Example:
        reporter = DeviationReporter()

        plane_detector:
        - Used only for the old wall/floor plane report.
        - It finds flat surfaces like floor and walls.

        lower_percentile:
        - Used for finding the lower safe boundary of the point cloud.
        - Example:
          Instead of using the absolute smallest point,
          we use the 1% point to avoid noise.

        upper_percentile:
        - Used for finding the upper safe boundary of the point cloud.
        - Example:
          Instead of using the absolute biggest point,
          we use the 99% point to avoid noise.

        Why?
        - A point cloud can contain bad noisy points.
        - These noisy points can be very far away.
        - If we use them directly, the box size becomes wrong.
        """

        # Store the plane detector inside this class.
        self.plane_detector = plane_detector

        # Store the lower percentile value.
        # This helps ignore extremely low noisy points.
        self.lower_percentile = lower_percentile

        # Store the upper percentile value.
        # This helps ignore extremely high noisy points.
        self.upper_percentile = upper_percentile

    def get_oriented_plane_model(self, plane, label):
        """
        This function makes sure the plane normal points in the correct direction.

        A plane model looks like this:

        ax + by + cz + d = 0

        It has four values:
        a, b, c, d

        The normal direction is:
        [a, b, c]

        Why do we need this?
        - A detected wall can have its normal pointing inward or outward.
        - If the normal direction is wrong, the signed distance can be confusing.
        - This function flips the normal if needed.
        """

        # Get the four plane values from the plane dictionary.
        a, b, c, d = plane["plane_model"]

        # Put the normal values into a NumPy array.
        # The normal tells us which direction the plane is facing.
        normal = np.array([a, b, c], dtype=np.float64)

        # If this is the floor, we want the normal to point upward.
        # Upward means the Z value should be positive.
        if label == "Floor" and normal[2] < 0:

            # Flip the normal direction.
            normal = -normal

            # Also flip d because the plane equation must stay correct.
            d = -d

        # If this is the X-min wall,
        # we want its normal to point toward negative X.
        elif label == "Wall X-min" and normal[0] > 0:

            # Flip the normal direction.
            normal = -normal

            # Flip d as well.
            d = -d

        # If this is the X-max wall,
        # we want its normal to point toward positive X.
        elif label == "Wall X-max" and normal[0] < 0:

            # Flip the normal direction.
            normal = -normal

            # Flip d as well.
            d = -d

        # If this is the Y-min wall,
        # we want its normal to point toward negative Y.
        elif label == "Wall Y-min" and normal[1] > 0:

            # Flip the normal direction.
            normal = -normal

            # Flip d as well.
            d = -d

        # If this is the Y-max wall,
        # we want its normal to point toward positive Y.
        elif label == "Wall Y-max" and normal[1] < 0:

            # Flip the normal direction.
            normal = -normal

            # Flip d as well.
            d = -d

        # Return the corrected plane model.
        return np.array([normal[0], normal[1], normal[2], d], dtype=np.float64)

    def calculate_plane_deviation(self, scan_plane, cad_plane, label):
        """
        This function compares one scanned plane with one CAD plane.

        Example:
        - Scanned floor compared with CAD floor.
        - Scanned wall compared with CAD wall.

        It measures how far the scan points are from the CAD plane.
        """

        # Get the CAD plane with the correct normal direction.
        cad_plane_model = self.get_oriented_plane_model(cad_plane, label)

        # Split the CAD plane equation into a, b, c, d.
        a, b, c, d = cad_plane_model

        # Create the normal vector from a, b, c.
        normal = np.array([a, b, c], dtype=np.float64)

        # Calculate the length of the normal vector.
        # This is needed to calculate the real distance to the plane.
        normal_length = np.linalg.norm(normal)

        # If the normal length is zero, the plane is invalid.
        # A plane cannot have a normal with zero length.
        if normal_length == 0:
            raise Exception("Invalid CAD plane normal.")

        # Get all points from the scanned plane.
        points = np.asarray(scan_plane["cloud"].points)

        # Calculate signed distance from every scan point to the CAD plane.
        #
        # Formula:
        # distance = (point dot normal + d) / normal_length
        #
        # Positive distance means the point is on one side of the plane.
        # Negative distance means the point is on the other side.
        signed_distances = (points @ normal + d) / normal_length

        # Convert all distances to positive values.
        # This only tells us "how far", not direction.
        absolute_distances = np.abs(signed_distances)

        # Return useful deviation values.
        return {
            # Average absolute distance.
            "mean_abs_m": float(np.mean(absolute_distances)),

            # Middle value of the distances.
            "median_abs_m": float(np.median(absolute_distances)),

            # RMSE gives a strong measurement of error.
            # Bigger errors affect RMSE more.
            "rmse_m": float(np.sqrt(np.mean(signed_distances ** 2))),

            # Biggest absolute distance found.
            "max_abs_m": float(np.max(absolute_distances)),

            # Average signed distance.
            # This still keeps direction.
            "signed_mean_m": float(np.mean(signed_distances)),

            # Number of scan points used.
            "scan_points": len(points),
        }

    def print_room_deviation_report(self, scan_pcd, cad_pcd):
        """
        This function prints the old room deviation report.

        It compares:
        - Floor
        - Wall X-min
        - Wall X-max
        - Wall Y-min
        - Wall Y-max

        It uses plane detection.
        """

        # If there is no plane detector, this report cannot work.
        if self.plane_detector is None:
            raise Exception("Plane detector is required for room deviation report.")

        # Print an empty line for cleaner output.
        print("")

        # Tell the user what is happening.
        print("Measuring wall and floor deviation...")

        # Detect flat planes in the scanned point cloud.
        scan_planes = self.plane_detector.detect_planes(scan_pcd)

        # Detect flat planes in the CAD point cloud.
        cad_planes = self.plane_detector.detect_planes(cad_pcd)

        # Calculate the center of the CAD point cloud.
        # This helps label which wall is which.
        cad_center = np.asarray(cad_pcd.points).mean(axis=0)

        # Label the scanned planes.
        # Example:
        # This plane is Floor.
        # This plane is Wall X-min.
        scan_labelled = self.plane_detector.label_room_planes(
            scan_planes,
            cad_center
        )

        # Label the CAD planes.
        cad_labelled = self.plane_detector.label_room_planes(
            cad_planes,
            cad_center
        )

        # These are the planes we want to compare.
        labels = [
            ("1. Floor", "Floor"),
            ("2. Wall X-min", "Wall X-min"),
            ("3. Wall X-max", "Wall X-max"),
            ("4. Wall Y-min", "Wall Y-min"),
            ("5. Wall Y-max", "Wall Y-max"),
        ]

        # Print report title.
        print("")
        print("Room deviation report:")
        print("Reference: STL/CAD model")
        print("Measured : PCD scan")
        print("Unit     : centimeters")
        print("")

        # Go through every plane label.
        for display_label, label in labels:

            # If the CAD plane was not found, skip it.
            if label not in cad_labelled:
                print(f"{display_label}: CAD plane not found.")
                print("")
                continue

            # If the scan plane was not found, skip it.
            if label not in scan_labelled:
                print(f"{display_label}: scan plane not found.")
                print("")
                continue

            # Calculate the deviation between scan plane and CAD plane.
            result = self.calculate_plane_deviation(
                scan_labelled[label],
                cad_labelled[label],
                label
            )

            # Print the result in centimeters.
            print(display_label)
            print(f"  Mean absolute difference : {result['mean_abs_m'] * 100:.2f} cm")
            print(f"  Median difference        : {result['median_abs_m'] * 100:.2f} cm")
            print(f"  RMSE                     : {result['rmse_m'] * 100:.2f} cm")
            print(f"  Maximum difference       : {result['max_abs_m'] * 100:.2f} cm")
            print(f"  Signed mean difference   : {result['signed_mean_m'] * 100:.2f} cm")
            print(f"  Scan points used         : {result['scan_points']}")
            print("")

    def get_robust_bounds(self, point_cloud):
        """
        This function finds the safe minimum and maximum boundary of a point cloud.

        A point cloud is many tiny 3D dots.

        Each dot has:
        - X position
        - Y position
        - Z position

        We want to find:
        min_bound = [x_min, y_min, z_min]
        max_bound = [x_max, y_max, z_max]

        But we do not use the absolute minimum and maximum,
        because noisy points can make the result wrong.

        Instead, we use percentiles.

        Example:
        lower_percentile = 1
        upper_percentile = 99

        This means:
        - Ignore the lowest 1% of points.
        - Ignore the highest 1% of points.

        This makes the bounding box more stable.
        """

        # Check if the point cloud has no points.
        # If it has no points, we cannot calculate bounds.
        if len(point_cloud.points) == 0:
            raise Exception("Point cloud is empty.")

        # Convert Open3D points into a NumPy array.
        # This makes it easier to calculate with the points.
        points = np.asarray(point_cloud.points)

        # Calculate the safe minimum boundary.
        #
        # axis=0 means:
        # calculate separately for X, Y, and Z.
        #
        # Result:
        # [safe_x_min, safe_y_min, safe_z_min]
        min_bound = np.percentile(
            points,
            self.lower_percentile,
            axis=0
        )

        # Calculate the safe maximum boundary.
        #
        # Result:
        # [safe_x_max, safe_y_max, safe_z_max]
        max_bound = np.percentile(
            points,
            self.upper_percentile,
            axis=0
        )

        # Return both boundaries.
        return min_bound, max_bound

    def build_corners(self, min_bound, max_bound):
        """
        This function builds the 8 corners of a box.

        Imagine a shoebox.

        A box has:
        - 8 corners
        - 12 edges
        - 6 faces

        We only need the 8 corners here.

        min_bound gives:
        x_min, y_min, z_min

        max_bound gives:
        x_max, y_max, z_max
        """

        # Take the minimum X, Y, Z values.
        x_min, y_min, z_min = min_bound

        # Take the maximum X, Y, Z values.
        x_max, y_max, z_max = max_bound

        # Return a dictionary with all 8 corners.
        #
        # Bottom corners use z_min.
        # Top corners use z_max.
        return {
            # Bottom-front-left style corner.
            "1. X-min Y-min Z-min": np.array([x_min, y_min, z_min]),

            # Bottom corner with maximum X.
            "2. X-max Y-min Z-min": np.array([x_max, y_min, z_min]),

            # Bottom corner with maximum Y.
            "3. X-min Y-max Z-min": np.array([x_min, y_max, z_min]),

            # Bottom corner with maximum X and maximum Y.
            "4. X-max Y-max Z-min": np.array([x_max, y_max, z_min]),

            # Top corner above corner 1.
            "5. X-min Y-min Z-max": np.array([x_min, y_min, z_max]),

            # Top corner above corner 2.
            "6. X-max Y-min Z-max": np.array([x_max, y_min, z_max]),

            # Top corner above corner 3.
            "7. X-min Y-max Z-max": np.array([x_min, y_max, z_max]),

            # Top corner above corner 4.
            "8. X-max Y-max Z-max": np.array([x_max, y_max, z_max]),
        }

    def build_edges(self, corners):
        """
        This function builds the 12 edges of a box.

        An edge is a line between two corners.

        Example:
        If corner 1 connects to corner 2,
        that creates one edge.

        A box has:
        - 4 bottom edges
        - 4 top edges
        - 4 vertical edges

        Total:
        12 edges
        """

        # Return all 12 edges.
        # Each edge contains two points:
        # start point and end point.
        return {
            # Bottom edge going in X direction.
            "1. Bottom edge X direction, Y-min Z-min": (
                corners["1. X-min Y-min Z-min"],
                corners["2. X-max Y-min Z-min"],
            ),

            # Bottom edge going in X direction on the Y-max side.
            "2. Bottom edge X direction, Y-max Z-min": (
                corners["3. X-min Y-max Z-min"],
                corners["4. X-max Y-max Z-min"],
            ),

            # Bottom edge going in Y direction.
            "3. Bottom edge Y direction, X-min Z-min": (
                corners["1. X-min Y-min Z-min"],
                corners["3. X-min Y-max Z-min"],
            ),

            # Bottom edge going in Y direction on the X-max side.
            "4. Bottom edge Y direction, X-max Z-min": (
                corners["2. X-max Y-min Z-min"],
                corners["4. X-max Y-max Z-min"],
            ),

            # Top edge going in X direction.
            "5. Top edge X direction, Y-min Z-max": (
                corners["5. X-min Y-min Z-max"],
                corners["6. X-max Y-min Z-max"],
            ),

            # Top edge going in X direction on the Y-max side.
            "6. Top edge X direction, Y-max Z-max": (
                corners["7. X-min Y-max Z-max"],
                corners["8. X-max Y-max Z-max"],
            ),

            # Top edge going in Y direction.
            "7. Top edge Y direction, X-min Z-max": (
                corners["5. X-min Y-min Z-max"],
                corners["7. X-min Y-max Z-max"],
            ),

            # Top edge going in Y direction on the X-max side.
            "8. Top edge Y direction, X-max Z-max": (
                corners["6. X-max Y-min Z-max"],
                corners["8. X-max Y-max Z-max"],
            ),

            # Vertical edge from bottom to top.
            "9. Vertical edge X-min Y-min": (
                corners["1. X-min Y-min Z-min"],
                corners["5. X-min Y-min Z-max"],
            ),

            # Vertical edge from bottom to top on X-max Y-min side.
            "10. Vertical edge X-max Y-min": (
                corners["2. X-max Y-min Z-min"],
                corners["6. X-max Y-min Z-max"],
            ),

            # Vertical edge from bottom to top on X-min Y-max side.
            "11. Vertical edge X-min Y-max": (
                corners["3. X-min Y-max Z-min"],
                corners["7. X-min Y-max Z-max"],
            ),

            # Vertical edge from bottom to top on X-max Y-max side.
            "12. Vertical edge X-max Y-max": (
                corners["4. X-max Y-max Z-min"],
                corners["8. X-max Y-max Z-max"],
            ),
        }

    def calculate_edge_deviation(self, scan_edges, cad_edges):
        """
        This function compares each scan edge with the matching CAD edge.

        It assumes:
        - Edge 1 from scan matches edge 1 from CAD.
        - Edge 2 from scan matches edge 2 from CAD.
        - And so on until edge 12.

        For each edge, it calculates:

        1. Start point difference:
           How far is the CAD start point from the scan start point?

        2. End point difference:
           How far is the CAD end point from the scan end point?

        3. Midpoint difference:
           How far is the middle of the CAD edge from the middle of the scan edge?

        4. X, Y, Z midpoint difference:
           Shows in which direction the difference happens.

        5. Length difference:
           Checks if the CAD edge is longer or shorter than the scanned edge.
        """

        # Create an empty dictionary to store all edge results.
        edge_results = {}

        # Go through each CAD edge label.
        for label in cad_edges:

            # Get the scan edge start and end points.
            scan_start, scan_end = scan_edges[label]

            # Get the CAD edge start and end points.
            cad_start, cad_end = cad_edges[label]

            # Calculate the middle point of the scan edge.
            scan_midpoint = (scan_start + scan_end) / 2.0

            # Calculate the middle point of the CAD edge.
            cad_midpoint = (cad_start + cad_end) / 2.0

            # Calculate the scan edge length.
            #
            # np.linalg.norm calculates the straight-line distance.
            scan_length = np.linalg.norm(scan_end - scan_start)

            # Calculate the CAD edge length.
            cad_length = np.linalg.norm(cad_end - cad_start)

            # Calculate the difference vector between CAD start and scan start.
            #
            # Example:
            # If CAD start is [5, 2, 1]
            # and scan start is [3, 2, 1],
            # the difference is [2, 0, 0].
            start_difference_vector = cad_start - scan_start

            # Calculate the difference vector between CAD end and scan end.
            end_difference_vector = cad_end - scan_end

            # Calculate the difference vector between CAD midpoint and scan midpoint.
            midpoint_difference_vector = cad_midpoint - scan_midpoint

            # Convert the start difference vector into one distance number.
            start_distance_m = np.linalg.norm(start_difference_vector)

            # Convert the end difference vector into one distance number.
            end_distance_m = np.linalg.norm(end_difference_vector)

            # Convert the midpoint difference vector into one distance number.
            midpoint_distance_m = np.linalg.norm(midpoint_difference_vector)

            # Calculate how much longer or shorter the CAD edge is.
            #
            # Positive value:
            # CAD edge is longer.
            #
            # Negative value:
            # CAD edge is shorter.
            length_difference_m = cad_length - scan_length

            # Save all values for this edge.
            edge_results[label] = {
                # Scan edge start point.
                "scan_start": scan_start,

                # Scan edge end point.
                "scan_end": scan_end,

                # CAD edge start point.
                "cad_start": cad_start,

                # CAD edge end point.
                "cad_end": cad_end,

                # Scan edge midpoint.
                "scan_midpoint": scan_midpoint,

                # CAD edge midpoint.
                "cad_midpoint": cad_midpoint,

                # Scan edge length in meters.
                "scan_length_m": float(scan_length),

                # CAD edge length in meters.
                "cad_length_m": float(cad_length),

                # Signed X midpoint difference.
                # Positive means CAD is more positive in X than scan.
                "signed_x_m": float(midpoint_difference_vector[0]),

                # Signed Y midpoint difference.
                # Positive means CAD is more positive in Y than scan.
                "signed_y_m": float(midpoint_difference_vector[1]),

                # Signed Z midpoint difference.
                # Positive means CAD is higher than scan.
                "signed_z_m": float(midpoint_difference_vector[2]),

                # Absolute X difference.
                # This ignores direction.
                "absolute_x_m": float(abs(midpoint_difference_vector[0])),

                # Absolute Y difference.
                # This ignores direction.
                "absolute_y_m": float(abs(midpoint_difference_vector[1])),

                # Absolute Z difference.
                # This ignores direction.
                "absolute_z_m": float(abs(midpoint_difference_vector[2])),

                # Start point distance.
                "start_distance_m": float(start_distance_m),

                # End point distance.
                "end_distance_m": float(end_distance_m),

                # Midpoint 3D distance.
                "midpoint_distance_m": float(midpoint_distance_m),

                # Signed length difference.
                "length_difference_m": float(length_difference_m),

                # Absolute length difference.
                "absolute_length_difference_m": float(abs(length_difference_m)),
            }

        # Return all edge comparison results.
        return edge_results

    def describe_signed_difference(self, axis, value_m):
        """
        This function turns a signed number into readable text.

        Example:
        Instead of only printing:
        Z difference = 0.05 m

        It prints:
        CAD/STL is 5.00 cm higher than PCD/scan

        This makes the report easier to understand.
        """

        # Convert meters to centimeters.
        value_cm = value_m * 100

        # If the difference is extremely small,
        # we say they are basically in the same position.
        if abs(value_cm) < 0.005:
            return f"same {axis} position"

        # Explain X direction difference.
        if axis == "X":

            # Positive X difference.
            if value_cm > 0:
                return f"CAD/STL is {abs(value_cm):.2f} cm more positive in X than PCD/scan"

            # Negative X difference.
            return f"CAD/STL is {abs(value_cm):.2f} cm more negative in X than PCD/scan"

        # Explain Y direction difference.
        if axis == "Y":

            # Positive Y difference.
            if value_cm > 0:
                return f"CAD/STL is {abs(value_cm):.2f} cm more positive in Y than PCD/scan"

            # Negative Y difference.
            return f"CAD/STL is {abs(value_cm):.2f} cm more negative in Y than PCD/scan"

        # Explain Z direction difference.
        if axis == "Z":

            # Positive Z means CAD is higher.
            if value_cm > 0:
                return f"CAD/STL is {abs(value_cm):.2f} cm higher than PCD/scan"

            # Negative Z means CAD is lower.
            return f"CAD/STL is {abs(value_cm):.2f} cm lower than PCD/scan"

        # Fallback text if the axis is not X, Y, or Z.
        return f"{axis} difference: {value_cm:.2f} cm"

    def calculate_edge_deviation_report(self, scan_pcd, cad_pcd):
        """
        This function calculates the full edge deviation report.

        It does not print yet.

        It only calculates and returns the values.

        Main steps:

        1. Find scan bounds.
        2. Find CAD bounds.
        3. Build scan corners.
        4. Build CAD corners.
        5. Build scan edges.
        6. Build CAD edges.
        7. Compare matching edges.
        8. Calculate summary values.
        """

        # Find safe min and max bounds of the scan point cloud.
        scan_min_bound, scan_max_bound = self.get_robust_bounds(scan_pcd)

        # Find safe min and max bounds of the CAD point cloud.
        cad_min_bound, cad_max_bound = self.get_robust_bounds(cad_pcd)

        # Build 8 scan corners from scan bounds.
        scan_corners = self.build_corners(
            scan_min_bound,
            scan_max_bound
        )

        # Build 8 CAD corners from CAD bounds.
        cad_corners = self.build_corners(
            cad_min_bound,
            cad_max_bound
        )

        # Build 12 scan edges from scan corners.
        scan_edges = self.build_edges(scan_corners)

        # Build 12 CAD edges from CAD corners.
        cad_edges = self.build_edges(cad_corners)

        # Compare every scan edge with the matching CAD edge.
        edge_results = self.calculate_edge_deviation(
            scan_edges,
            cad_edges
        )

        # Collect all midpoint distances into one NumPy array.
        midpoint_distances = np.array([
            result["midpoint_distance_m"]
            for result in edge_results.values()
        ])

        # Collect all start point distances into one NumPy array.
        start_distances = np.array([
            result["start_distance_m"]
            for result in edge_results.values()
        ])

        # Collect all end point distances into one NumPy array.
        end_distances = np.array([
            result["end_distance_m"]
            for result in edge_results.values()
        ])

        # Collect all absolute length differences into one NumPy array.
        length_differences = np.array([
            result["absolute_length_difference_m"]
            for result in edge_results.values()
        ])

        # Return the full report data.
        return {
            # Scan minimum bound.
            "scan_min_bound": scan_min_bound,

            # Scan maximum bound.
            "scan_max_bound": scan_max_bound,

            # CAD minimum bound.
            "cad_min_bound": cad_min_bound,

            # CAD maximum bound.
            "cad_max_bound": cad_max_bound,

            # Detailed result for each of the 12 edges.
            "edge_results": edge_results,

            # Average midpoint difference.
            "midpoint_mean_m": float(np.mean(midpoint_distances)),

            # Median midpoint difference.
            "midpoint_median_m": float(np.median(midpoint_distances)),

            # RMSE midpoint difference.
            "midpoint_rmse_m": float(np.sqrt(np.mean(midpoint_distances ** 2))),

            # Biggest midpoint difference.
            "midpoint_max_m": float(np.max(midpoint_distances)),

            # Average start point difference.
            "start_mean_m": float(np.mean(start_distances)),

            # Average end point difference.
            "end_mean_m": float(np.mean(end_distances)),

            # Average edge length difference.
            "length_mean_m": float(np.mean(length_differences)),

            # Median edge length difference.
            "length_median_m": float(np.median(length_differences)),

            # RMSE edge length difference.
            "length_rmse_m": float(np.sqrt(np.mean(length_differences ** 2))),

            # Biggest edge length difference.
            "length_max_m": float(np.max(length_differences)),
        }

    def print_edge_deviation_report(self, scan_pcd, cad_pcd):
        """
        This function prints the 12-edge deviation report.

        This answers the question:

        "After alignment, how different are the CAD/STL edges
        from the PCD/scan edges?"

        This is useful because edges and corners show whether
        the scan and CAD model are really aligned properly.
        """

        # Print an empty line.
        print("")

        # Tell the user what is being measured.
        print("Measuring 12-edge deviation between scan and CAD...")

        # Calculate the full edge report first.
        result = self.calculate_edge_deviation_report(
            scan_pcd,
            cad_pcd
        )

        # Print the report header.
        print("")
        print("12-edge deviation report:")
        print("Reference: STL/CAD model")
        print("Measured : PCD scan")
        print("Method   : robust bounding-box edge comparison")
        print("Unit     : centimeters")
        print("")

        # Print the bounds used.
        # These show the box size used for scan and CAD.
        print("Bounds used")
        print(f"  Scan min bound: {np.round(result['scan_min_bound'], 4)}")
        print(f"  Scan max bound: {np.round(result['scan_max_bound'], 4)}")
        print(f"  CAD min bound : {np.round(result['cad_min_bound'], 4)}")
        print(f"  CAD max bound : {np.round(result['cad_max_bound'], 4)}")
        print("")

        # Print summary for edge midpoint differences.
        print("Edge midpoint deviation summary")
        print(f"  Mean midpoint difference   : {result['midpoint_mean_m'] * 100:.2f} cm")
        print(f"  Median midpoint difference : {result['midpoint_median_m'] * 100:.2f} cm")
        print(f"  RMSE midpoint difference   : {result['midpoint_rmse_m'] * 100:.2f} cm")
        print(f"  Maximum midpoint difference: {result['midpoint_max_m'] * 100:.2f} cm")
        print("")

        # Print summary for endpoint differences.
        print("Edge endpoint deviation summary")
        print(f"  Mean start-point difference: {result['start_mean_m'] * 100:.2f} cm")
        print(f"  Mean end-point difference  : {result['end_mean_m'] * 100:.2f} cm")
        print("")

        # Print summary for edge length differences.
        print("Edge length deviation summary")
        print(f"  Mean length difference     : {result['length_mean_m'] * 100:.2f} cm")
        print(f"  Median length difference   : {result['length_median_m'] * 100:.2f} cm")
        print(f"  RMSE length difference     : {result['length_rmse_m'] * 100:.2f} cm")
        print(f"  Maximum length difference  : {result['length_max_m'] * 100:.2f} cm")
        print("")

        # Start printing every edge one by one.
        print("Detailed 12-edge differences")

        # Loop through all 12 edge results.
        for label, edge_result in result["edge_results"].items():

            # Print edge name.
            print(label)

            # Print CAD and scan start/end points.
            print(f"  CAD/STL start point      : {np.round(edge_result['cad_start'], 4)}")
            print(f"  PCD/scan start point     : {np.round(edge_result['scan_start'], 4)}")
            print(f"  CAD/STL end point        : {np.round(edge_result['cad_end'], 4)}")
            print(f"  PCD/scan end point       : {np.round(edge_result['scan_end'], 4)}")

            # Print distance between start points.
            print(f"  Start point difference   : {edge_result['start_distance_m'] * 100:.2f} cm")

            # Print distance between end points.
            print(f"  End point difference     : {edge_result['end_distance_m'] * 100:.2f} cm")

            # Print distance between midpoints.
            print(f"  Midpoint 3D difference   : {edge_result['midpoint_distance_m'] * 100:.2f} cm")

            # Print X, Y, and Z midpoint differences.
            print(f"  X midpoint difference    : {edge_result['absolute_x_m'] * 100:.2f} cm")
            print(f"  Y midpoint difference    : {edge_result['absolute_y_m'] * 100:.2f} cm")
            print(f"  Z midpoint difference    : {edge_result['absolute_z_m'] * 100:.2f} cm")

            # Print readable X direction explanation.
            print(f"  X direction              : {self.describe_signed_difference('X', edge_result['signed_x_m'])}")

            # Print readable Y direction explanation.
            print(f"  Y direction              : {self.describe_signed_difference('Y', edge_result['signed_y_m'])}")

            # Print readable Z direction explanation.
            print(f"  Z direction              : {self.describe_signed_difference('Z', edge_result['signed_z_m'])}")

            # Print CAD edge length.
            print(f"  CAD/STL edge length      : {edge_result['cad_length_m'] * 100:.2f} cm")

            # Print scan edge length.
            print(f"  PCD/scan edge length     : {edge_result['scan_length_m'] * 100:.2f} cm")

            # If CAD edge is longer, print that.
            if edge_result["length_difference_m"] > 0:
                print(f"  Length direction         : CAD/STL edge is {edge_result['absolute_length_difference_m'] * 100:.2f} cm longer")

            # If CAD edge is shorter, print that.
            elif edge_result["length_difference_m"] < 0:
                print(f"  Length direction         : CAD/STL edge is {edge_result['absolute_length_difference_m'] * 100:.2f} cm shorter")

            # If both edge lengths are the same, print that.
            else:
                print("  Length direction         : same length")

            # Print an empty line after each edge.
            print("")

    def print_alignment_deviation_report(self, scan_pcd, cad_pcd):
        """
        This is a compatibility method.

        It exists because the old main.py file may still call:

        print_alignment_deviation_report()

        Instead of breaking the code,
        this function redirects the call to:

        print_edge_deviation_report()

        So the old name still works,
        but it now prints the new 12-edge report.
        """

        # Redirect to the edge deviation report.
        self.print_edge_deviation_report(
            scan_pcd,
            cad_pcd
        )