import cv2
import numpy as np
import pyrealsense2 as rs


class AutoBoxDetector:
    def __init__(self, config):
        self.config = config

    def get_depth_in_region(self, depth_image, depth_scale, x1, y1, x2, y2):
        image_height, image_width = depth_image.shape

        x1 = max(0, min(int(x1), image_width))
        x2 = max(0, min(int(x2), image_width))
        y1 = max(0, min(int(y1), image_height))
        y2 = max(0, min(int(y2), image_height))

        if x2 <= x1 or y2 <= y1:
            return None

        depth_crop = depth_image[y1:y2, x1:x2].astype(np.float32) * depth_scale

        valid_depth = depth_crop[
            (depth_crop > self.config.AUTO_CENTER_MIN_DEPTH_M)
            & (depth_crop < self.config.AUTO_CENTER_MAX_DEPTH_M)
        ]

        if valid_depth.size == 0:
            return None

        return float(np.percentile(valid_depth, 30))

    def create_roi_mask(self, image_height, image_width):
        roi_mask = np.zeros((image_height, image_width), dtype=np.uint8)

        x1 = int(image_width * self.config.AUTO_DETECTION_ROI_LEFT_RATIO)
        x2 = int(image_width * self.config.AUTO_DETECTION_ROI_RIGHT_RATIO)
        y1 = int(image_height * self.config.AUTO_DETECTION_ROI_TOP_RATIO)
        y2 = int(image_height * self.config.AUTO_DETECTION_ROI_BOTTOM_RATIO)

        roi_mask[y1:y2, x1:x2] = 255

        return roi_mask

    def create_depth_mask(self, depth_image, depth_scale):
        image_height, image_width = depth_image.shape
        depth_meters = depth_image.astype(np.float32) * depth_scale

        roi_mask = self.create_roi_mask(image_height, image_width)

        valid_mask = (
            (depth_meters > self.config.AUTO_CENTER_MIN_DEPTH_M)
            & (depth_meters < self.config.AUTO_CENTER_MAX_DEPTH_M)
            & (roi_mask == 255)
        )

        if not np.any(valid_mask):
            return None

        valid_depth_values = depth_meters[valid_mask]
        front_depth = np.percentile(valid_depth_values, self.config.AUTO_DEPTH_PERCENTILE)

        mask = (
            valid_mask
            & (depth_meters > front_depth - self.config.AUTO_DEPTH_FRONT_MARGIN)
            & (depth_meters < front_depth + self.config.AUTO_DEPTH_BACK_MARGIN)
        )

        mask = mask.astype(np.uint8) * 255

        close_kernel = np.ones((11, 11), np.uint8)
        open_kernel = np.ones((5, 5), np.uint8)

        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, close_kernel, iterations=3)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, open_kernel, iterations=1)
        mask = cv2.bitwise_and(mask, roi_mask)

        return mask

    def detect_box(self, depth_image, depth_scale):
        mask = self.create_depth_mask(depth_image, depth_scale)

        if mask is None:
            return None, None

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        image_height, image_width = depth_image.shape
        image_center_x = image_width / 2.0
        image_center_y = image_height / 2.0

        best_box = None
        best_score = 0

        for contour in contours:
            area = cv2.contourArea(contour)

            if area < self.config.AUTO_MIN_BOX_AREA:
                continue

            x, y, width, height = cv2.boundingRect(contour)

            if width < self.config.AUTO_MIN_BOX_WIDTH or height < self.config.AUTO_MIN_BOX_HEIGHT:
                continue

            if width > image_width * 0.98 or height > image_height * 0.98:
                continue

            aspect_ratio = width / float(height)

            if aspect_ratio < 0.50 or aspect_ratio > 4.50:
                continue

            x1 = x
            y1 = y
            x2 = x + width
            y2 = y + height

            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)

            distance_meters = self.get_depth_in_region(
                depth_image,
                depth_scale,
                x1,
                y1,
                x2,
                y2,
            )

            if distance_meters is None:
                continue

            center_error = np.sqrt(
                (center_x - image_center_x) ** 2
                + (center_y - image_center_y) ** 2
            )

            area_score = area / float(image_width * image_height)
            center_score = 1.0 / (1.0 + center_error)
            score = area_score * 1000.0 + center_score * 150.0

            if score > best_score:
                best_score = score
                best_box = {
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2,
                    "center_x": center_x,
                    "center_y": center_y,
                    "distance_meters": distance_meters,
                    "area": area,
                }

        return best_box, mask

    def get_box_center_3d(self, depth_frame, box):
        center_x = box["center_x"]
        center_y = box["center_y"]
        depth_meters = box["distance_meters"]

        if depth_meters is None:
            return None

        if depth_meters <= self.config.AUTO_CENTER_MIN_DEPTH_M:
            return None

        if depth_meters >= self.config.AUTO_CENTER_MAX_DEPTH_M:
            return None

        intrinsics = depth_frame.profile.as_video_stream_profile().intrinsics

        point_camera = rs.rs2_deproject_pixel_to_point(
            intrinsics,
            [center_x, center_y],
            depth_meters,
        )

        return np.array(point_camera, dtype=np.float64)

    def get_box_offset_pixels(self, box):
        image_center_x = int(self.config.RS_WIDTH / 2)
        image_center_y = int(self.config.RS_HEIGHT / 2)

        offset_x = box["center_x"] - image_center_x
        offset_y = box["center_y"] - image_center_y

        return offset_x, offset_y

    def is_box_centered(self, box):
        offset_x, offset_y = self.get_box_offset_pixels(box)

        center_error = np.sqrt(offset_x ** 2 + offset_y ** 2)
        distance_error = abs(box["distance_meters"] - self.config.AUTO_CENTER_TARGET_DISTANCE_M)

        return (
            center_error <= self.config.AUTO_CENTER_TOLERANCE_PX
            and distance_error <= self.config.AUTO_DISTANCE_TOLERANCE_M
        )

    def is_box_stable(self, current_box, previous_box):
        if current_box is None or previous_box is None:
            return False

        center_change = np.sqrt(
            (current_box["center_x"] - previous_box["center_x"]) ** 2
            + (current_box["center_y"] - previous_box["center_y"]) ** 2
        )

        distance_change = abs(
            current_box["distance_meters"] - previous_box["distance_meters"]
        )

        return (
            center_change <= self.config.AUTO_STABLE_CENTER_TOLERANCE_PX
            and distance_change <= self.config.AUTO_STABLE_DISTANCE_TOLERANCE_M
        )

    def update_stability(self, box, previous_box, stable_frame_count):
        if box is None:
            return 0, None

        if self.is_box_stable(box, previous_box):
            stable_frame_count += 1
        else:
            stable_frame_count = 1

        return stable_frame_count, box

    def calculate_camera_correction(self, point_camera):
        camera_offset = np.array([
            point_camera[0] * self.config.AUTO_CENTERING_GAIN,
            point_camera[1] * self.config.AUTO_CENTERING_GAIN,
            (point_camera[2] - self.config.AUTO_CENTER_TARGET_DISTANCE_M) * self.config.AUTO_DEPTH_GAIN,
        ])

        offset_size = np.linalg.norm(camera_offset)

        if offset_size > self.config.AUTO_CENTER_MAX_TRANSLATION_STEP_M:
            camera_offset = (
                camera_offset / offset_size
            ) * self.config.AUTO_CENTER_MAX_TRANSLATION_STEP_M

        return camera_offset

    def draw_box(self, image, box):
        image_center_x = int(self.config.RS_WIDTH / 2)
        image_center_y = int(self.config.RS_HEIGHT / 2)

        cv2.rectangle(image, (box["x1"], box["y1"]), (box["x2"], box["y2"]), (0, 255, 0), 3)
        cv2.circle(image, (box["center_x"], box["center_y"]), 7, (0, 0, 255), -1)
        cv2.line(image, (image_center_x - 15, image_center_y), (image_center_x + 15, image_center_y), (255, 0, 0), 2)
        cv2.line(image, (image_center_x, image_center_y - 15), (image_center_x, image_center_y + 15), (255, 0, 0), 2)
        cv2.line(image, (image_center_x, image_center_y), (box["center_x"], box["center_y"]), (0, 255, 255), 2)
        cv2.putText(
            image,
            f"Box | {box['distance_meters']:.2f} m",
            (box["x1"], max(box["y1"] - 10, 25)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 255, 0),
            2,
        )

    @staticmethod
    def draw_text(image, text, y, color):
        cv2.putText(image, text, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2)

    def draw_center_screen(self, color_image_bgr, box, stable_frame_count, failed_auto_moves, total_auto_moves):
        self.draw_text(color_image_bgr, "AUTO CENTERING BEFORE SCAN", 30, (0, 255, 255))
        self.draw_text(
            color_image_bgr,
            "S = start scan manually | H = home | C = center reference | Q = quit",
            60,
            (255, 255, 255),
        )
        self.draw_text(
            color_image_bgr,
            f"Moves: {total_auto_moves}/{self.config.AUTO_MAX_TOTAL_MOVES} | Failed: {failed_auto_moves}/{self.config.AUTO_MAX_FAILED_MOVES}",
            90,
            (255, 255, 255),
        )

        if box is None:
            self.draw_text(color_image_bgr, "No box detected", 120, (0, 0, 255))
            return

        self.draw_box(color_image_bgr, box)

        offset_x, offset_y = self.get_box_offset_pixels(box)
        centered_status = "Centered" if self.is_box_centered(box) else "Moving"

        self.draw_text(
            color_image_bgr,
            (
                f"Offset X={offset_x}px Y={offset_y}px | "
                f"{centered_status} | Stable {stable_frame_count}/{self.config.AUTO_REQUIRED_STABLE_FRAMES}"
            ),
            120,
            (0, 255, 0),
        )

    def close_windows(self):
        for window_name in [self.config.AUTO_WINDOW_NAME, self.config.AUTO_MASK_WINDOW_NAME]:
            try:
                cv2.destroyWindow(window_name)
            except cv2.error:
                pass
