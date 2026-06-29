import cv2
import numpy as np
import open3d as o3d

from auto_box_detector import AutoBoxDetector
from auto_centering_service import AutoCenteringService
from point_cloud_service import PointCloudService
from pose_generator import AdaptivePoseGenerator
from realsense_camera import RealSenseCamera
from robot_controller import RobotController
from transform_utils import print_transform, robodk_mat_to_numpy, xyzrxryrz_to_numpy


class AdaptiveInsideBoxScanner:
    def __init__(self, config):
        self.config = config
        self.robot_controller = None
        self.camera = RealSenseCamera(config)
        self.point_cloud_service = PointCloudService(config)
        self.pose_generator = AdaptivePoseGenerator(config)
        self.detector = AutoBoxDetector(config)

        self.combined_point_cloud = o3d.geometry.PointCloud()
        self.successful_scans = 0
        self.skipped_scans = 0
        self.unsafe_scans = 0
        self.failed_moves = 0

    def scan_current_position(self, label, T_base_camera_actual, adaptive_bounds=None):
        point_cloud = self.camera.capture_stable_pointcloud(
            self.config.CAPTURE_FRAMES_PER_POSITION,
        )

        if point_cloud is None:
            print(f"WARNING: Empty point cloud at {label}.")
            return None

        print(f"Captured raw camera points at {label}: {len(point_cloud.points):,}")
        self.point_cloud_service.print_cloud_bounds(
            f"Raw camera-frame scan - {label}",
            point_cloud,
        )

        if adaptive_bounds is not None:
            point_cloud = self.point_cloud_service.crop_adaptive(point_cloud, adaptive_bounds)

        if len(point_cloud.points) == 0:
            print(f"WARNING: Empty point cloud after adaptive crop at {label}.")
            return None

        self.point_cloud_service.print_cloud_bounds(
            f"Cropped camera-frame scan - {label}",
            point_cloud,
        )

        point_cloud.transform(T_base_camera_actual)
        clean_scan = self.point_cloud_service.clean(point_cloud)

        if len(clean_scan.points) == 0:
            print(f"WARNING: Point cloud empty after cleaning at {label}.")
            return None

        self.point_cloud_service.save_debug_scan(label, clean_scan)

        if self.config.SHOW_DEBUG_EACH_SCAN:
            o3d.visualization.draw_geometries(
                [clean_scan],
                window_name=f"Debug transformed scan - {label}",
            )

        return clean_scan

    def run(self):
        self.config.OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

        self.robot_controller = RobotController.create_from_user_selection(self.config)
        self.robot_controller.connect()

        T_tcp_mount = xyzrxryrz_to_numpy(self.config.TCP_TO_CAMERA_MOUNT)
        T_mount_optical = xyzrxryrz_to_numpy(self.config.CAMERA_MOUNT_TO_OPTICAL)
        T_tcp_camera = T_tcp_mount @ T_mount_optical
        T_camera_tcp = np.linalg.inv(T_tcp_camera)

        print_transform("T_tcp_camera", T_tcp_camera)

        try:
            self.camera.start()
            self._run_scan_sequence(T_tcp_camera, T_camera_tcp)

        except KeyboardInterrupt:
            print("\nScanning interrupted by user.")

        finally:
            self.camera.stop()
            cv2.destroyAllWindows()

            try:
                self.robot_controller.move_to_joints(
                    self.config.HOME_JOINTS,
                    "Home_End",
                )
            except Exception as error:
                print("Could not move robot back to home position:", error)

        self._finish_and_save_result()

    def _run_scan_sequence(self, T_tcp_camera, T_camera_tcp):
        print("\n" + "=" * 70)
        print("AUTO-CENTERED ADAPTIVE INSIDE-BOX SCANNING STARTED")
        print("=" * 70)
        print("Step 1: Center the camera on the open box.")
        print("Step 2: Capture the reference scan from the centered pose.")
        print("Step 3: Generate adaptive scan poses.")
        print("Step 4: Capture and merge all scans.")
        print("=" * 70)

        if self.config.AUTO_CENTER_BEFORE_SCAN:
            auto_centering_service = AutoCenteringService(
                self.config,
                self.robot_controller,
                self.camera,
                self.detector,
                T_tcp_camera,
                T_camera_tcp,
            )
            center_actual_joints = auto_centering_service.run()
        else:
            center_actual_joints = self.robot_controller.move_to_joints(
                self.config.CENTER_REFERENCE_JOINTS,
                "Cabinet_Center_Reference",
            )

        T_base_tcp_center = robodk_mat_to_numpy(
            self.robot_controller.robot.SolveFK(center_actual_joints)
        )
        T_base_camera_center = T_base_tcp_center @ T_tcp_camera

        print_transform("T_base_tcp_center", T_base_tcp_center)
        print_transform("T_base_camera_center", T_base_camera_center)

        adaptive_bounds = self._capture_reference_scan(T_base_camera_center)
        generated_camera_poses = self.pose_generator.generate_scan_camera_poses_from_center(
            T_base_camera_center,
            adaptive_bounds,
        )

        self._capture_generated_poses(
            generated_camera_poses,
            T_camera_tcp,
            T_tcp_camera,
            adaptive_bounds,
        )

    def _capture_reference_scan(self, T_base_camera_center):
        reference_cloud = self.camera.capture_stable_pointcloud(
            self.config.CAPTURE_FRAMES_PER_POSITION,
        )

        if reference_cloud is None:
            raise Exception("Reference scan failed. No point cloud was captured.")

        self.point_cloud_service.print_cloud_bounds(
            "Reference raw camera-frame scan",
            reference_cloud,
        )
        adaptive_bounds = self.point_cloud_service.estimate_camera_cloud_bounds(reference_cloud)

        reference_cloud_cropped = self.point_cloud_service.crop_adaptive(
            reference_cloud,
            adaptive_bounds,
        )

        reference_cloud_cropped.transform(T_base_camera_center)
        reference_clean_scan = self.point_cloud_service.clean(reference_cloud_cropped)

        if len(reference_clean_scan.points) > 0:
            self.point_cloud_service.save_debug_scan("Reference_Center", reference_clean_scan)
            self.combined_point_cloud += reference_clean_scan
            self.successful_scans += 1
            print(
                f"Accepted scan {self.successful_scans}: Reference_Center "
                f"with {len(reference_clean_scan.points):,} cleaned points"
            )
        else:
            print("WARNING: Reference scan became empty after cleaning.")
            self.skipped_scans += 1

        return adaptive_bounds

    def _capture_generated_poses(self, generated_camera_poses, T_camera_tcp, T_tcp_camera, adaptive_bounds):
        for label, T_base_camera_target in generated_camera_poses:
            if label == "Reference_Center":
                continue

            T_base_tcp_target = T_base_camera_target @ T_camera_tcp

            if not self.robot_controller.is_generated_pose_safe(
                T_base_tcp_target,
                T_base_camera_target,
                label,
            ):
                self.unsafe_scans += 1
                self.skipped_scans += 1
                continue

            try:
                actual_joints = self.robot_controller.move_to_pose(
                    T_base_tcp_target,
                    label,
                )
            except Exception as error:
                print("")
                print(f"WARNING: Could not move to generated pose {label}.")
                print("Move error:", error)
                self.failed_moves += 1
                self.skipped_scans += 1
                continue

            T_base_tcp_actual = robodk_mat_to_numpy(
                self.robot_controller.robot.SolveFK(actual_joints)
            )
            T_base_camera_actual = T_base_tcp_actual @ T_tcp_camera

            print_transform(f"T_base_tcp_actual_{label}", T_base_tcp_actual)
            print_transform(f"T_base_camera_actual_{label}", T_base_camera_actual)

            clean_scan = self.scan_current_position(
                label,
                T_base_camera_actual,
                adaptive_bounds,
            )

            if clean_scan is None:
                self.skipped_scans += 1
                continue

            self.combined_point_cloud += clean_scan
            self.successful_scans += 1

            print(
                f"Accepted scan {self.successful_scans}: {label} "
                f"with {len(clean_scan.points):,} cleaned points"
            )

    def _finish_and_save_result(self):
        print("\n" + "=" * 70)
        print("SCAN SUMMARY")
        print("=" * 70)
        print("Successful scans:", self.successful_scans)
        print("Skipped scans:", self.skipped_scans)
        print("Unsafe skipped scans:", self.unsafe_scans)
        print("Failed robot moves:", self.failed_moves)
        print("Total merged points before final cleanup:", len(self.combined_point_cloud.points))
        self.point_cloud_service.print_cloud_bounds(
            "Combined point cloud before final cleanup",
            self.combined_point_cloud,
        )

        if len(self.combined_point_cloud.points) == 0:
            raise Exception("No valid point cloud was captured. Combined cloud is empty.")

        self.combined_point_cloud = self.point_cloud_service.clean(self.combined_point_cloud)
        self.combined_point_cloud = self.point_cloud_service.estimate_normals(self.combined_point_cloud)

        print("Total merged points after final cleanup:", len(self.combined_point_cloud.points))
        self.point_cloud_service.print_cloud_bounds(
            "Combined point cloud after final cleanup",
            self.combined_point_cloud,
        )

        o3d.io.write_point_cloud(str(self.config.OUTPUT_CLEAN_FILE), self.combined_point_cloud)
        print("Saved final merged point cloud to:", self.config.OUTPUT_CLEAN_FILE)

        if self.config.SHOW_FINAL_CLOUD:
            o3d.visualization.draw_geometries(
                [self.combined_point_cloud],
                window_name=f"Adaptive Inside Box Point Cloud - {self.successful_scans} scans",
            )

        print("Done.")
