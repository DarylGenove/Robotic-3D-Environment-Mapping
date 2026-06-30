# Bring in numpy so this file can use it.
import numpy as np


# Create the DeviationReporter class, which groups related code together.
class DeviationReporter:


    # Create the setup function that runs when this object is made.
    def __init__(self, plane_detector=None, lower_percentile=1.0, upper_percentile=99.0):


        # Save this value inside the object for later.
        self.plane_detector = plane_detector


        # Save this value inside the object for later.
        self.lower_percentile = lower_percentile


        # Save this value inside the object for later.
        self.upper_percentile = upper_percentile

    # Create the get oriented plane model function.
    def get_oriented_plane_model(self, plane, label):


        # Save several results into separate variable names.
        a, b, c, d = plane["plane_model"]


        # Put these numbers into a NumPy array.
        normal = np.array([a, b, c], dtype=np.float64)


        # Check this condition before choosing what happens next.
        if label == "Floor" and normal[2] < 0:


            # Save a value in normal.
            normal = -normal


            # Save a value in d.
            d = -d


        # Check another condition if the previous one was false.
        elif label == "Wall X-min" and normal[0] > 0:


            # Save a value in normal.
            normal = -normal


            # Save a value in d.
            d = -d


        # Check another condition if the previous one was false.
        elif label == "Wall X-max" and normal[0] < 0:


            # Save a value in normal.
            normal = -normal


            # Save a value in d.
            d = -d


        # Check another condition if the previous one was false.
        elif label == "Wall Y-min" and normal[1] > 0:


            # Save a value in normal.
            normal = -normal


            # Save a value in d.
            d = -d


        # Check another condition if the previous one was false.
        elif label == "Wall Y-max" and normal[1] < 0:


            # Save a value in normal.
            normal = -normal


            # Save a value in d.
            d = -d


        # Put these numbers into a NumPy array.
        return np.array([normal[0], normal[1], normal[2], d], dtype=np.float64)

    # Create the calculate plane deviation function.
    def calculate_plane_deviation(self, scan_plane, cad_plane, label):


        # Save a value in cad plane model.
        cad_plane_model = self.get_oriented_plane_model(cad_plane, label)


        # Save several results into separate variable names.
        a, b, c, d = cad_plane_model


        # Put these numbers into a NumPy array.
        normal = np.array([a, b, c], dtype=np.float64)


        # Measure how long this vector is.
        normal_length = np.linalg.norm(normal)


        # Check this condition before choosing what happens next.
        if normal_length == 0:
            # Stop the program and show a clear error message.
            raise Exception("Invalid CAD plane normal.")


        # Change the Open3D points into NumPy numbers.
        points = np.asarray(scan_plane["cloud"].points)


        # Save a value in signed distances.
        signed_distances = (points @ normal + d) / normal_length


        # Save a value in absolute distances.
        absolute_distances = np.abs(signed_distances)


        # Send this result back to the part of the code that asked for it.
        return {

            # Store this named value inside a dictionary.
            "mean_abs_m": float(np.mean(absolute_distances)),


            # Store this named value inside a dictionary.
            "median_abs_m": float(np.median(absolute_distances)),


            # Store this named value inside a dictionary.
            "rmse_m": float(np.sqrt(np.mean(signed_distances ** 2))),


            # Store this named value inside a dictionary.
            "max_abs_m": float(np.max(absolute_distances)),


            # Store this named value inside a dictionary.
            "signed_mean_m": float(np.mean(signed_distances)),


            # Count how many points are inside this object.
            "scan_points": len(points),
        }

    # Create the print room deviation report function.
    def print_room_deviation_report(self, scan_pcd, cad_pcd):


        # Check this condition before choosing what happens next.
        if self.plane_detector is None:
            # Stop the program and show a clear error message.
            raise Exception("Plane detector is required for room deviation report.")


        # Show helpful information on the screen.
        print("")


        # Show helpful information on the screen.
        print("Measuring wall and floor deviation...")


        # Save a value in scan planes.
        scan_planes = self.plane_detector.detect_planes(scan_pcd)


        # Save a value in cad planes.
        cad_planes = self.plane_detector.detect_planes(cad_pcd)


        # Change the Open3D points into NumPy numbers.
        cad_center = np.asarray(cad_pcd.points).mean(axis=0)


        # Save a value in scan labelled.
        scan_labelled = self.plane_detector.label_room_planes(
            # Add this value to the current group.
            scan_planes,
            # Run this line as one small step in the program.
            cad_center
        )


        # Save a value in cad labelled.
        cad_labelled = self.plane_detector.label_room_planes(
            # Add this value to the current group.
            cad_planes,
            # Run this line as one small step in the program.
            cad_center
        )


        # Save a value in labels.
        labels = [
            # Start a group of values.
            ("1. Floor", "Floor"),
            # Start a group of values.
            ("2. Wall X-min", "Wall X-min"),
            # Start a group of values.
            ("3. Wall X-max", "Wall X-max"),
            # Start a group of values.
            ("4. Wall Y-min", "Wall Y-min"),
            # Start a group of values.
            ("5. Wall Y-max", "Wall Y-max"),
        ]


        # Show helpful information on the screen.
        print("")
        # Show helpful information on the screen.
        print("Room deviation report:")
        # Show helpful information on the screen.
        print("Reference: STL/CAD model")
        # Show helpful information on the screen.
        print("Measured : PCD scan")
        # Show helpful information on the screen.
        print("Unit     : centimeters")
        # Show helpful information on the screen.
        print("")


        # Repeat this code for every item in the group.
        for display_label, label in labels:


            # Check this condition before choosing what happens next.
            if label not in cad_labelled:
                # Show helpful information on the screen.
                print(f"{display_label}: CAD plane not found.")
                # Show helpful information on the screen.
                print("")
                # Skip the rest of this loop and go to the next item.
                continue


            # Check this condition before choosing what happens next.
            if label not in scan_labelled:
                # Show helpful information on the screen.
                print(f"{display_label}: scan plane not found.")
                # Show helpful information on the screen.
                print("")
                # Skip the rest of this loop and go to the next item.
                continue


            # Save a value in result.
            result = self.calculate_plane_deviation(
                # Add this value to the current group.
                scan_labelled[label],
                # Add this value to the current group.
                cad_labelled[label],
                # Run this line as one small step in the program.
                label
            )


            # Show helpful information on the screen.
            print(display_label)
            # Show helpful information on the screen.
            print(f"  Mean absolute difference : {result['mean_abs_m'] * 100:.2f} cm")
            # Show helpful information on the screen.
            print(f"  Median difference        : {result['median_abs_m'] * 100:.2f} cm")
            # Show helpful information on the screen.
            print(f"  RMSE                     : {result['rmse_m'] * 100:.2f} cm")
            # Show helpful information on the screen.
            print(f"  Maximum difference       : {result['max_abs_m'] * 100:.2f} cm")
            # Show helpful information on the screen.
            print(f"  Signed mean difference   : {result['signed_mean_m'] * 100:.2f} cm")
            # Show helpful information on the screen.
            print(f"  Scan points used         : {result['scan_points']}")
            # Show helpful information on the screen.
            print("")

    # Create the get robust bounds function.
    def get_robust_bounds(self, point_cloud):


        # Count how many points are inside this object.
        if len(point_cloud.points) == 0:
            # Stop the program and show a clear error message.
            raise Exception("Point cloud is empty.")


        # Change the Open3D points into NumPy numbers.
        points = np.asarray(point_cloud.points)


        # Get a safe edge value while ignoring extreme noisy points.
        min_bound = np.percentile(
            # Add this value to the current group.
            points,
            # Add this value to the current group.
            self.lower_percentile,
            # Save a value in axis.
            axis=0
        )


        # Get a safe edge value while ignoring extreme noisy points.
        max_bound = np.percentile(
            # Add this value to the current group.
            points,
            # Add this value to the current group.
            self.upper_percentile,
            # Save a value in axis.
            axis=0
        )


        # Send this result back to the part of the code that asked for it.
        return min_bound, max_bound

    # Create the build corners function.
    def build_corners(self, min_bound, max_bound):


        # Save several results into separate variable names.
        x_min, y_min, z_min = min_bound


        # Save several results into separate variable names.
        x_max, y_max, z_max = max_bound


        # Send this result back to the part of the code that asked for it.
        return {

            # Put these numbers into a NumPy array.
            "1. X-min Y-min Z-min": np.array([x_min, y_min, z_min]),


            # Put these numbers into a NumPy array.
            "2. X-max Y-min Z-min": np.array([x_max, y_min, z_min]),


            # Put these numbers into a NumPy array.
            "3. X-min Y-max Z-min": np.array([x_min, y_max, z_min]),


            # Put these numbers into a NumPy array.
            "4. X-max Y-max Z-min": np.array([x_max, y_max, z_min]),


            # Put these numbers into a NumPy array.
            "5. X-min Y-min Z-max": np.array([x_min, y_min, z_max]),


            # Put these numbers into a NumPy array.
            "6. X-max Y-min Z-max": np.array([x_max, y_min, z_max]),


            # Put these numbers into a NumPy array.
            "7. X-min Y-max Z-max": np.array([x_min, y_max, z_max]),


            # Put these numbers into a NumPy array.
            "8. X-max Y-max Z-max": np.array([x_max, y_max, z_max]),
        }

    # Create the build edges function.
    def build_edges(self, corners):


        # Send this result back to the part of the code that asked for it.
        return {

            # Store this named value inside a dictionary.
            "1. Bottom edge X direction, Y-min Z-min": (
                # Add this value to the current group.
                corners["1. X-min Y-min Z-min"],
                # Add this value to the current group.
                corners["2. X-max Y-min Z-min"],
            ),


            # Store this named value inside a dictionary.
            "2. Bottom edge X direction, Y-max Z-min": (
                # Add this value to the current group.
                corners["3. X-min Y-max Z-min"],
                # Add this value to the current group.
                corners["4. X-max Y-max Z-min"],
            ),


            # Store this named value inside a dictionary.
            "3. Bottom edge Y direction, X-min Z-min": (
                # Add this value to the current group.
                corners["1. X-min Y-min Z-min"],
                # Add this value to the current group.
                corners["3. X-min Y-max Z-min"],
            ),


            # Store this named value inside a dictionary.
            "4. Bottom edge Y direction, X-max Z-min": (
                # Add this value to the current group.
                corners["2. X-max Y-min Z-min"],
                # Add this value to the current group.
                corners["4. X-max Y-max Z-min"],
            ),


            # Store this named value inside a dictionary.
            "5. Top edge X direction, Y-min Z-max": (
                # Add this value to the current group.
                corners["5. X-min Y-min Z-max"],
                # Add this value to the current group.
                corners["6. X-max Y-min Z-max"],
            ),


            # Store this named value inside a dictionary.
            "6. Top edge X direction, Y-max Z-max": (
                # Add this value to the current group.
                corners["7. X-min Y-max Z-max"],
                # Add this value to the current group.
                corners["8. X-max Y-max Z-max"],
            ),


            # Store this named value inside a dictionary.
            "7. Top edge Y direction, X-min Z-max": (
                # Add this value to the current group.
                corners["5. X-min Y-min Z-max"],
                # Add this value to the current group.
                corners["7. X-min Y-max Z-max"],
            ),


            # Store this named value inside a dictionary.
            "8. Top edge Y direction, X-max Z-max": (
                # Add this value to the current group.
                corners["6. X-max Y-min Z-max"],
                # Add this value to the current group.
                corners["8. X-max Y-max Z-max"],
            ),


            # Store this named value inside a dictionary.
            "9. Vertical edge X-min Y-min": (
                # Add this value to the current group.
                corners["1. X-min Y-min Z-min"],
                # Add this value to the current group.
                corners["5. X-min Y-min Z-max"],
            ),


            # Store this named value inside a dictionary.
            "10. Vertical edge X-max Y-min": (
                # Add this value to the current group.
                corners["2. X-max Y-min Z-min"],
                # Add this value to the current group.
                corners["6. X-max Y-min Z-max"],
            ),


            # Store this named value inside a dictionary.
            "11. Vertical edge X-min Y-max": (
                # Add this value to the current group.
                corners["3. X-min Y-max Z-min"],
                # Add this value to the current group.
                corners["7. X-min Y-max Z-max"],
            ),


            # Store this named value inside a dictionary.
            "12. Vertical edge X-max Y-max": (
                # Add this value to the current group.
                corners["4. X-max Y-max Z-min"],
                # Add this value to the current group.
                corners["8. X-max Y-max Z-max"],
            ),
        }

    # Create the calculate edge deviation function.
    def calculate_edge_deviation(self, scan_edges, cad_edges):


        # Save a value in edge results.
        edge_results = {}


        # Repeat this code for every item in the group.
        for label in cad_edges:


            # Save several results into separate variable names.
            scan_start, scan_end = scan_edges[label]


            # Save several results into separate variable names.
            cad_start, cad_end = cad_edges[label]


            # Save a value in scan midpoint.
            scan_midpoint = (scan_start + scan_end) / 2.0


            # Save a value in cad midpoint.
            cad_midpoint = (cad_start + cad_end) / 2.0


            # Measure how long this vector is.
            scan_length = np.linalg.norm(scan_end - scan_start)


            # Measure how long this vector is.
            cad_length = np.linalg.norm(cad_end - cad_start)


            # Save a value in start difference vector.
            start_difference_vector = cad_start - scan_start


            # Save a value in end difference vector.
            end_difference_vector = cad_end - scan_end


            # Save a value in midpoint difference vector.
            midpoint_difference_vector = cad_midpoint - scan_midpoint


            # Measure how long this vector is.
            start_distance_m = np.linalg.norm(start_difference_vector)


            # Measure how long this vector is.
            end_distance_m = np.linalg.norm(end_difference_vector)


            # Measure how long this vector is.
            midpoint_distance_m = np.linalg.norm(midpoint_difference_vector)


            # Save a value in length difference m.
            length_difference_m = cad_length - scan_length


            # Save a value in edge results[label].
            edge_results[label] = {

                # Store this named value inside a dictionary.
                "scan_start": scan_start,


                # Store this named value inside a dictionary.
                "scan_end": scan_end,


                # Store this named value inside a dictionary.
                "cad_start": cad_start,


                # Store this named value inside a dictionary.
                "cad_end": cad_end,


                # Store this named value inside a dictionary.
                "scan_midpoint": scan_midpoint,


                # Store this named value inside a dictionary.
                "cad_midpoint": cad_midpoint,


                # Store this named value inside a dictionary.
                "scan_length_m": float(scan_length),


                # Store this named value inside a dictionary.
                "cad_length_m": float(cad_length),


                # Store this named value inside a dictionary.
                "signed_x_m": float(midpoint_difference_vector[0]),


                # Store this named value inside a dictionary.
                "signed_y_m": float(midpoint_difference_vector[1]),


                # Store this named value inside a dictionary.
                "signed_z_m": float(midpoint_difference_vector[2]),


                # Store this named value inside a dictionary.
                "absolute_x_m": float(abs(midpoint_difference_vector[0])),


                # Store this named value inside a dictionary.
                "absolute_y_m": float(abs(midpoint_difference_vector[1])),


                # Store this named value inside a dictionary.
                "absolute_z_m": float(abs(midpoint_difference_vector[2])),


                # Store this named value inside a dictionary.
                "start_distance_m": float(start_distance_m),


                # Store this named value inside a dictionary.
                "end_distance_m": float(end_distance_m),


                # Store this named value inside a dictionary.
                "midpoint_distance_m": float(midpoint_distance_m),


                # Store this named value inside a dictionary.
                "length_difference_m": float(length_difference_m),


                # Store this named value inside a dictionary.
                "absolute_length_difference_m": float(abs(length_difference_m)),
            }


        # Send this result back to the part of the code that asked for it.
        return edge_results

    # Create the describe signed difference function.
    def describe_signed_difference(self, axis, value_m):


        # Save a value in value cm.
        value_cm = value_m * 100


        # Check this condition before choosing what happens next.
        if abs(value_cm) < 0.005:
            # Send this result back to the part of the code that asked for it.
            return f"same {axis} position"


        # Check this condition before choosing what happens next.
        if axis == "X":


            # Check this condition before choosing what happens next.
            if value_cm > 0:
                # Send this result back to the part of the code that asked for it.
                return f"CAD/STL is {abs(value_cm):.2f} cm more positive in X than PCD/scan"


            # Send this result back to the part of the code that asked for it.
            return f"CAD/STL is {abs(value_cm):.2f} cm more negative in X than PCD/scan"


        # Check this condition before choosing what happens next.
        if axis == "Y":


            # Check this condition before choosing what happens next.
            if value_cm > 0:
                # Send this result back to the part of the code that asked for it.
                return f"CAD/STL is {abs(value_cm):.2f} cm more positive in Y than PCD/scan"


            # Send this result back to the part of the code that asked for it.
            return f"CAD/STL is {abs(value_cm):.2f} cm more negative in Y than PCD/scan"


        # Check this condition before choosing what happens next.
        if axis == "Z":


            # Check this condition before choosing what happens next.
            if value_cm > 0:
                # Send this result back to the part of the code that asked for it.
                return f"CAD/STL is {abs(value_cm):.2f} cm higher than PCD/scan"


            # Send this result back to the part of the code that asked for it.
            return f"CAD/STL is {abs(value_cm):.2f} cm lower than PCD/scan"


        # Send this result back to the part of the code that asked for it.
        return f"{axis} difference: {value_cm:.2f} cm"

    # Create the calculate edge deviation report function.
    def calculate_edge_deviation_report(self, scan_pcd, cad_pcd):


        # Save several results into separate variable names.
        scan_min_bound, scan_max_bound = self.get_robust_bounds(scan_pcd)


        # Save several results into separate variable names.
        cad_min_bound, cad_max_bound = self.get_robust_bounds(cad_pcd)


        # Save a value in scan corners.
        scan_corners = self.build_corners(
            # Add this value to the current group.
            scan_min_bound,
            # Run this line as one small step in the program.
            scan_max_bound
        )


        # Save a value in cad corners.
        cad_corners = self.build_corners(
            # Add this value to the current group.
            cad_min_bound,
            # Run this line as one small step in the program.
            cad_max_bound
        )


        # Save a value in scan edges.
        scan_edges = self.build_edges(scan_corners)


        # Save a value in cad edges.
        cad_edges = self.build_edges(cad_corners)


        # Save a value in edge results.
        edge_results = self.calculate_edge_deviation(
            # Add this value to the current group.
            scan_edges,
            # Run this line as one small step in the program.
            cad_edges
        )


        # Put these numbers into a NumPy array.
        midpoint_distances = np.array([
            # Run this line as one small step in the program.
            result["midpoint_distance_m"]
            # Repeat this code for every item in the group.
            for result in edge_results.values()
        # Run this line as one small step in the program.
        ])


        # Put these numbers into a NumPy array.
        start_distances = np.array([
            # Run this line as one small step in the program.
            result["start_distance_m"]
            # Repeat this code for every item in the group.
            for result in edge_results.values()
        # Run this line as one small step in the program.
        ])


        # Put these numbers into a NumPy array.
        end_distances = np.array([
            # Run this line as one small step in the program.
            result["end_distance_m"]
            # Repeat this code for every item in the group.
            for result in edge_results.values()
        # Run this line as one small step in the program.
        ])


        # Put these numbers into a NumPy array.
        length_differences = np.array([
            # Run this line as one small step in the program.
            result["absolute_length_difference_m"]
            # Repeat this code for every item in the group.
            for result in edge_results.values()
        # Run this line as one small step in the program.
        ])


        # Send this result back to the part of the code that asked for it.
        return {

            # Store this named value inside a dictionary.
            "scan_min_bound": scan_min_bound,


            # Store this named value inside a dictionary.
            "scan_max_bound": scan_max_bound,


            # Store this named value inside a dictionary.
            "cad_min_bound": cad_min_bound,


            # Store this named value inside a dictionary.
            "cad_max_bound": cad_max_bound,


            # Store this named value inside a dictionary.
            "edge_results": edge_results,


            # Store this named value inside a dictionary.
            "midpoint_mean_m": float(np.mean(midpoint_distances)),


            # Store this named value inside a dictionary.
            "midpoint_median_m": float(np.median(midpoint_distances)),


            # Store this named value inside a dictionary.
            "midpoint_rmse_m": float(np.sqrt(np.mean(midpoint_distances ** 2))),


            # Store this named value inside a dictionary.
            "midpoint_max_m": float(np.max(midpoint_distances)),


            # Store this named value inside a dictionary.
            "start_mean_m": float(np.mean(start_distances)),


            # Store this named value inside a dictionary.
            "end_mean_m": float(np.mean(end_distances)),


            # Store this named value inside a dictionary.
            "length_mean_m": float(np.mean(length_differences)),


            # Store this named value inside a dictionary.
            "length_median_m": float(np.median(length_differences)),


            # Store this named value inside a dictionary.
            "length_rmse_m": float(np.sqrt(np.mean(length_differences ** 2))),


            # Store this named value inside a dictionary.
            "length_max_m": float(np.max(length_differences)),
        }

    # Create the print edge deviation report function.
    def print_edge_deviation_report(self, scan_pcd, cad_pcd):


        # Show helpful information on the screen.
        print("")


        # Show helpful information on the screen.
        print("Measuring 12-edge deviation between scan and CAD...")


        # Save a value in result.
        result = self.calculate_edge_deviation_report(
            # Add this value to the current group.
            scan_pcd,
            # Run this line as one small step in the program.
            cad_pcd
        )


        # Show helpful information on the screen.
        print("")
        # Show helpful information on the screen.
        print("12-edge deviation report:")
        # Show helpful information on the screen.
        print("Reference: STL/CAD model")
        # Show helpful information on the screen.
        print("Measured : PCD scan")
        # Show helpful information on the screen.
        print("Method   : robust bounding-box edge comparison")
        # Show helpful information on the screen.
        print("Unit     : centimeters")
        # Show helpful information on the screen.
        print("")


        # Show helpful information on the screen.
        print("Bounds used")
        # Round the numbers so they are easier to read.
        print(f"  Scan min bound: {np.round(result['scan_min_bound'], 4)}")
        # Round the numbers so they are easier to read.
        print(f"  Scan max bound: {np.round(result['scan_max_bound'], 4)}")
        # Round the numbers so they are easier to read.
        print(f"  CAD min bound : {np.round(result['cad_min_bound'], 4)}")
        # Round the numbers so they are easier to read.
        print(f"  CAD max bound : {np.round(result['cad_max_bound'], 4)}")
        # Show helpful information on the screen.
        print("")


        # Show helpful information on the screen.
        print("Edge midpoint deviation summary")
        # Show helpful information on the screen.
        print(f"  Mean midpoint difference   : {result['midpoint_mean_m'] * 100:.2f} cm")
        # Show helpful information on the screen.
        print(f"  Median midpoint difference : {result['midpoint_median_m'] * 100:.2f} cm")
        # Show helpful information on the screen.
        print(f"  RMSE midpoint difference   : {result['midpoint_rmse_m'] * 100:.2f} cm")
        # Show helpful information on the screen.
        print(f"  Maximum midpoint difference: {result['midpoint_max_m'] * 100:.2f} cm")
        # Show helpful information on the screen.
        print("")


        # Show helpful information on the screen.
        print("Edge endpoint deviation summary")
        # Show helpful information on the screen.
        print(f"  Mean start-point difference: {result['start_mean_m'] * 100:.2f} cm")
        # Show helpful information on the screen.
        print(f"  Mean end-point difference  : {result['end_mean_m'] * 100:.2f} cm")
        # Show helpful information on the screen.
        print("")


        # Show helpful information on the screen.
        print("Edge length deviation summary")
        # Show helpful information on the screen.
        print(f"  Mean length difference     : {result['length_mean_m'] * 100:.2f} cm")
        # Show helpful information on the screen.
        print(f"  Median length difference   : {result['length_median_m'] * 100:.2f} cm")
        # Show helpful information on the screen.
        print(f"  RMSE length difference     : {result['length_rmse_m'] * 100:.2f} cm")
        # Show helpful information on the screen.
        print(f"  Maximum length difference  : {result['length_max_m'] * 100:.2f} cm")
        # Show helpful information on the screen.
        print("")


        # Show helpful information on the screen.
        print("Detailed 12-edge differences")


        # Repeat this code for every item in the group.
        for label, edge_result in result["edge_results"].items():


            # Show helpful information on the screen.
            print(label)


            # Round the numbers so they are easier to read.
            print(f"  CAD/STL start point      : {np.round(edge_result['cad_start'], 4)}")
            # Round the numbers so they are easier to read.
            print(f"  PCD/scan start point     : {np.round(edge_result['scan_start'], 4)}")
            # Round the numbers so they are easier to read.
            print(f"  CAD/STL end point        : {np.round(edge_result['cad_end'], 4)}")
            # Round the numbers so they are easier to read.
            print(f"  PCD/scan end point       : {np.round(edge_result['scan_end'], 4)}")


            # Show helpful information on the screen.
            print(f"  Start point difference   : {edge_result['start_distance_m'] * 100:.2f} cm")


            # Show helpful information on the screen.
            print(f"  End point difference     : {edge_result['end_distance_m'] * 100:.2f} cm")


            # Show helpful information on the screen.
            print(f"  Midpoint 3D difference   : {edge_result['midpoint_distance_m'] * 100:.2f} cm")


            # Show helpful information on the screen.
            print(f"  X midpoint difference    : {edge_result['absolute_x_m'] * 100:.2f} cm")
            # Show helpful information on the screen.
            print(f"  Y midpoint difference    : {edge_result['absolute_y_m'] * 100:.2f} cm")
            # Show helpful information on the screen.
            print(f"  Z midpoint difference    : {edge_result['absolute_z_m'] * 100:.2f} cm")


            # Show helpful information on the screen.
            print(f"  X direction              : {self.describe_signed_difference('X', edge_result['signed_x_m'])}")


            # Show helpful information on the screen.
            print(f"  Y direction              : {self.describe_signed_difference('Y', edge_result['signed_y_m'])}")


            # Show helpful information on the screen.
            print(f"  Z direction              : {self.describe_signed_difference('Z', edge_result['signed_z_m'])}")


            # Show helpful information on the screen.
            print(f"  CAD/STL edge length      : {edge_result['cad_length_m'] * 100:.2f} cm")


            # Show helpful information on the screen.
            print(f"  PCD/scan edge length     : {edge_result['scan_length_m'] * 100:.2f} cm")


            # Check this condition before choosing what happens next.
            if edge_result["length_difference_m"] > 0:
                # Show helpful information on the screen.
                print(f"  Length direction         : CAD/STL edge is {edge_result['absolute_length_difference_m'] * 100:.2f} cm longer")


            # Check another condition if the previous one was false.
            elif edge_result["length_difference_m"] < 0:
                # Show helpful information on the screen.
                print(f"  Length direction         : CAD/STL edge is {edge_result['absolute_length_difference_m'] * 100:.2f} cm shorter")


            # Use this path when the earlier checks were false.
            else:
                # Show helpful information on the screen.
                print("  Length direction         : same length")


            # Show helpful information on the screen.
            print("")

    # Create the print alignment deviation report function.
    def print_alignment_deviation_report(self, scan_pcd, cad_pcd):


        # Run this line as one small step in the program.
        self.print_edge_deviation_report(
            # Add this value to the current group.
            scan_pcd,
            # Run this line as one small step in the program.
            cad_pcd
        )
