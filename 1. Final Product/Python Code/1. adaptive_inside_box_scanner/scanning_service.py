import cv2  # Loads OpenCV so the code can work with camera images.
import numpy as np  # Loads NumPy as np so the code can do fast number and matrix math.
import open3d as o3d  # Loads Open3D so the code can work with 3D point clouds.

from auto_box_detector import AutoBoxDetector  # Gets AutoBoxDetector from auto_box_detector so this file can use it.
from auto_centering_service import AutoCenteringService  # Gets AutoCenteringService from auto_centering_service so this file can use it.
from point_cloud_service import PointCloudService  # Gets PointCloudService from point_cloud_service so this file can use it.
from pose_generator import AdaptivePoseGenerator  # Gets AdaptivePoseGenerator from pose_generator so this file can use it.
from realsense_camera import RealSenseCamera  # Gets RealSenseCamera from realsense_camera so this file can use it.
from robot_controller import RobotController  # Gets RobotController from robot_controller so this file can use it.
from transform_utils import print_transform, robodk_mat_to_numpy, xyzrxryrz_to_numpy  # Gets print_transform, robodk_mat_to_numpy, xyzrxryrz_to_numpy from transform_utils so this file can use it.


class AdaptiveInsideBoxScanner:  # Makes the main scanner that controls the robot, camera, and point clouds.
    def __init__(self, config):  # Makes a function named   init  .
        self.config = config  # Stores the scanner settings so the program can use them.
        self.robot_controller = None  # Saves robot controller inside this object so other methods can use it.
        self.camera = RealSenseCamera(config)  # Saves camera inside this object so other methods can use it.
        self.point_cloud_service = PointCloudService(config)  # Saves point cloud service inside this object so other methods can use it.
        self.pose_generator = AdaptivePoseGenerator(config)  # Saves pose generator inside this object so other methods can use it.
        self.detector = AutoBoxDetector(config)  # Saves detector inside this object so other methods can use it.

        self.combined_point_cloud = o3d.geometry.PointCloud()  # Stores all accepted scans merged together.
        self.successful_scans = 0  # Saves successful scans inside this object so other methods can use it.
        self.skipped_scans = 0  # Saves skipped scans inside this object so other methods can use it.
        self.unsafe_scans = 0  # Saves unsafe scans inside this object so other methods can use it.
        self.failed_moves = 0  # Saves failed moves inside this object so other methods can use it.

    def scan_current_position(self, label, T_base_camera_actual, adaptive_bounds=None):  # Scans the cabinet from the robot current position.
        point_cloud = self.camera.capture_stable_pointcloud(  # Stores the 3D points captured by the camera.
            self.config.CAPTURE_FRAMES_PER_POSITION,  # Adds one item to the multi-line value.
        )  # Closes the multi-line code started above.

        if point_cloud is None:  # Checks if this value is missing.
            print(f"WARNING: Empty point cloud at {label}.")  # Shows a message in the console.
            return None  # Gives this result back to the part of the code that called it.

        print(f"Captured raw camera points at {label}: {len(point_cloud.points):,}")  # Shows a message in the console.
        self.point_cloud_service.print_cloud_bounds(  # Shows the size and position information for this point cloud.
            f"Raw camera-frame scan - {label}",  # Adds one item to the multi-line value.
            point_cloud,  # Adds one item to the multi-line value.
        )  # Closes the multi-line code started above.

        if adaptive_bounds is not None:  # Checks if this value exists before using it.
            point_cloud = self.point_cloud_service.crop_adaptive(point_cloud, adaptive_bounds)  # Stores the 3D points captured by the camera.

        if len(point_cloud.points) == 0:  # Checks if there are no items to work with.
            print(f"WARNING: Empty point cloud after adaptive crop at {label}.")  # Shows a message in the console.
            return None  # Gives this result back to the part of the code that called it.

        self.point_cloud_service.print_cloud_bounds(  # Shows the size and position information for this point cloud.
            f"Cropped camera-frame scan - {label}",  # Adds one item to the multi-line value.
            point_cloud,  # Adds one item to the multi-line value.
        )  # Closes the multi-line code started above.

        point_cloud.transform(T_base_camera_actual)  # Moves the point cloud or matrix into another coordinate space.
        clean_scan = self.point_cloud_service.clean(point_cloud)  # Stores the cleaned scan after noise is removed.

        if len(clean_scan.points) == 0:  # Checks if there are no items to work with.
            print(f"WARNING: Point cloud empty after cleaning at {label}.")  # Shows a message in the console.
            return None  # Gives this result back to the part of the code that called it.

        self.point_cloud_service.save_debug_scan(label, clean_scan)  # Saves this scan separately for checking later.

        if self.config.SHOW_DEBUG_EACH_SCAN:  # Checks a condition before running the next indented lines.
            o3d.visualization.draw_geometries(  # Opens a 3D window to show the point cloud.
                [clean_scan],  # Adds one item to the multi-line value.
                window_name=f"Debug transformed scan - {label}",  # Stores window name for use in the next steps.
            )  # Closes the multi-line code started above.

        return clean_scan  # Gives this result back to the part of the code that called it.

    def run(self):  # Runs the full scanning process from start to finish.
        self.config.OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)  # Makes the folder if it does not exist yet.

        self.robot_controller = RobotController.create_from_user_selection(self.config)  # Saves robot controller inside this object so other methods can use it.
        self.robot_controller.connect()  # Runs this line as one small step in the program.

        T_tcp_mount = xyzrxryrz_to_numpy(self.config.TCP_TO_CAMERA_MOUNT)  # Stores the transform from the robot tool point to the camera mount.
        T_mount_optical = xyzrxryrz_to_numpy(self.config.CAMERA_MOUNT_TO_OPTICAL)  # Stores the transform from the camera mount to the RealSense optical frame.
        T_tcp_camera = T_tcp_mount @ T_mount_optical  # Stores the transform from the robot tool point to the camera.
        T_camera_tcp = np.linalg.inv(T_tcp_camera)  # Stores the reverse transform from the camera back to the robot tool point.

        print_transform("T_tcp_camera", T_tcp_camera)  # Moves the point cloud or matrix into another coordinate space.

        try:  # Tries the next steps because they might fail.
            self.camera.start()  # Runs this line as one small step in the program.
            self._run_scan_sequence(T_tcp_camera, T_camera_tcp)  # Runs this line as one small step in the program.

        except KeyboardInterrupt:  # Runs this part when the user stops the scan with the keyboard.
            print("\nScanning interrupted by user.")  # Shows a message in the console.

        finally:  # Runs the cleanup steps no matter what happened before.
            self.camera.stop()  # Runs this line as one small step in the program.
            cv2.destroyAllWindows()  # Closes all OpenCV windows.

            try:  # Tries the next steps because they might fail.
                self.robot_controller.move_to_joints(  # Moves the robot using joint angles.
                    self.config.HOME_JOINTS,  # Adds one item to the multi-line value.
                    "Home_End",  # Adds one item to the multi-line value.
                )  # Closes the multi-line code started above.
            except Exception as error:  # Runs this part if an error happens and saves the error message.
                print("Could not move robot back to home position:", error)  # Shows a message in the console.

        self._finish_and_save_result()  # Runs this line as one small step in the program.

    def _run_scan_sequence(self, T_tcp_camera, T_camera_tcp):  # Runs the main scan steps after setup is ready.
        print("\n" + "=" * 70)  # Shows a message in the console.
        print("AUTO-CENTERED ADAPTIVE INSIDE-BOX SCANNING STARTED")  # Shows a message in the console.
        print("=" * 70)  # Shows a message in the console.
        print("Step 1: Center the camera on the open box.")  # Shows a message in the console.
        print("Step 2: Capture the reference scan from the centered pose.")  # Shows a message in the console.
        print("Step 3: Generate adaptive scan poses.")  # Shows a message in the console.
        print("Step 4: Capture and merge all scans.")  # Shows a message in the console.
        print("=" * 70)  # Shows a message in the console.

        if self.config.AUTO_CENTER_BEFORE_SCAN:  # Checks a condition before running the next indented lines.
            auto_centering_service = AutoCenteringService(  # Stores auto centering service for use in the next steps.
                self.config,  # Adds one item to the multi-line value.
                self.robot_controller,  # Adds one item to the multi-line value.
                self.camera,  # Adds one item to the multi-line value.
                self.detector,  # Adds one item to the multi-line value.
                T_tcp_camera,  # Adds one item to the multi-line value.
                T_camera_tcp,  # Adds one item to the multi-line value.
            )  # Closes the multi-line code started above.
            center_actual_joints = auto_centering_service.run()  # Stores the joint angles after the camera is centered.
        else:  # Runs this part when the earlier condition was not true.
            center_actual_joints = self.robot_controller.move_to_joints(  # Stores the joint angles after the camera is centered.
                self.config.CENTER_REFERENCE_JOINTS,  # Adds one item to the multi-line value.
                "Cabinet_Center_Reference",  # Adds one item to the multi-line value.
            )  # Closes the multi-line code started above.

        T_base_tcp_center = robodk_mat_to_numpy(  # Stores the center tool pose in the robot base frame.
            self.robot_controller.robot.SolveFK(center_actual_joints)  # Calculates the robot tool pose from joint angles.
        )  # Closes the multi-line code started above.
        T_base_camera_center = T_base_tcp_center @ T_tcp_camera  # Stores the center camera pose in the robot base frame.

        print_transform("T_base_tcp_center", T_base_tcp_center)  # Moves the point cloud or matrix into another coordinate space.
        print_transform("T_base_camera_center", T_base_camera_center)  # Moves the point cloud or matrix into another coordinate space.

        adaptive_bounds = self._capture_reference_scan(T_base_camera_center)  # Stores the estimated size and position of the cabinet in camera space.
        generated_camera_poses = self.pose_generator.generate_scan_camera_poses_from_center(  # Stores all camera positions the robot should scan from.
            T_base_camera_center,  # Adds one item to the multi-line value.
            adaptive_bounds,  # Adds one item to the multi-line value.
        )  # Closes the multi-line code started above.

        self._capture_generated_poses(  # Runs this line as one small step in the program.
            generated_camera_poses,  # Adds one item to the multi-line value.
            T_camera_tcp,  # Adds one item to the multi-line value.
            T_tcp_camera,  # Adds one item to the multi-line value.
            adaptive_bounds,  # Adds one item to the multi-line value.
        )  # Closes the multi-line code started above.

    def _capture_reference_scan(self, T_base_camera_center):  # Captures the first scan and uses it as the reference.
        reference_cloud = self.camera.capture_stable_pointcloud(  # Stores the first scan used to understand the cabinet size.
            self.config.CAPTURE_FRAMES_PER_POSITION,  # Adds one item to the multi-line value.
        )  # Closes the multi-line code started above.

        if reference_cloud is None:  # Checks if this value is missing.
            raise Exception("Reference scan failed. No point cloud was captured.")  # Stops the program because something important went wrong.

        self.point_cloud_service.print_cloud_bounds(  # Shows the size and position information for this point cloud.
            "Reference raw camera-frame scan",  # Adds one item to the multi-line value.
            reference_cloud,  # Adds one item to the multi-line value.
        )  # Closes the multi-line code started above.
        adaptive_bounds = self.point_cloud_service.estimate_camera_cloud_bounds(reference_cloud)  # Stores the estimated size and position of the cabinet in camera space.

        reference_cloud_cropped = self.point_cloud_service.crop_adaptive(  # Stores only the useful part of the reference scan.
            reference_cloud,  # Adds one item to the multi-line value.
            adaptive_bounds,  # Adds one item to the multi-line value.
        )  # Closes the multi-line code started above.

        reference_cloud_cropped.transform(T_base_camera_center)  # Moves the point cloud or matrix into another coordinate space.
        reference_clean_scan = self.point_cloud_service.clean(reference_cloud_cropped)  # Stores the cleaned reference scan.

        if len(reference_clean_scan.points) > 0:  # Checks a condition before running the next indented lines.
            self.point_cloud_service.save_debug_scan("Reference_Center", reference_clean_scan)  # Saves this scan separately for checking later.
            self.combined_point_cloud += reference_clean_scan  # Runs this line as one small step in the program.
            self.successful_scans += 1  # Runs this line as one small step in the program.
            print(  # Shows a message in the console.
                f"Accepted scan {self.successful_scans}: Reference_Center "  # Runs this line as one small step in the program.
                f"with {len(reference_clean_scan.points):,} cleaned points"  # Counts how many items there are.
            )  # Closes the multi-line code started above.
        else:  # Runs this part when the earlier condition was not true.
            print("WARNING: Reference scan became empty after cleaning.")  # Shows a message in the console.
            self.skipped_scans += 1  # Runs this line as one small step in the program.

        return adaptive_bounds  # Gives this result back to the part of the code that called it.

    def _capture_generated_poses(self, generated_camera_poses, T_camera_tcp, T_tcp_camera, adaptive_bounds):  # Moves to each generated pose and captures a scan.
        for label, T_base_camera_target in generated_camera_poses:  # Repeats the next indented lines for each item.
            if label == "Reference_Center":  # Checks a condition before running the next indented lines.
                continue  # Skips the rest of this loop and starts the next loop round.

            T_base_tcp_target = T_base_camera_target @ T_camera_tcp  # Stores where the robot tool should move to place the camera there.

            if not self.robot_controller.is_generated_pose_safe(  # Checks if this condition is not true.
                T_base_tcp_target,  # Adds one item to the multi-line value.
                T_base_camera_target,  # Adds one item to the multi-line value.
                label,  # Adds one item to the multi-line value.
            ):  # Closes the multi-line code started above.
                self.unsafe_scans += 1  # Runs this line as one small step in the program.
                self.skipped_scans += 1  # Runs this line as one small step in the program.
                continue  # Skips the rest of this loop and starts the next loop round.

            try:  # Tries the next steps because they might fail.
                actual_joints = self.robot_controller.move_to_pose(  # Stores the real joint angles read from the robot.
                    T_base_tcp_target,  # Adds one item to the multi-line value.
                    label,  # Adds one item to the multi-line value.
                )  # Closes the multi-line code started above.
            except Exception as error:  # Runs this part if an error happens and saves the error message.
                print("")  # Shows a message in the console.
                print(f"WARNING: Could not move to generated pose {label}.")  # Shows a message in the console.
                print("Move error:", error)  # Shows a message in the console.
                self.failed_moves += 1  # Runs this line as one small step in the program.
                self.skipped_scans += 1  # Runs this line as one small step in the program.
                continue  # Skips the rest of this loop and starts the next loop round.

            T_base_tcp_actual = robodk_mat_to_numpy(  # Stores where the robot tool really is after the robot moves.
                self.robot_controller.robot.SolveFK(actual_joints)  # Calculates the robot tool pose from joint angles.
            )  # Closes the multi-line code started above.
            T_base_camera_actual = T_base_tcp_actual @ T_tcp_camera  # Stores where the camera really is after the robot moves.

            print_transform(f"T_base_tcp_actual_{label}", T_base_tcp_actual)  # Moves the point cloud or matrix into another coordinate space.
            print_transform(f"T_base_camera_actual_{label}", T_base_camera_actual)  # Moves the point cloud or matrix into another coordinate space.

            clean_scan = self.scan_current_position(  # Stores the cleaned scan after noise is removed.
                label,  # Adds one item to the multi-line value.
                T_base_camera_actual,  # Adds one item to the multi-line value.
                adaptive_bounds,  # Adds one item to the multi-line value.
            )  # Closes the multi-line code started above.

            if clean_scan is None:  # Checks if this value is missing.
                self.skipped_scans += 1  # Runs this line as one small step in the program.
                continue  # Skips the rest of this loop and starts the next loop round.

            self.combined_point_cloud += clean_scan  # Runs this line as one small step in the program.
            self.successful_scans += 1  # Runs this line as one small step in the program.

            print(  # Shows a message in the console.
                f"Accepted scan {self.successful_scans}: {label} "  # Runs this line as one small step in the program.
                f"with {len(clean_scan.points):,} cleaned points"  # Counts how many items there are.
            )  # Closes the multi-line code started above.

    def _finish_and_save_result(self):  # Cleans, saves, and shows the final merged scan.
        print("\n" + "=" * 70)  # Shows a message in the console.
        print("SCAN SUMMARY")  # Shows a message in the console.
        print("=" * 70)  # Shows a message in the console.
        print("Successful scans:", self.successful_scans)  # Shows a message in the console.
        print("Skipped scans:", self.skipped_scans)  # Shows a message in the console.
        print("Unsafe skipped scans:", self.unsafe_scans)  # Shows a message in the console.
        print("Failed robot moves:", self.failed_moves)  # Shows a message in the console.
        print("Total merged points before final cleanup:", len(self.combined_point_cloud.points))  # Shows a message in the console.
        self.point_cloud_service.print_cloud_bounds(  # Shows the size and position information for this point cloud.
            "Combined point cloud before final cleanup",  # Adds one item to the multi-line value.
            self.combined_point_cloud,  # Adds one item to the multi-line value.
        )  # Closes the multi-line code started above.

        if len(self.combined_point_cloud.points) == 0:  # Checks if there are no items to work with.
            raise Exception("No valid point cloud was captured. Combined cloud is empty.")  # Stops the program because something important went wrong.

        self.combined_point_cloud = self.point_cloud_service.clean(self.combined_point_cloud)  # Stores all accepted scans merged together.
        self.combined_point_cloud = self.point_cloud_service.estimate_normals(self.combined_point_cloud)  # Stores all accepted scans merged together.

        print("Total merged points after final cleanup:", len(self.combined_point_cloud.points))  # Shows a message in the console.
        self.point_cloud_service.print_cloud_bounds(  # Shows the size and position information for this point cloud.
            "Combined point cloud after final cleanup",  # Adds one item to the multi-line value.
            self.combined_point_cloud,  # Adds one item to the multi-line value.
        )  # Closes the multi-line code started above.

        o3d.io.write_point_cloud(str(self.config.OUTPUT_CLEAN_FILE), self.combined_point_cloud)  # Saves the point cloud to a file.
        print("Saved final merged point cloud to:", self.config.OUTPUT_CLEAN_FILE)  # Shows a message in the console.

        if self.config.SHOW_FINAL_CLOUD:  # Checks a condition before running the next indented lines.
            o3d.visualization.draw_geometries(  # Opens a 3D window to show the point cloud.
                [self.combined_point_cloud],  # Adds one item to the multi-line value.
                window_name=f"Adaptive Inside Box Point Cloud - {self.successful_scans} scans",  # Stores window name for use in the next steps.
            )  # Closes the multi-line code started above.

        print("Done.")  # Shows a message in the console.
