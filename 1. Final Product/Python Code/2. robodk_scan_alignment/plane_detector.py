# Bring in copy so this file can use it.
import copy
# Bring in numpy so this file can use it.
import numpy as np


# Create the PlaneDetector class, which groups related code together.
class PlaneDetector:


    # Create the setup function that runs when this object is made.
    def __init__(self, config):
        # Save this value inside the object for later.
        self.config = config

    # Create the detect planes function.
    def detect_planes(self, point_cloud, max_planes=None):
        # Check this condition before choosing what happens next.
        if max_planes is None:
            # Save a value in max planes.
            max_planes = self.config.MAX_PLANES_TO_CHECK

        # Make a safe copy so the original object does not change.
        remaining = copy.deepcopy(point_cloud)
        # Save a value in planes.
        planes = []

        # Repeat this code for every item in the group.
        for _ in range(max_planes):

            # Count how many points are inside this object.
            if len(remaining.points) < self.config.MIN_PLANE_POINTS:
                # Stop this loop early.
                break

            # Find one flat surface inside the point cloud.
            plane_model, inliers = remaining.segment_plane(
                # Save a value in distance threshold.
                distance_threshold=self.config.PLANE_DISTANCE_THRESHOLD,
                # Save a value in ransac n.
                ransac_n=self.config.PLANE_RANSAC_N,
                # Save a value in num iterations.
                num_iterations=self.config.PLANE_NUM_ITERATIONS
            )

            # Count how many points are inside this object.
            if len(inliers) < self.config.MIN_PLANE_POINTS:
                # Stop this loop early.
                break

            # Save several results into separate variable names.
            a, b, c, d = plane_model

            # Put these numbers into a NumPy array.
            normal = np.array([a, b, c], dtype=np.float64)

            # Measure how long this vector is.
            normal_length = np.linalg.norm(normal)

            # Check this condition before choosing what happens next.
            if normal_length == 0:
                # Skip the rest of this loop and go to the next item.
                continue

            # Save a value in normal.
            normal = normal / normal_length

            # Pick only the points with these index numbers.
            plane_cloud = remaining.select_by_index(inliers)
            # Change the Open3D points into NumPy numbers.
            points = np.asarray(plane_cloud.points)
            # Save a value in centroid.
            centroid = points.mean(axis=0)

            # Add this item to the list.
            planes.append({
                # Store this named value inside a dictionary.
                "plane_model": plane_model,
                # Store this named value inside a dictionary.
                "normal": normal,
                # Store this named value inside a dictionary.
                "centroid": centroid,
                # Count how many points are inside this object.
                "n_points": len(inliers),
                # Store this named value inside a dictionary.
                "cloud": plane_cloud,
            # Run this line as one small step in the program.
            })

            # Pick only the points with these index numbers.
            remaining = remaining.select_by_index(inliers, invert=True)

        # Send this result back to the part of the code that asked for it.
        return planes

    # Create the print detected planes function.
    def print_detected_planes(self, planes, title):
        # Show helpful information on the screen.
        print("")
        # Show helpful information on the screen.
        print(title)
        # Show helpful information on the screen.
        print("Detected planes:", len(planes))

        # Repeat this code for every item in the group.
        for index, plane in enumerate(planes, start=1):
            # Show helpful information on the screen.
            print(f"Plane {index}")
            # Round the numbers so they are easier to read.
            print("  Normal  :", np.round(plane["normal"], 4))
            # Round the numbers so they are easier to read.
            print("  Centroid:", np.round(plane["centroid"], 4))
            # Show helpful information on the screen.
            print("  Points  :", plane["n_points"])

        # Show helpful information on the screen.
        print("")

    # Create the classify cabinet planes function.
    def classify_cabinet_planes(self, planes):


        # Check this condition before choosing what happens next.
        if len(planes) == 0:
            # Stop the program and show a clear error message.
            raise Exception("No cabinet planes found.")

        # Sort the items into a better order.
        sorted_planes = sorted(
            # Add this value to the current group.
            planes,
            # Save a value in key.
            key=lambda plane: plane["n_points"],
            # Save a value in reverse.
            reverse=True
        )

        # Save a value in back panel.
        back_panel = sorted_planes[0]
        # Save a value in back normal.
        back_normal = back_panel["normal"]

        # Save a value in perpendicular planes.
        perpendicular_planes = []

        # Repeat this code for every item in the group.
        for plane in sorted_planes[1:]:
            # Compare two directions using a dot product.
            dot_value = abs(np.dot(plane["normal"], back_normal))

            # Check this condition before choosing what happens next.
            if dot_value < 0.35:
                # Add this item to the list.
                perpendicular_planes.append(plane)

        # Check this condition before choosing what happens next.
        if len(perpendicular_planes) == 0:
            # Stop the program and show a clear error message.
            raise Exception(
                # Run this line as one small step in the program.
                "No perpendicular cabinet panel found. "
                # Run this line as one small step in the program.
                "The scan needs at least the back panel and one side/bottom/top panel."
            )

        # Save a value in reference panel.
        reference_panel = perpendicular_planes[0]

        # Send this result back to the part of the code that asked for it.
        return {
            # Store this named value inside a dictionary.
            "back_panel": back_panel,
            # Store this named value inside a dictionary.
            "reference_panel": reference_panel,
            # Store this named value inside a dictionary.
            "perpendicular_planes": perpendicular_planes,
        }

    # Create the classify floor and walls function.
    def classify_floor_and_walls(self, planes):
        # Save a value in floor.
        floor = None
        # Save a value in walls.
        walls = []

        # Repeat this code for every item in the group.
        for plane in planes:
            # Save a value in normal.
            normal = plane["normal"]

            # Save a value in horizontal score.
            horizontal_score = abs(
                # Compare two directions using a dot product.
                np.dot(normal, np.array([0.0, 0.0, 1.0]))
            )

            # Check this condition before choosing what happens next.
            if horizontal_score > 0.75:
                # Check this condition before choosing what happens next.
                if floor is None or plane["centroid"][2] < floor["centroid"][2]:
                    # Save a value in floor.
                    floor = plane

            # Check another condition if the previous one was false.
            elif horizontal_score < 0.25:
                # Add this item to the list.
                walls.append(plane)

        # Check this condition before choosing what happens next.
        if floor is None:
            # Stop the program and show a clear error message.
            raise Exception("No floor plane found.")

        # Check this condition before choosing what happens next.
        if len(walls) == 0:
            # Stop the program and show a clear error message.
            raise Exception("No wall plane found.")

        # Send this result back to the part of the code that asked for it.
        return floor, walls

    # Create the label room planes function.
    def label_room_planes(self, planes, room_center):
        # Save a value in labelled planes.
        labelled_planes = {}

        # Save a value in horizontal planes.
        horizontal_planes = []
        # Save a value in vertical planes.
        vertical_planes = []

        # Repeat this code for every item in the group.
        for plane in planes:
            # Save a value in normal.
            normal = plane["normal"]

            # Save a value in horizontal score.
            horizontal_score = abs(
                # Compare two directions using a dot product.
                np.dot(normal, np.array([0.0, 0.0, 1.0]))
            )

            # Check this condition before choosing what happens next.
            if horizontal_score > 0.75:
                # Add this item to the list.
                horizontal_planes.append(plane)

            # Check another condition if the previous one was false.
            elif horizontal_score < 0.25:
                # Add this item to the list.
                vertical_planes.append(plane)

        # Check this condition before choosing what happens next.
        if len(horizontal_planes) > 0:
            # Save a value in floor.
            floor = min(horizontal_planes, key=lambda p: p["centroid"][2])
            # Save a value in labelled planes["Floor"].
            labelled_planes["Floor"] = floor

        # Repeat this code for every item in the group.
        for plane in vertical_planes:
            # Save a value in normal.
            normal = plane["normal"]
            # Save a value in centroid.
            centroid = plane["centroid"]

            # Check this condition before choosing what happens next.
            if abs(normal[0]) >= abs(normal[1]):
                # Check this condition before choosing what happens next.
                if centroid[0] < room_center[0]:
                    # Save a value in label.
                    label = "Wall X-min"
                # Use this path when the earlier checks were false.
                else:
                    # Save a value in label.
                    label = "Wall X-max"
            # Use this path when the earlier checks were false.
            else:
                # Check this condition before choosing what happens next.
                if centroid[1] < room_center[1]:
                    # Save a value in label.
                    label = "Wall Y-min"
                # Use this path when the earlier checks were false.
                else:
                    # Save a value in label.
                    label = "Wall Y-max"

            # Check this condition before choosing what happens next.
            if label not in labelled_planes:
                # Save a value in labelled planes[label].
                labelled_planes[label] = plane
            # Use this path when the earlier checks were false.
            else:
                # Check this condition before choosing what happens next.
                if plane["n_points"] > labelled_planes[label]["n_points"]:
                    # Save a value in labelled planes[label].
                    labelled_planes[label] = plane

        # Send this result back to the part of the code that asked for it.
        return labelled_planes
