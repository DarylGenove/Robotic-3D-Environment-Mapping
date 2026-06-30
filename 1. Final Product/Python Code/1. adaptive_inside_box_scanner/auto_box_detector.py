import cv2  # Loads OpenCV so the code can work with camera images.
import numpy as np  # Loads NumPy as np so the code can do fast number and matrix math.
import pyrealsense2 as rs  # Loads the RealSense library so the code can use the Intel camera.


class AutoBoxDetector:  # Makes a toolbox that finds the cabinet box in the camera image.
    def __init__(self, config):  # Makes a function named   init  .
        self.config = config  # Stores the scanner settings so the program can use them.

    def get_depth_in_region(self, depth_image, depth_scale, x1, y1, x2, y2):  # Finds the useful depth distance inside a small image area.
        image_height, image_width = depth_image.shape  # Runs this line as one small step in the program.

        x1 = max(0, min(int(x1), image_width))  # Stores x1 for use in the next steps.
        x2 = max(0, min(int(x2), image_width))  # Stores x2 for use in the next steps.
        y1 = max(0, min(int(y1), image_height))  # Stores y1 for use in the next steps.
        y2 = max(0, min(int(y2), image_height))  # Stores y2 for use in the next steps.

        if x2 <= x1 or y2 <= y1:  # Checks a condition before running the next indented lines.
            return None  # Gives this result back to the part of the code that called it.

        depth_crop = depth_image[y1:y2, x1:x2].astype(np.float32) * depth_scale  # Stores depth crop for use in the next steps.

        valid_depth = depth_crop[  # Stores depth values that are inside the allowed distance range.
            (depth_crop > self.config.AUTO_CENTER_MIN_DEPTH_M)  # Runs this line as one small step in the program.
            & (depth_crop < self.config.AUTO_CENTER_MAX_DEPTH_M)  # Adds another rule to the filter condition.
        ]  # Closes the multi-line code started above.

        if valid_depth.size == 0:  # Checks a condition before running the next indented lines.
            return None  # Gives this result back to the part of the code that called it.

        return float(np.percentile(valid_depth, 30))  # Gives this result back to the part of the code that called it.

    def create_roi_mask(self, image_height, image_width):  # Creates the camera area where the box is allowed to be found.
        roi_mask = np.zeros((image_height, image_width), dtype=np.uint8)  # Stores roi mask for use in the next steps.

        x1 = int(image_width * self.config.AUTO_DETECTION_ROI_LEFT_RATIO)  # Stores x1 for use in the next steps.
        x2 = int(image_width * self.config.AUTO_DETECTION_ROI_RIGHT_RATIO)  # Stores x2 for use in the next steps.
        y1 = int(image_height * self.config.AUTO_DETECTION_ROI_TOP_RATIO)  # Stores y1 for use in the next steps.
        y2 = int(image_height * self.config.AUTO_DETECTION_ROI_BOTTOM_RATIO)  # Stores y2 for use in the next steps.

        roi_mask[y1:y2, x1:x2] = 255  # Runs this line as one small step in the program.

        return roi_mask  # Gives this result back to the part of the code that called it.

    def create_depth_mask(self, depth_image, depth_scale):  # Creates a black-and-white depth image to help find the box.
        image_height, image_width = depth_image.shape  # Runs this line as one small step in the program.
        depth_meters = depth_image.astype(np.float32) * depth_scale  # Stores depth meters for use in the next steps.

        roi_mask = self.create_roi_mask(image_height, image_width)  # Stores roi mask for use in the next steps.

        valid_mask = (  # Marks only points/pixels that look usable.
            (depth_meters > self.config.AUTO_CENTER_MIN_DEPTH_M)  # Runs this line as one small step in the program.
            & (depth_meters < self.config.AUTO_CENTER_MAX_DEPTH_M)  # Adds another rule to the filter condition.
            & (roi_mask == 255)  # Adds another rule to the filter condition.
        )  # Closes the multi-line code started above.

        if not np.any(valid_mask):  # Checks if this condition is not true.
            return None  # Gives this result back to the part of the code that called it.

        valid_depth_values = depth_meters[valid_mask]  # Stores useful depth values from the selected image area.
        front_depth = np.percentile(valid_depth_values, self.config.AUTO_DEPTH_PERCENTILE)  # Stores the estimated front distance of the box.

        mask = (  # Stores True or False for points/pixels that should be kept.
            valid_mask  # Runs this line as one small step in the program.
            & (depth_meters > front_depth - self.config.AUTO_DEPTH_FRONT_MARGIN)  # Adds another rule to the filter condition.
            & (depth_meters < front_depth + self.config.AUTO_DEPTH_BACK_MARGIN)  # Adds another rule to the filter condition.
        )  # Closes the multi-line code started above.

        mask = mask.astype(np.uint8) * 255  # Stores True or False for points/pixels that should be kept.

        close_kernel = np.ones((11, 11), np.uint8)  # Stores close kernel for use in the next steps.
        open_kernel = np.ones((5, 5), np.uint8)  # Stores open kernel for use in the next steps.

        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, close_kernel, iterations=3)  # Stores True or False for points/pixels that should be kept.
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, open_kernel, iterations=1)  # Stores True or False for points/pixels that should be kept.
        mask = cv2.bitwise_and(mask, roi_mask)  # Stores True or False for points/pixels that should be kept.

        return mask  # Gives this result back to the part of the code that called it.

    def detect_box(self, depth_image, depth_scale):  # Finds the best box shape in the depth image.
        mask = self.create_depth_mask(depth_image, depth_scale)  # Stores True or False for points/pixels that should be kept.

        if mask is None:  # Checks if this value is missing.
            return None, None  # Gives this result back to the part of the code that called it.

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # Finds shapes in the black-and-white mask image.

        image_height, image_width = depth_image.shape  # Runs this line as one small step in the program.
        image_center_x = image_width / 2.0  # Stores image center x for use in the next steps.
        image_center_y = image_height / 2.0  # Stores image center y for use in the next steps.

        best_box = None  # Stores the best detected box so far.
        best_score = 0  # Stores the score of the best detected box.

        for contour in contours:  # Repeats the next indented lines for each item.
            area = cv2.contourArea(contour)  # Stores how large the detected shape is.

            if area < self.config.AUTO_MIN_BOX_AREA:  # Checks a condition before running the next indented lines.
                continue  # Skips the rest of this loop and starts the next loop round.

            x, y, width, height = cv2.boundingRect(contour)  # Draws a simple rectangle around one detected shape.

            if width < self.config.AUTO_MIN_BOX_WIDTH or height < self.config.AUTO_MIN_BOX_HEIGHT:  # Checks a condition before running the next indented lines.
                continue  # Skips the rest of this loop and starts the next loop round.

            if width > image_width * 0.98 or height > image_height * 0.98:  # Checks a condition before running the next indented lines.
                continue  # Skips the rest of this loop and starts the next loop round.

            aspect_ratio = width / float(height)  # Stores the rectangle width compared with its height.

            if aspect_ratio < 0.50 or aspect_ratio > 4.50:  # Checks a condition before running the next indented lines.
                continue  # Skips the rest of this loop and starts the next loop round.

            x1 = x  # Stores x1 for use in the next steps.
            y1 = y  # Stores y1 for use in the next steps.
            x2 = x + width  # Stores x2 for use in the next steps.
            y2 = y + height  # Stores y2 for use in the next steps.

            center_x = int((x1 + x2) / 2)  # Stores the horizontal center of the detected box.
            center_y = int((y1 + y2) / 2)  # Stores the vertical center of the detected box.

            distance_meters = self.get_depth_in_region(  # Stores the detected box distance in meters.
                depth_image,  # Adds one item to the multi-line value.
                depth_scale,  # Adds one item to the multi-line value.
                x1,  # Adds one item to the multi-line value.
                y1,  # Adds one item to the multi-line value.
                x2,  # Adds one item to the multi-line value.
                y2,  # Adds one item to the multi-line value.
            )  # Closes the multi-line code started above.

            if distance_meters is None:  # Checks if this value is missing.
                continue  # Skips the rest of this loop and starts the next loop round.

            center_error = np.sqrt(  # Stores how far the box center is from the image center.
                (center_x - image_center_x) ** 2  # Runs this line as one small step in the program.
                + (center_y - image_center_y) ** 2  # Runs this line as one small step in the program.
            )  # Closes the multi-line code started above.

            area_score = area / float(image_width * image_height)  # Gives a bigger score to bigger detected boxes.
            center_score = 1.0 / (1.0 + center_error)  # Gives a bigger score when the box is closer to the image center.
            score = area_score * 1000.0 + center_score * 150.0  # Combines size and center position to choose the best box.

            if score > best_score:  # Checks a condition before running the next indented lines.
                best_score = score  # Stores the score of the best detected box.
                best_box = {  # Stores the best detected box so far.
                    "x1": x1,  # Adds one named value to the dictionary.
                    "y1": y1,  # Adds one named value to the dictionary.
                    "x2": x2,  # Adds one named value to the dictionary.
                    "y2": y2,  # Adds one named value to the dictionary.
                    "center_x": center_x,  # Adds one named value to the dictionary.
                    "center_y": center_y,  # Adds one named value to the dictionary.
                    "distance_meters": distance_meters,  # Adds one named value to the dictionary.
                    "area": area,  # Adds one named value to the dictionary.
                }  # Closes the multi-line code started above.

        return best_box, mask  # Gives this result back to the part of the code that called it.

    def get_box_center_3d(self, depth_frame, box):  # Turns the detected box center pixel into a 3D camera point.
        center_x = box["center_x"]  # Stores the horizontal center of the detected box.
        center_y = box["center_y"]  # Stores the vertical center of the detected box.
        depth_meters = box["distance_meters"]  # Stores depth meters for use in the next steps.

        if depth_meters is None:  # Checks if this value is missing.
            return None  # Gives this result back to the part of the code that called it.

        if depth_meters <= self.config.AUTO_CENTER_MIN_DEPTH_M:  # Checks a condition before running the next indented lines.
            return None  # Gives this result back to the part of the code that called it.

        if depth_meters >= self.config.AUTO_CENTER_MAX_DEPTH_M:  # Checks a condition before running the next indented lines.
            return None  # Gives this result back to the part of the code that called it.

        intrinsics = depth_frame.profile.as_video_stream_profile().intrinsics  # Stores the camera lens numbers needed for 3D projection.

        point_camera = rs.rs2_deproject_pixel_to_point(  # Stores a 3D point from the camera view.
            intrinsics,  # Adds one item to the multi-line value.
            [center_x, center_y],  # Adds one item to the multi-line value.
            depth_meters,  # Adds one item to the multi-line value.
        )  # Closes the multi-line code started above.

        return np.array(point_camera, dtype=np.float64)  # Gives this result back to the part of the code that called it.

    def get_box_offset_pixels(self, box):  # Measures how far the box is from the image center in pixels.
        image_center_x = int(self.config.RS_WIDTH / 2)  # Stores image center x for use in the next steps.
        image_center_y = int(self.config.RS_HEIGHT / 2)  # Stores image center y for use in the next steps.

        offset_x = box["center_x"] - image_center_x  # Stores how far the box is from the image center horizontally.
        offset_y = box["center_y"] - image_center_y  # Stores how far the box is from the image center vertically.

        return offset_x, offset_y  # Gives this result back to the part of the code that called it.

    def is_box_centered(self, box):  # Checks if the box is centered and at the right distance.
        offset_x, offset_y = self.get_box_offset_pixels(box)  # Runs this line as one small step in the program.

        center_error = np.sqrt(offset_x ** 2 + offset_y ** 2)  # Stores how far the box center is from the image center.
        distance_error = abs(box["distance_meters"] - self.config.AUTO_CENTER_TARGET_DISTANCE_M)  # Stores how far the box distance is from the wanted distance.

        return (  # Gives this result back to the part of the code that called it.
            center_error <= self.config.AUTO_CENTER_TOLERANCE_PX  # Runs this line as one small step in the program.
            and distance_error <= self.config.AUTO_DISTANCE_TOLERANCE_M  # Runs this line as one small step in the program.
        )  # Closes the multi-line code started above.

    def is_box_stable(self, current_box, previous_box):  # Checks if the detected box stayed almost still.
        if current_box is None or previous_box is None:  # Checks if this value is missing.
            return False  # Gives this result back to the part of the code that called it.

        center_change = np.sqrt(  # Stores center change for use in the next steps.
            (current_box["center_x"] - previous_box["center_x"]) ** 2  # Runs this line as one small step in the program.
            + (current_box["center_y"] - previous_box["center_y"]) ** 2  # Runs this line as one small step in the program.
        )  # Closes the multi-line code started above.

        distance_change = abs(  # Stores distance change for use in the next steps.
            current_box["distance_meters"] - previous_box["distance_meters"]  # Runs this line as one small step in the program.
        )  # Closes the multi-line code started above.

        return (  # Gives this result back to the part of the code that called it.
            center_change <= self.config.AUTO_STABLE_CENTER_TOLERANCE_PX  # Runs this line as one small step in the program.
            and distance_change <= self.config.AUTO_STABLE_DISTANCE_TOLERANCE_M  # Runs this line as one small step in the program.
        )  # Closes the multi-line code started above.

    def update_stability(self, box, previous_box, stable_frame_count):  # Updates the count of stable detection frames.
        if box is None:  # Checks if this value is missing.
            return 0, None  # Gives this result back to the part of the code that called it.

        if self.is_box_stable(box, previous_box):  # Checks a condition before running the next indented lines.
            stable_frame_count += 1  # Runs this line as one small step in the program.
        else:  # Runs this part when the earlier condition was not true.
            stable_frame_count = 1  # Counts how many frames the box stayed still.

        return stable_frame_count, box  # Gives this result back to the part of the code that called it.

    def calculate_camera_correction(self, point_camera):  # Calculates how the camera should move to center the box.
        camera_offset = np.array([  # Stores how far the camera should move to center the box.
            point_camera[0] * self.config.AUTO_CENTERING_GAIN,  # Adds one item to the multi-line value.
            point_camera[1] * self.config.AUTO_CENTERING_GAIN,  # Adds one item to the multi-line value.
            (point_camera[2] - self.config.AUTO_CENTER_TARGET_DISTANCE_M) * self.config.AUTO_DEPTH_GAIN,  # Adds one item to the multi-line value.
        ])  # Closes the multi-line code started above.

        offset_size = np.linalg.norm(camera_offset)  # Stores the size of the requested camera movement.

        if offset_size > self.config.AUTO_CENTER_MAX_TRANSLATION_STEP_M:  # Checks a condition before running the next indented lines.
            camera_offset = (  # Stores how far the camera should move to center the box.
                camera_offset / offset_size  # Runs this line as one small step in the program.
            ) * self.config.AUTO_CENTER_MAX_TRANSLATION_STEP_M  # Closes the multi-line code started above.

        return camera_offset  # Gives this result back to the part of the code that called it.

    def draw_box(self, image, box):  # Draws the detected box and guide marks on the camera image.
        image_center_x = int(self.config.RS_WIDTH / 2)  # Stores image center x for use in the next steps.
        image_center_y = int(self.config.RS_HEIGHT / 2)  # Stores image center y for use in the next steps.

        cv2.rectangle(image, (box["x1"], box["y1"]), (box["x2"], box["y2"]), (0, 255, 0), 3)  # Draws a rectangle around the detected box.
        cv2.circle(image, (box["center_x"], box["center_y"]), 7, (0, 0, 255), -1)  # Draws a dot on the detected box center.
        cv2.line(image, (image_center_x - 15, image_center_y), (image_center_x + 15, image_center_y), (255, 0, 0), 2)  # Draws a guide line on the camera image.
        cv2.line(image, (image_center_x, image_center_y - 15), (image_center_x, image_center_y + 15), (255, 0, 0), 2)  # Draws a guide line on the camera image.
        cv2.line(image, (image_center_x, image_center_y), (box["center_x"], box["center_y"]), (0, 255, 255), 2)  # Draws a guide line on the camera image.
        cv2.putText(  # Writes text on the camera image.
            image,  # Adds one item to the multi-line value.
            f"Box | {box['distance_meters']:.2f} m",  # Adds one named value to the dictionary.
            (box["x1"], max(box["y1"] - 10, 25)),  # Keeps the bigger value.
            cv2.FONT_HERSHEY_SIMPLEX,  # Adds one item to the multi-line value.
            0.65,  # Adds one item to the multi-line value.
            (0, 255, 0),  # Adds one item to the multi-line value.
            2,  # Adds one item to the multi-line value.
        )  # Closes the multi-line code started above.

    @staticmethod  # Lets this helper run without using object data.
    def draw_text(image, text, y, color):  # Draws one line of text on the image.
        cv2.putText(image, text, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2)  # Writes text on the camera image.

    def draw_center_screen(self, color_image_bgr, box, stable_frame_count, failed_auto_moves, total_auto_moves):  # Draws all auto-centering information on the camera screen.
        self.draw_text(color_image_bgr, "AUTO CENTERING BEFORE SCAN", 30, (0, 255, 255))  # Runs this line as one small step in the program.
        self.draw_text(  # Runs this line as one small step in the program.
            color_image_bgr,  # Adds one item to the multi-line value.
            "S = start scan manually | H = home | C = center reference | Q = quit",  # Adds one item to the multi-line value.
            60,  # Adds one item to the multi-line value.
            (255, 255, 255),  # Adds one item to the multi-line value.
        )  # Closes the multi-line code started above.
        self.draw_text(  # Runs this line as one small step in the program.
            color_image_bgr,  # Adds one item to the multi-line value.
            f"Moves: {total_auto_moves}/{self.config.AUTO_MAX_TOTAL_MOVES} | Failed: {failed_auto_moves}/{self.config.AUTO_MAX_FAILED_MOVES}",  # Adds one named value to the dictionary.
            90,  # Adds one item to the multi-line value.
            (255, 255, 255),  # Adds one item to the multi-line value.
        )  # Closes the multi-line code started above.

        if box is None:  # Checks if this value is missing.
            self.draw_text(color_image_bgr, "No box detected", 120, (0, 0, 255))  # Runs this line as one small step in the program.
            return  # Gives this result back to the part of the code that called it.

        self.draw_box(color_image_bgr, box)  # Runs this line as one small step in the program.

        offset_x, offset_y = self.get_box_offset_pixels(box)  # Runs this line as one small step in the program.
        centered_status = "Centered" if self.is_box_centered(box) else "Moving"  # Stores centered status for use in the next steps.

        self.draw_text(  # Runs this line as one small step in the program.
            color_image_bgr,  # Adds one item to the multi-line value.
            (  # Starts a multi-line value.
                f"Offset X={offset_x}px Y={offset_y}px | "  # Runs this line as one small step in the program.
                f"{centered_status} | Stable {stable_frame_count}/{self.config.AUTO_REQUIRED_STABLE_FRAMES}"  # Runs this line as one small step in the program.
            ),  # Adds one item to the multi-line value.
            120,  # Adds one item to the multi-line value.
            (0, 255, 0),  # Adds one item to the multi-line value.
        )  # Closes the multi-line code started above.

    def close_windows(self):  # Closes the auto-centering OpenCV windows.
        for window_name in [self.config.AUTO_WINDOW_NAME, self.config.AUTO_MASK_WINDOW_NAME]:  # Repeats the next indented lines for each item.
            try:  # Tries the next steps because they might fail.
                cv2.destroyWindow(window_name)  # Closes one OpenCV window.
            except cv2.error:  # Runs this line as one small step in the program.
                pass  # Does nothing here, but keeps the code valid.
