import time

import cv2
import numpy as np

from transform_utils import make_local_offset_transform, robodk_mat_to_numpy


class AutoCenteringService:
    def __init__(self, config, robot_controller, camera, detector, T_tcp_camera, T_camera_tcp):
        self.config = config
        self.robot_controller = robot_controller
        self.camera = camera
        self.detector = detector
        self.T_tcp_camera = T_tcp_camera
        self.T_camera_tcp = T_camera_tcp

    def move_camera_one_step_to_box_center(self, point_camera):
        actual_joints = self.robot_controller.get_joints_when_ready()

        T_base_tcp_current = robodk_mat_to_numpy(
            self.robot_controller.robot.SolveFK(actual_joints)
        )
        T_base_camera_current = T_base_tcp_current @ self.T_tcp_camera

        camera_offset = self.detector.calculate_camera_correction(point_camera)

        T_camera_offset = make_local_offset_transform(
            camera_offset[0],
            camera_offset[1],
            camera_offset[2],
        )

        T_base_camera_target = T_base_camera_current @ T_camera_offset
        T_base_tcp_target = T_base_camera_target @ self.T_camera_tcp

        print("")
        print("Automatic box-centering movement")
        print("3D box point in camera frame:", np.round(point_camera, 4), "m")
        print("Camera movement step:", np.round(camera_offset, 4), "m")
        print("Current robot joints:", [round(joint, 2) for joint in actual_joints])

        if not self.robot_controller.is_generated_pose_safe(
            T_base_tcp_target,
            T_base_camera_target,
            "Auto_Box_Center_Step",
        ):
            return None

        try:
            return self.robot_controller.move_to_pose(
                T_base_tcp_target,
                "Auto_Box_Center_Step",
            )
        except Exception as error:
            print("")
            print("Could not move robot to automatic box center step.")
            print("Move error:", error)
            return None

    def should_move(self, box, stable_frame_count, last_auto_move_time, failed_auto_moves, total_auto_moves):
        if box is None:
            return False

        if self.detector.is_box_centered(box):
            return False

        if stable_frame_count < self.config.AUTO_REQUIRED_STABLE_FRAMES:
            return False

        if time.time() - last_auto_move_time < self.config.AUTO_MOVE_COOLDOWN_SECONDS:
            return False

        if failed_auto_moves >= self.config.AUTO_MAX_FAILED_MOVES:
            return False

        if total_auto_moves >= self.config.AUTO_MAX_TOTAL_MOVES:
            return False

        return True

    def run(self):
        previous_box = None
        stable_frame_count = 0
        failed_auto_moves = 0
        total_auto_moves = 0
        last_auto_move_time = 0.0
        start_time = time.time()
        last_print_time = 0.0

        print("")
        print("=" * 70)
        print("AUTO CENTERING STARTED")
        print("=" * 70)
        print("The robot will center the camera on the detected open box.")
        print("When centered, the code will continue with the reference capture.")
        print("Press S to skip centering and start the scan from the current pose.")
        print("=" * 70)

        while True:
            if time.time() - start_time > self.config.AUTO_CENTER_TIMEOUT_SECONDS:
                self.detector.close_windows()
                raise Exception("Auto centering timed out before the box was centered.")

            depth_frame, color_image_rgb, depth_image = self.camera.get_aligned_frame()

            if depth_frame is None:
                continue

            color_image_bgr = cv2.cvtColor(color_image_rgb, cv2.COLOR_RGB2BGR)
            box, mask = self.detector.detect_box(depth_image, self.camera.depth_scale)

            stable_frame_count, previous_box = self.detector.update_stability(
                box,
                previous_box,
                stable_frame_count,
            )

            self.detector.draw_center_screen(
                color_image_bgr,
                box,
                stable_frame_count,
                failed_auto_moves,
                total_auto_moves,
            )

            if box is not None and time.time() - last_print_time > 0.5:
                offset_x, offset_y = self.detector.get_box_offset_pixels(box)
                print(
                    "Auto box:",
                    f"center=({box['center_x']}, {box['center_y']}),",
                    f"offset=({offset_x}, {offset_y}),",
                    f"distance={box['distance_meters']:.2f}m,",
                    f"stable={stable_frame_count}/{self.config.AUTO_REQUIRED_STABLE_FRAMES}",
                )
                last_print_time = time.time()

            if mask is not None:
                cv2.imshow(self.config.AUTO_MASK_WINDOW_NAME, mask)

            cv2.imshow(self.config.AUTO_WINDOW_NAME, color_image_bgr)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q") or key == 27:
                self.detector.close_windows()
                raise KeyboardInterrupt

            if key == ord("s"):
                print("")
                print("Manual skip selected. Starting scan from current robot pose.")
                self.detector.close_windows()
                return self.robot_controller.get_joints_when_ready()

            if key == ord("h"):
                failed_auto_moves = 0
                total_auto_moves = 0
                stable_frame_count = 0
                previous_box = None
                self.robot_controller.move_to_joints(
                    self.config.HOME_JOINTS,
                    "Home_From_Auto_Center",
                )

            if key == ord("c"):
                failed_auto_moves = 0
                total_auto_moves = 0
                stable_frame_count = 0
                previous_box = None
                self.robot_controller.move_to_joints(
                    self.config.CENTER_REFERENCE_JOINTS,
                    "Center_Reference_From_Auto_Center",
                )

            if box is not None and self.detector.is_box_centered(box):
                if stable_frame_count >= self.config.AUTO_REQUIRED_STABLE_FRAMES:
                    print("")
                    print("=" * 70)
                    print("AUTO CENTERING FINISHED")
                    print("=" * 70)
                    print("The camera is centered on the box.")
                    print("Continuing with reference point cloud capture.")
                    print("=" * 70)
                    self.detector.close_windows()
                    return self.robot_controller.get_joints_when_ready()

            if self.should_move(
                box,
                stable_frame_count,
                last_auto_move_time,
                failed_auto_moves,
                total_auto_moves,
            ):
                point_camera = self.detector.get_box_center_3d(depth_frame, box)

                if point_camera is None:
                    print("Auto move skipped. No valid 3D box center.")
                    failed_auto_moves += 1
                else:
                    actual_joints = self.move_camera_one_step_to_box_center(point_camera)

                    if actual_joints is None:
                        failed_auto_moves += 1
                    else:
                        failed_auto_moves = 0
                        total_auto_moves += 1

                stable_frame_count = 0
                previous_box = None
                last_auto_move_time = time.time()

            if failed_auto_moves >= self.config.AUTO_MAX_FAILED_MOVES:
                self.detector.close_windows()
                raise Exception("Auto centering stopped because too many robot moves failed.")

            if total_auto_moves >= self.config.AUTO_MAX_TOTAL_MOVES:
                self.detector.close_windows()
                raise Exception("Auto centering stopped because the maximum move count was reached.")
