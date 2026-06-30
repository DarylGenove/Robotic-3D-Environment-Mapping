import time  # Loads time so the code can wait and measure seconds.

import cv2  # Loads OpenCV so the code can work with camera images.
import numpy as np  # Loads NumPy as np so the code can do fast number and matrix math.

from transform_utils import make_local_offset_transform, robodk_mat_to_numpy  # Gets make_local_offset_transform, robodk_mat_to_numpy from transform_utils so this file can use it.


class AutoCenteringService:  # Makes a toolbox that moves the robot until the camera is centered on the box.
    def __init__(self, config, robot_controller, camera, detector, T_tcp_camera, T_camera_tcp):  # Makes a function named   init  .
        self.config = config  # Stores the scanner settings so the program can use them.
        self.robot_controller = robot_controller  # Saves robot controller inside this object so other methods can use it.
        self.camera = camera  # Saves camera inside this object so other methods can use it.
        self.detector = detector  # Saves detector inside this object so other methods can use it.
        self.T_tcp_camera = T_tcp_camera  # Stores the transform from the robot tool point to the camera.
        self.T_camera_tcp = T_camera_tcp  # Stores the reverse transform from the camera back to the robot tool point.

    def move_camera_one_step_to_box_center(self, point_camera):  # Moves the camera one small step toward the detected box center.
        actual_joints = self.robot_controller.get_joints_when_ready()  # Stores the real joint angles read from the robot.

        T_base_tcp_current = robodk_mat_to_numpy(  # Stores T base tcp current for use in the next steps.
            self.robot_controller.robot.SolveFK(actual_joints)  # Calculates the robot tool pose from joint angles.
        )  # Closes the multi-line code started above.
        T_base_camera_current = T_base_tcp_current @ self.T_tcp_camera  # Stores T base camera current for use in the next steps.

        camera_offset = self.detector.calculate_camera_correction(point_camera)  # Stores how far the camera should move to center the box.

        T_camera_offset = make_local_offset_transform(  # Stores a small camera movement from the current camera position.
            camera_offset[0],  # Adds one item to the multi-line value.
            camera_offset[1],  # Adds one item to the multi-line value.
            camera_offset[2],  # Adds one item to the multi-line value.
        )  # Closes the multi-line code started above.

        T_base_camera_target = T_base_camera_current @ T_camera_offset  # Stores where the camera should move next.
        T_base_tcp_target = T_base_camera_target @ self.T_camera_tcp  # Stores where the robot tool should move to place the camera there.

        print("")  # Shows a message in the console.
        print("Automatic box-centering movement")  # Shows a message in the console.
        print("3D box point in camera frame:", np.round(point_camera, 4), "m")  # Shows a message in the console.
        print("Camera movement step:", np.round(camera_offset, 4), "m")  # Shows a message in the console.
        print("Current robot joints:", [round(joint, 2) for joint in actual_joints])  # Shows a message in the console.

        if not self.robot_controller.is_generated_pose_safe(  # Checks if this condition is not true.
            T_base_tcp_target,  # Adds one item to the multi-line value.
            T_base_camera_target,  # Adds one item to the multi-line value.
            "Auto_Box_Center_Step",  # Adds one item to the multi-line value.
        ):  # Closes the multi-line code started above.
            return None  # Gives this result back to the part of the code that called it.

        try:  # Tries the next steps because they might fail.
            return self.robot_controller.move_to_pose(  # Gives this result back to the part of the code that called it.
                T_base_tcp_target,  # Adds one item to the multi-line value.
                "Auto_Box_Center_Step",  # Adds one item to the multi-line value.
            )  # Closes the multi-line code started above.
        except Exception as error:  # Runs this part if an error happens and saves the error message.
            print("")  # Shows a message in the console.
            print("Could not move robot to automatic box center step.")  # Shows a message in the console.
            print("Move error:", error)  # Shows a message in the console.
            return None  # Gives this result back to the part of the code that called it.

    def should_move(self, box, stable_frame_count, last_auto_move_time, failed_auto_moves, total_auto_moves):  # Checks if auto-centering is allowed to move now.
        if box is None:  # Checks if this value is missing.
            return False  # Gives this result back to the part of the code that called it.

        if self.detector.is_box_centered(box):  # Checks a condition before running the next indented lines.
            return False  # Gives this result back to the part of the code that called it.

        if stable_frame_count < self.config.AUTO_REQUIRED_STABLE_FRAMES:  # Checks a condition before running the next indented lines.
            return False  # Gives this result back to the part of the code that called it.

        if time.time() - last_auto_move_time < self.config.AUTO_MOVE_COOLDOWN_SECONDS:  # Checks a condition before running the next indented lines.
            return False  # Gives this result back to the part of the code that called it.

        if failed_auto_moves >= self.config.AUTO_MAX_FAILED_MOVES:  # Checks a condition before running the next indented lines.
            return False  # Gives this result back to the part of the code that called it.

        if total_auto_moves >= self.config.AUTO_MAX_TOTAL_MOVES:  # Checks a condition before running the next indented lines.
            return False  # Gives this result back to the part of the code that called it.

        return True  # Gives this result back to the part of the code that called it.

    def run(self):  # Runs the full scanning process from start to finish.
        previous_box = None  # Stores the box from the previous frame.
        stable_frame_count = 0  # Counts how many frames the box stayed still.
        failed_auto_moves = 0  # Counts automatic moves that failed.
        total_auto_moves = 0  # Counts all automatic moves already made.
        last_auto_move_time = 0.0  # Stores the time of the last automatic move.
        start_time = time.time()  # Stores when auto-centering started.
        last_print_time = 0.0  # Stores when the last status message was printed.

        print("")  # Shows a message in the console.
        print("=" * 70)  # Shows a message in the console.
        print("AUTO CENTERING STARTED")  # Shows a message in the console.
        print("=" * 70)  # Shows a message in the console.
        print("The robot will center the camera on the detected open box.")  # Shows a message in the console.
        print("When centered, the code will continue with the reference capture.")  # Shows a message in the console.
        print("Press S to skip centering and start the scan from the current pose.")  # Shows a message in the console.
        print("=" * 70)  # Shows a message in the console.

        while True:  # Keeps repeating until the code returns, breaks, or raises an error.
            if time.time() - start_time > self.config.AUTO_CENTER_TIMEOUT_SECONDS:  # Checks a condition before running the next indented lines.
                self.detector.close_windows()  # Runs this line as one small step in the program.
                raise Exception("Auto centering timed out before the box was centered.")  # Stops the program because something important went wrong.

            depth_frame, color_image_rgb, depth_image = self.camera.get_aligned_frame()  # Runs this line as one small step in the program.

            if depth_frame is None:  # Checks if this value is missing.
                continue  # Skips the rest of this loop and starts the next loop round.

            color_image_bgr = cv2.cvtColor(color_image_rgb, cv2.COLOR_RGB2BGR)  # Stores the color image in OpenCV color order.
            box, mask = self.detector.detect_box(depth_image, self.camera.depth_scale)  # Runs this line as one small step in the program.

            stable_frame_count, previous_box = self.detector.update_stability(  # Runs this line as one small step in the program.
                box,  # Adds one item to the multi-line value.
                previous_box,  # Adds one item to the multi-line value.
                stable_frame_count,  # Adds one item to the multi-line value.
            )  # Closes the multi-line code started above.

            self.detector.draw_center_screen(  # Runs this line as one small step in the program.
                color_image_bgr,  # Adds one item to the multi-line value.
                box,  # Adds one item to the multi-line value.
                stable_frame_count,  # Adds one item to the multi-line value.
                failed_auto_moves,  # Adds one item to the multi-line value.
                total_auto_moves,  # Adds one item to the multi-line value.
            )  # Closes the multi-line code started above.

            if box is not None and time.time() - last_print_time > 0.5:  # Checks if this value exists before using it.
                offset_x, offset_y = self.detector.get_box_offset_pixels(box)  # Runs this line as one small step in the program.
                print(  # Shows a message in the console.
                    "Auto box:",  # Adds one named value to the dictionary.
                    f"center=({box['center_x']}, {box['center_y']}),",  # Adds one item to the multi-line value.
                    f"offset=({offset_x}, {offset_y}),",  # Adds one item to the multi-line value.
                    f"distance={box['distance_meters']:.2f}m,",  # Adds one named value to the dictionary.
                    f"stable={stable_frame_count}/{self.config.AUTO_REQUIRED_STABLE_FRAMES}",  # Adds one item to the multi-line value.
                )  # Closes the multi-line code started above.
                last_print_time = time.time()  # Stores when the last status message was printed.

            if mask is not None:  # Checks if this value exists before using it.
                cv2.imshow(self.config.AUTO_MASK_WINDOW_NAME, mask)  # Shows an image window on the screen.

            cv2.imshow(self.config.AUTO_WINDOW_NAME, color_image_bgr)  # Shows an image window on the screen.

            key = cv2.waitKey(1) & 0xFF  # Stores key for use in the next steps.

            if key == ord("q") or key == 27:  # Checks if the user pressed Q to quit.
                self.detector.close_windows()  # Runs this line as one small step in the program.
                raise KeyboardInterrupt  # Stops the program because something important went wrong.

            if key == ord("s"):  # Checks if the user pressed S to start scanning manually.
                print("")  # Shows a message in the console.
                print("Manual skip selected. Starting scan from current robot pose.")  # Shows a message in the console.
                self.detector.close_windows()  # Runs this line as one small step in the program.
                return self.robot_controller.get_joints_when_ready()  # Gives this result back to the part of the code that called it.

            if key == ord("h"):  # Checks if the user pressed H to move home.
                failed_auto_moves = 0  # Counts automatic moves that failed.
                total_auto_moves = 0  # Counts all automatic moves already made.
                stable_frame_count = 0  # Counts how many frames the box stayed still.
                previous_box = None  # Stores the box from the previous frame.
                self.robot_controller.move_to_joints(  # Moves the robot using joint angles.
                    self.config.HOME_JOINTS,  # Adds one item to the multi-line value.
                    "Home_From_Auto_Center",  # Adds one item to the multi-line value.
                )  # Closes the multi-line code started above.

            if key == ord("c"):  # Checks if the user pressed C to move to the center reference.
                failed_auto_moves = 0  # Counts automatic moves that failed.
                total_auto_moves = 0  # Counts all automatic moves already made.
                stable_frame_count = 0  # Counts how many frames the box stayed still.
                previous_box = None  # Stores the box from the previous frame.
                self.robot_controller.move_to_joints(  # Moves the robot using joint angles.
                    self.config.CENTER_REFERENCE_JOINTS,  # Adds one item to the multi-line value.
                    "Center_Reference_From_Auto_Center",  # Adds one item to the multi-line value.
                )  # Closes the multi-line code started above.

            if box is not None and self.detector.is_box_centered(box):  # Checks if this value exists before using it.
                if stable_frame_count >= self.config.AUTO_REQUIRED_STABLE_FRAMES:  # Checks a condition before running the next indented lines.
                    print("")  # Shows a message in the console.
                    print("=" * 70)  # Shows a message in the console.
                    print("AUTO CENTERING FINISHED")  # Shows a message in the console.
                    print("=" * 70)  # Shows a message in the console.
                    print("The camera is centered on the box.")  # Shows a message in the console.
                    print("Continuing with reference point cloud capture.")  # Shows a message in the console.
                    print("=" * 70)  # Shows a message in the console.
                    self.detector.close_windows()  # Runs this line as one small step in the program.
                    return self.robot_controller.get_joints_when_ready()  # Gives this result back to the part of the code that called it.

            if self.should_move(  # Checks a condition before running the next indented lines.
                box,  # Adds one item to the multi-line value.
                stable_frame_count,  # Adds one item to the multi-line value.
                last_auto_move_time,  # Adds one item to the multi-line value.
                failed_auto_moves,  # Adds one item to the multi-line value.
                total_auto_moves,  # Adds one item to the multi-line value.
            ):  # Closes the multi-line code started above.
                point_camera = self.detector.get_box_center_3d(depth_frame, box)  # Stores a 3D point from the camera view.

                if point_camera is None:  # Checks if this value is missing.
                    print("Auto move skipped. No valid 3D box center.")  # Shows a message in the console.
                    failed_auto_moves += 1  # Runs this line as one small step in the program.
                else:  # Runs this part when the earlier condition was not true.
                    actual_joints = self.move_camera_one_step_to_box_center(point_camera)  # Stores the real joint angles read from the robot.

                    if actual_joints is None:  # Checks if this value is missing.
                        failed_auto_moves += 1  # Runs this line as one small step in the program.
                    else:  # Runs this part when the earlier condition was not true.
                        failed_auto_moves = 0  # Counts automatic moves that failed.
                        total_auto_moves += 1  # Runs this line as one small step in the program.

                stable_frame_count = 0  # Counts how many frames the box stayed still.
                previous_box = None  # Stores the box from the previous frame.
                last_auto_move_time = time.time()  # Stores the time of the last automatic move.

            if failed_auto_moves >= self.config.AUTO_MAX_FAILED_MOVES:  # Checks a condition before running the next indented lines.
                self.detector.close_windows()  # Runs this line as one small step in the program.
                raise Exception("Auto centering stopped because too many robot moves failed.")  # Stops the program because something important went wrong.

            if total_auto_moves >= self.config.AUTO_MAX_TOTAL_MOVES:  # Checks a condition before running the next indented lines.
                self.detector.close_windows()  # Runs this line as one small step in the program.
                raise Exception("Auto centering stopped because the maximum move count was reached.")  # Stops the program because something important went wrong.
