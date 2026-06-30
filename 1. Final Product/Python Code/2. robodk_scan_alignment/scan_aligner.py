# Bring in copy so this file can use it.
import copy
# Bring in itertools so this file can use it.
import itertools

# Bring in numpy so this file can use it.
import numpy as np
# Bring in open3d so this file can use it.
import open3d as o3d


# Create the ScanAligner class, which groups related code together.
class ScanAligner:


    # Create the setup function that runs when this object is made.
    def __init__(self, config, plane_detector):
        # Save this value inside the object for later.
        self.config = config
        # Save this value inside the object for later.
        self.plane_detector = plane_detector

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
            1.0,
            # Save a value in axis.
            axis=0
        )

        # Get a safe edge value while ignoring extreme noisy points.
        max_bound = np.percentile(
            # Add this value to the current group.
            points,
            # Add this value to the current group.
            99.0,
            # Save a value in axis.
            axis=0
        )

        # Send this result back to the part of the code that asked for it.
        return min_bound, max_bound

    # Create the make transform from rotation function.
    def make_transform_from_rotation(self, rotation_matrix):
        # Make an identity matrix, which means no movement yet.
        transformation = np.eye(4)
        # Save several results into separate variable names.
        transformation[:3, :3] = rotation_matrix
        # Send this result back to the part of the code that asked for it.
        return transformation

    # Create the make transform from translation function.
    def make_transform_from_translation(self, translation):
        # Make an identity matrix, which means no movement yet.
        transformation = np.eye(4)
        # Save several results into separate variable names.
        transformation[:3, 3] = translation
        # Send this result back to the part of the code that asked for it.
        return transformation

    # Create the rotation x function.
    def rotation_x(self, angle_radians):
        # Save a value in cosine angle.
        cosine_angle = np.cos(angle_radians)
        # Save a value in sine angle.
        sine_angle = np.sin(angle_radians)

        # Put these numbers into a NumPy array.
        return np.array([
            # Start a group of values.
            [1.0, 0.0, 0.0],
            # Start a group of values.
            [0.0, cosine_angle, -sine_angle],
            # Start a group of values.
            [0.0, sine_angle, cosine_angle]
        # Run this line as one small step in the program.
        ])

    # Create the rotation y function.
    def rotation_y(self, angle_radians):
        # Save a value in cosine angle.
        cosine_angle = np.cos(angle_radians)
        # Save a value in sine angle.
        sine_angle = np.sin(angle_radians)

        # Put these numbers into a NumPy array.
        return np.array([
            # Start a group of values.
            [cosine_angle, 0.0, sine_angle],
            # Start a group of values.
            [0.0, 1.0, 0.0],
            # Start a group of values.
            [-sine_angle, 0.0, cosine_angle]
        # Run this line as one small step in the program.
        ])

    # Create the rotation z function.
    def rotation_z(self, angle_radians):
        # Save a value in cosine angle.
        cosine_angle = np.cos(angle_radians)
        # Save a value in sine angle.
        sine_angle = np.sin(angle_radians)

        # Put these numbers into a NumPy array.
        return np.array([
            # Start a group of values.
            [cosine_angle, -sine_angle, 0.0],
            # Start a group of values.
            [sine_angle, cosine_angle, 0.0],
            # Start a group of values.
            [0.0, 0.0, 1.0]
        # Run this line as one small step in the program.
        ])

    # Create the generate right angle rotations function.
    def generate_right_angle_rotations(self):


        # Save a value in angles.
        angles = [
            # Add this value to the current group.
            0.0,
            # Add this value to the current group.
            np.pi / 2.0,
            # Add this value to the current group.
            np.pi,
            # Run this line as one small step in the program.
            3.0 * np.pi / 2.0
        ]

        # Save a value in rotations.
        rotations = []

        # Repeat this code for every item in the group.
        for rx, ry, rz in itertools.product(angles, angles, angles):
            # Save a value in rotation matrix.
            rotation_matrix = (
                # Run this line as one small step in the program.
                self.rotation_z(rz)
                # Run this line as one small step in the program.
                @ self.rotation_y(ry)
                # Run this line as one small step in the program.
                @ self.rotation_x(rx)
            )

            # Round the numbers so they are easier to read.
            rounded_matrix = np.round(rotation_matrix, 6)

            # Save a value in is duplicate.
            is_duplicate = False

            # Repeat this code for every item in the group.
            for existing_rotation in rotations:
                # Check this condition before choosing what happens next.
                if np.allclose(
                    # Add this value to the current group.
                    rounded_matrix,
                    # Add this value to the current group.
                    existing_rotation,
                    # Save a value in atol.
                    atol=1e-6
                # Run this line as one small step in the program.
                ):
                    # Save a value in is duplicate.
                    is_duplicate = True
                    # Stop this loop early.
                    break

            # Check this condition before choosing what happens next.
            if not is_duplicate:
                # Add this item to the list.
                rotations.append(rounded_matrix)

        # Show helpful information on the screen.
        print("")
        # Show helpful information on the screen.
        print("Generated right-angle CAD orientation candidates:", len(rotations))

        # Send this result back to the part of the code that asked for it.
        return rotations

    # Calculate which way the surface points are facing.
    def estimate_normals(self, point_cloud):
        # Count how many points are inside this object.
        if len(point_cloud.points) == 0:
            # Stop the program and show a clear error message.
            raise Exception("Cannot estimate normals on an empty point cloud.")

        # Calculate which way the surface points are facing.
        point_cloud.estimate_normals(
            # Save a value in search param.
            search_param=o3d.geometry.KDTreeSearchParamHybrid(
                # Save a value in radius.
                radius=self.config.VOXEL_SIZE * 2.0,
                # Save a value in max nn.
                max_nn=30
            )
        )

        # Send this result back to the part of the code that asked for it.
        return point_cloud

    # Create the structure scan function.
    def structure_scan(self, scan_down):


        # Show helpful information on the screen.
        print("")
        # Show helpful information on the screen.
        print("=" * 70)
        # Show helpful information on the screen.
        print("Keeping scan in original robot-base coordinate frame")
        # Show helpful information on the screen.
        print("=" * 70)

        # Make a safe copy so the original object does not change.
        scan_structured = copy.deepcopy(scan_down)
        # Calculate which way the surface points are facing.
        scan_structured = self.estimate_normals(scan_structured)

        # Make an identity matrix, which means no movement yet.
        structure_transform = np.eye(4)

        # Send this result back to the part of the code that asked for it.
        return scan_structured, structure_transform

    # Create the structure cad to floor function.
    def structure_cad_to_floor(self, cad_down):


        # Show helpful information on the screen.
        print("")
        # Show helpful information on the screen.
        print("=" * 70)
        # Show helpful information on the screen.
        print("Keeping CAD in loaded orientation before orientation search")
        # Show helpful information on the screen.
        print("=" * 70)

        # Make a safe copy so the original object does not change.
        cad_structured = copy.deepcopy(cad_down)
        # Calculate which way the surface points are facing.
        cad_structured = self.estimate_normals(cad_structured)

        # Make an identity matrix, which means no movement yet.
        cad_structure_transform = np.eye(4)

        # Send this result back to the part of the code that asked for it.
        return cad_structured, cad_structure_transform

    # Create the center align cad function.
    def center_align_cad(self, scan_structured, cad_down):


        # Create a simple box around the object.
        scan_bounding_box = scan_structured.get_axis_aligned_bounding_box()
        # Create a simple box around the object.
        cad_bounding_box = cad_down.get_axis_aligned_bounding_box()

        # Save a value in scan center.
        scan_center = scan_bounding_box.get_center()
        # Save a value in cad center.
        cad_center = cad_bounding_box.get_center()

        # Save a value in scan extent.
        scan_extent = scan_bounding_box.get_extent()
        # Save a value in cad extent.
        cad_extent = cad_bounding_box.get_extent()

        # Save a value in initial translation.
        initial_translation = scan_center - cad_center

        # Show helpful information on the screen.
        print("")
        # Show helpful information on the screen.
        print("=" * 70)
        # Show helpful information on the screen.
        print("Center-aligning CAD to scan using bounding-box center")
        # Show helpful information on the screen.
        print("=" * 70)
        # Round the numbers so they are easier to read.
        print("Scan bbox min   :", np.round(scan_bounding_box.get_min_bound(), 4))
        # Round the numbers so they are easier to read.
        print("Scan bbox max   :", np.round(scan_bounding_box.get_max_bound(), 4))
        # Round the numbers so they are easier to read.
        print("Scan bbox center:", np.round(scan_center, 4))
        # Round the numbers so they are easier to read.
        print("Scan bbox extent:", np.round(scan_extent, 4))
        # Show helpful information on the screen.
        print("")
        # Round the numbers so they are easier to read.
        print("CAD bbox min    :", np.round(cad_bounding_box.get_min_bound(), 4))
        # Round the numbers so they are easier to read.
        print("CAD bbox max    :", np.round(cad_bounding_box.get_max_bound(), 4))
        # Round the numbers so they are easier to read.
        print("CAD bbox center :", np.round(cad_center, 4))
        # Round the numbers so they are easier to read.
        print("CAD bbox extent :", np.round(cad_extent, 4))
        # Show helpful information on the screen.
        print("")
        # Round the numbers so they are easier to read.
        print("Initial XYZ center shift:", np.round(initial_translation, 4))

        # Make a safe copy so the original object does not change.
        cad_initial = copy.deepcopy(cad_down)
        # Move the 3D object by a chosen amount.
        cad_initial.translate(initial_translation)

        # Put these numbers into a NumPy array.
        manual_translation = np.array([
            # Add this value to the current group.
            self.config.MANUAL_TX,
            # Add this value to the current group.
            self.config.MANUAL_TY,
            # Run this line as one small step in the program.
            self.config.MANUAL_TZ
        # Run this line as one small step in the program.
        ])

        # Check this condition before choosing what happens next.
        if np.any(manual_translation != 0.0):
            # Move the 3D object by a chosen amount.
            cad_initial.translate(manual_translation)
            # Show helpful information on the screen.
            print("Applied manual shift:", manual_translation.tolist())

        # Make an identity matrix, which means no movement yet.
        center_transform = np.eye(4)
        # Save several results into separate variable names.
        center_transform[:3, 3] = initial_translation + manual_translation

        # Calculate which way the surface points are facing.
        cad_initial = self.estimate_normals(cad_initial)

        # Send this result back to the part of the code that asked for it.
        return cad_initial, center_transform

    # Create the run icp function.
    def run_icp(self, cad_initial, scan_structured):
        # Show helpful information on the screen.
        print("")
        # Show helpful information on the screen.
        print("Running cabinet ICP refinement.")

        # Use ICP to carefully line up the CAD model with the scan.
        registration = o3d.pipelines.registration.registration_icp(
            # Add this value to the current group.
            cad_initial,
            # Add this value to the current group.
            scan_structured,
            # Add this value to the current group.
            self.config.ICP_DISTANCE,
            # Make an identity matrix, which means no movement yet.
            np.eye(4),
            # Run this line as one small step in the program.
            o3d.pipelines.registration.TransformationEstimationPointToPlane()
        )

        # Show helpful information on the screen.
        print("ICP fitness:", registration.fitness)
        # Show helpful information on the screen.
        print("ICP RMSE:", registration.inlier_rmse)

        # Show helpful information on the screen.
        print("ICP transform:")
        # Show helpful information on the screen.
        print(registration.transformation)

        # Make a safe copy so the original object does not change.
        cad_final = copy.deepcopy(cad_initial)
        # Move or rotate the 3D object using a transform matrix.
        cad_final.transform(registration.transformation)

        # Calculate which way the surface points are facing.
        cad_final = self.estimate_normals(cad_final)

        # Send this result back to the part of the code that asked for it.
        return cad_final, registration.transformation

    # Create the align cad to scan by orientation search function.
    def align_cad_to_scan_by_orientation_search(self, scan_structured, cad_structured):


        # Show helpful information on the screen.
        print("")
        # Show helpful information on the screen.
        print("=" * 70)
        # Show helpful information on the screen.
        print("Starting CAD orientation search")
        # Show helpful information on the screen.
        print("=" * 70)

        # Calculate which way the surface points are facing.
        scan_structured = self.estimate_normals(scan_structured)

        # Save a value in rotations.
        rotations = self.generate_right_angle_rotations()

        # Save a value in best result.
        best_result = None
        # Save a value in best score.
        best_score = -np.inf

        # Repeat this code for every item in the group.
        for index, rotation_matrix in enumerate(rotations, start=1):
            # Show helpful information on the screen.
            print("")
            # Show helpful information on the screen.
            print("-" * 70)
            # Show helpful information on the screen.
            print(f"Testing CAD orientation candidate {index}/{len(rotations)}")
            # Show helpful information on the screen.
            print("-" * 70)

            # Save a value in orientation transform.
            orientation_transform = self.make_transform_from_rotation(
                # Run this line as one small step in the program.
                rotation_matrix
            )

            # Make a safe copy so the original object does not change.
            cad_oriented = copy.deepcopy(cad_structured)
            # Move or rotate the 3D object using a transform matrix.
            cad_oriented.transform(orientation_transform)
            # Calculate which way the surface points are facing.
            cad_oriented = self.estimate_normals(cad_oriented)

            # Save several results into separate variable names.
            cad_initial, center_transform = self.center_align_cad(
                # Add this value to the current group.
                scan_structured,
                # Run this line as one small step in the program.
                cad_oriented
            )

            # Try this code, but be ready if something goes wrong.
            try:
                # Save several results into separate variable names.
                cad_final, icp_transform = self.run_icp(
                    # Add this value to the current group.
                    cad_initial,
                    # Run this line as one small step in the program.
                    scan_structured
                )
            # Handle the error so the program can continue or explain it.
            except Exception as error:
                # Show helpful information on the screen.
                print("ICP failed for this orientation:", error)
                # Skip the rest of this loop and go to the next item.
                continue

            # Save a value in evaluation.
            evaluation = o3d.pipelines.registration.evaluate_registration(
                # Add this value to the current group.
                cad_final,
                # Add this value to the current group.
                scan_structured,
                # Run this line as one small step in the program.
                self.config.ICP_DISTANCE
            )

            # Save a value in fitness.
            fitness = float(evaluation.fitness)
            # Save a value in rmse.
            rmse = float(evaluation.inlier_rmse)

            # Save a value in score.
            score = fitness - rmse

            # Show helpful information on the screen.
            print("")
            # Show helpful information on the screen.
            print("Candidate result:")
            # Show helpful information on the screen.
            print("Fitness:", fitness)
            # Show helpful information on the screen.
            print("RMSE   :", rmse)
            # Show helpful information on the screen.
            print("Score  :", score)

            # Save a value in full transform.
            full_transform = (
                # Run this line as one small step in the program.
                icp_transform
                # Run this line as one small step in the program.
                @ center_transform
                # Run this line as one small step in the program.
                @ orientation_transform
            )

            # Check this condition before choosing what happens next.
            if best_result is None or score > best_score:
                # Save a value in best score.
                best_score = score
                # Save a value in best result.
                best_result = {
                    # Store this named value inside a dictionary.
                    "candidate_index": index,
                    # Store this named value inside a dictionary.
                    "cad_initial": cad_initial,
                    # Store this named value inside a dictionary.
                    "cad_final": cad_final,
                    # Store this named value inside a dictionary.
                    "full_transform": full_transform,
                    # Store this named value inside a dictionary.
                    "orientation_transform": orientation_transform,
                    # Store this named value inside a dictionary.
                    "center_transform": center_transform,
                    # Store this named value inside a dictionary.
                    "icp_transform": icp_transform,
                    # Store this named value inside a dictionary.
                    "fitness": fitness,
                    # Store this named value inside a dictionary.
                    "rmse": rmse,
                    # Store this named value inside a dictionary.
                    "score": score,
                }

        # Check this condition before choosing what happens next.
        if best_result is None:
            # Stop the program and show a clear error message.
            raise Exception("No valid CAD orientation candidate could be aligned.")

        # Show helpful information on the screen.
        print("")
        # Show helpful information on the screen.
        print("=" * 70)
        # Show helpful information on the screen.
        print("Best CAD orientation selected")
        # Show helpful information on the screen.
        print("=" * 70)
        # Show helpful information on the screen.
        print("Candidate index:", best_result["candidate_index"])
        # Show helpful information on the screen.
        print("Fitness        :", best_result["fitness"])
        # Show helpful information on the screen.
        print("RMSE           :", best_result["rmse"])
        # Show helpful information on the screen.
        print("Score          :", best_result["score"])
        # Show helpful information on the screen.
        print("")
        # Show helpful information on the screen.
        print("Best CAD-to-scan transform:")
        # Show helpful information on the screen.
        print(best_result["full_transform"])

        # Send this result back to the part of the code that asked for it.
        return (
            # Add this value to the current group.
            best_result["cad_initial"],
            # Add this value to the current group.
            best_result["cad_final"],
            # Add this value to the current group.
            best_result["full_transform"],
            # Add this value to the current group.
            best_result["orientation_transform"],
            # Add this value to the current group.
            best_result["center_transform"],
            # Add this value to the current group.
            best_result["icp_transform"],
        )

    # Create the create floor locked transform function.
    def create_floor_locked_transform(self, transformation):
        # Send this result back to the part of the code that asked for it.
        return transformation
