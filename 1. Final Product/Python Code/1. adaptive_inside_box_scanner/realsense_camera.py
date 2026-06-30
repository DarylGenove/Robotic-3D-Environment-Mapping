import numpy as np  # Loads NumPy as np so the code can do fast number and matrix math.
import open3d as o3d  # Loads Open3D so the code can work with 3D point clouds.
import pyrealsense2 as rs  # Loads the RealSense library so the code can use the Intel camera.


class RealSenseCamera:  # Makes a toolbox for starting the camera and capturing 3D scans.
    def __init__(self, config):  # Makes a function named   init  .
        self.config = config  # Stores the scanner settings so the program can use them.
        self.pipeline = None  # Saves pipeline inside this object so other methods can use it.
        self.align = None  # Saves align inside this object so other methods can use it.
        self.depth_scale = None  # Converts raw depth numbers into meters.
        self.intrinsic_o3d = None  # Saves intrinsic o3d inside this object so other methods can use it.
        self.spatial_filter = None  # Saves spatial filter inside this object so other methods can use it.
        self.temporal_filter = None  # Saves temporal filter inside this object so other methods can use it.
        self.hole_filling_filter = None  # Saves hole filling filter inside this object so other methods can use it.

    def start(self):  # Starts and prepares the RealSense camera.
        print("\nStarting Intel RealSense D455f...")  # Shows a message in the console.

        self.pipeline = rs.pipeline()  # Saves pipeline inside this object so other methods can use it.
        rs_config = rs.config()  # Stores rs config for use in the next steps.

        rs_config.enable_stream(  # Turns on a RealSense camera stream.
            rs.stream.depth,  # Adds one item to the multi-line value.
            self.config.RS_WIDTH,  # Adds one item to the multi-line value.
            self.config.RS_HEIGHT,  # Adds one item to the multi-line value.
            rs.format.z16,  # Adds one item to the multi-line value.
            self.config.RS_FPS,  # Adds one item to the multi-line value.
        )  # Closes the multi-line code started above.
        rs_config.enable_stream(  # Turns on a RealSense camera stream.
            rs.stream.color,  # Adds one item to the multi-line value.
            self.config.RS_WIDTH,  # Adds one item to the multi-line value.
            self.config.RS_HEIGHT,  # Adds one item to the multi-line value.
            rs.format.rgb8,  # Adds one item to the multi-line value.
            self.config.RS_FPS,  # Adds one item to the multi-line value.
        )  # Closes the multi-line code started above.

        profile = self.pipeline.start(rs_config)  # Stores the active RealSense camera profile.
        depth_sensor = profile.get_device().first_depth_sensor()  # Stores the RealSense depth sensor settings object.

        self._configure_depth_sensor(depth_sensor)  # Runs this line as one small step in the program.

        self.depth_scale = depth_sensor.get_depth_scale()  # Converts raw depth numbers into meters.
        print("Depth scale:", self.depth_scale)  # Shows a message in the console.

        self.spatial_filter = rs.spatial_filter()  # Saves spatial filter inside this object so other methods can use it.
        self.temporal_filter = rs.temporal_filter()  # Saves temporal filter inside this object so other methods can use it.
        self.hole_filling_filter = rs.hole_filling_filter()  # Saves hole filling filter inside this object so other methods can use it.

        self.spatial_filter.set_option(rs.option.filter_magnitude, 2)  # Changes a RealSense camera setting.
        self.spatial_filter.set_option(rs.option.filter_smooth_alpha, 0.5)  # Changes a RealSense camera setting.
        self.spatial_filter.set_option(rs.option.filter_smooth_delta, 20)  # Changes a RealSense camera setting.
        self.hole_filling_filter.set_option(rs.option.holes_fill, 1)  # Changes a RealSense camera setting.

        self.align = rs.align(rs.stream.color)  # Saves align inside this object so other methods can use it.

        print(f"Warming up RealSense for {self.config.WARMUP_FRAMES} frames...")  # Shows a message in the console.
        for _ in range(self.config.WARMUP_FRAMES):  # Repeats the next indented lines for each item.
            self.pipeline.wait_for_frames()  # Waits until the camera gives a new frame.

        color_stream = profile.get_stream(rs.stream.color).as_video_stream_profile()  # Stores color stream for use in the next steps.
        intrinsics = color_stream.get_intrinsics()  # Stores the camera lens numbers needed for 3D projection.

        self.intrinsic_o3d = o3d.camera.PinholeCameraIntrinsic(  # Saves intrinsic o3d inside this object so other methods can use it.
            intrinsics.width,  # Adds one item to the multi-line value.
            intrinsics.height,  # Adds one item to the multi-line value.
            intrinsics.fx,  # Adds one item to the multi-line value.
            intrinsics.fy,  # Adds one item to the multi-line value.
            intrinsics.ppx,  # Adds one item to the multi-line value.
            intrinsics.ppy,  # Adds one item to the multi-line value.
        )  # Closes the multi-line code started above.

        print(f"RealSense ready: fx={intrinsics.fx:.1f}, fy={intrinsics.fy:.1f}")  # Shows a message in the console.

    def _configure_depth_sensor(self, depth_sensor):  # Changes RealSense depth settings for better scanning.
        if depth_sensor.supports(rs.option.visual_preset):  # Checks a condition before running the next indented lines.
            try:  # Tries the next steps because they might fail.
                depth_sensor.set_option(  # Changes a RealSense camera setting.
                    rs.option.visual_preset,  # Adds one item to the multi-line value.
                    int(rs.rs400_visual_preset.high_density),  # Changes the value into a whole number.
                )  # Closes the multi-line code started above.
                print("Visual preset: HIGH_DENSITY")  # Shows a message in the console.
            except Exception as error:  # Runs this part if an error happens and saves the error message.
                print("Could not set HIGH_DENSITY preset:", error)  # Shows a message in the console.

        if depth_sensor.supports(rs.option.emitter_enabled):  # Checks a condition before running the next indented lines.
            try:  # Tries the next steps because they might fail.
                depth_sensor.set_option(rs.option.emitter_enabled, 1)  # Changes a RealSense camera setting.
                print("Emitter enabled.")  # Shows a message in the console.
            except Exception as error:  # Runs this part if an error happens and saves the error message.
                print("Could not enable emitter:", error)  # Shows a message in the console.

        if depth_sensor.supports(rs.option.laser_power):  # Checks a condition before running the next indented lines.
            try:  # Tries the next steps because they might fail.
                laser_range = depth_sensor.get_option_range(rs.option.laser_power)  # Stores laser range for use in the next steps.
                depth_sensor.set_option(rs.option.laser_power, laser_range.max)  # Changes a RealSense camera setting.
                print("Laser power set to max:", laser_range.max)  # Shows a message in the console.
            except Exception as error:  # Runs this part if an error happens and saves the error message.
                print("Could not set laser power:", error)  # Shows a message in the console.

    def stop(self):  # Stops the RealSense camera safely.
        if self.pipeline is not None:  # Checks if this value exists before using it.
            self.pipeline.stop()  # Runs this line as one small step in the program.
            print("\nRealSense stopped.")  # Shows a message in the console.

    def get_aligned_frame(self):  # Gets one depth frame and one color frame lined up together.
        frames = self.pipeline.wait_for_frames()  # Stores the latest camera frames.
        aligned_frames = self.align.process(frames)  # Stores depth and color frames aligned to the same image.

        depth_frame = aligned_frames.get_depth_frame()  # Stores one RealSense depth frame.
        color_frame = aligned_frames.get_color_frame()  # Stores color frame for use in the next steps.

        if not depth_frame or not color_frame:  # Checks if this condition is not true.
            return None, None, None  # Gives this result back to the part of the code that called it.

        depth_image = np.asanyarray(depth_frame.get_data())  # Stores the depth image as numbers.
        color_image_rgb = np.asanyarray(color_frame.get_data())  # Stores the color camera image in RGB order.

        return depth_frame, color_image_rgb, depth_image  # Gives this result back to the part of the code that called it.

    def make_rgbd(self, color_image, depth_image):  # Turns color and depth images into one RGBD image.
        color_o3d = o3d.geometry.Image(color_image.astype(np.uint8))  # Stores color o3d for use in the next steps.
        depth_o3d = o3d.geometry.Image(depth_image.astype(np.uint16))  # Stores depth o3d for use in the next steps.

        return o3d.geometry.RGBDImage.create_from_color_and_depth(  # Gives this result back to the part of the code that called it.
            color_o3d,  # Adds one item to the multi-line value.
            depth_o3d,  # Adds one item to the multi-line value.
            depth_scale=1.0 / self.depth_scale,  # Converts raw depth numbers into meters.
            depth_trunc=self.config.DEPTH_TRUNC_MAX,  # Stores depth trunc for use in the next steps.
            convert_rgb_to_intensity=False,  # Stores convert rgb to intensity for use in the next steps.
        )  # Closes the multi-line code started above.

    def capture_stable_pointcloud(self, frames_to_capture=None):  # Captures many frames and combines them into a steadier point cloud.
        if frames_to_capture is None:  # Checks if this value is missing.
            frames_to_capture = self.config.CAPTURE_FRAMES_PER_POSITION  # Stores frames to capture for use in the next steps.

        color_stack = []  # Stores many color images before combining them.
        depth_stack = []  # Stores many depth images before combining them.

        print(f"Capturing {frames_to_capture} frames...")  # Shows a message in the console.

        for frame_index in range(frames_to_capture):  # Repeats the next indented lines for each item.
            frames = self.pipeline.wait_for_frames()  # Stores the latest camera frames.
            aligned_frames = self.align.process(frames)  # Stores depth and color frames aligned to the same image.

            depth_frame = aligned_frames.get_depth_frame()  # Stores one RealSense depth frame.
            color_frame = aligned_frames.get_color_frame()  # Stores color frame for use in the next steps.

            if not depth_frame or not color_frame:  # Checks if this condition is not true.
                print(f"Frame {frame_index + 1}: skipped because depth or color is missing.")  # Shows a message in the console.
                continue  # Skips the rest of this loop and starts the next loop round.

            depth_frame = self.spatial_filter.process(depth_frame)  # Stores one RealSense depth frame.
            depth_frame = self.temporal_filter.process(depth_frame)  # Stores one RealSense depth frame.
            depth_frame = self.hole_filling_filter.process(depth_frame)  # Stores one RealSense depth frame.

            depth_stack.append(np.asanyarray(depth_frame.get_data()).astype(np.uint16))  # Reads the image data from the camera frame.
            color_stack.append(np.asanyarray(color_frame.get_data()).astype(np.uint8))  # Reads the image data from the camera frame.

            print(f"Frame {frame_index + 1}/{frames_to_capture} captured.")  # Shows a message in the console.

        if not depth_stack:  # Checks if this condition is not true.
            return None  # Gives this result back to the part of the code that called it.

        print("Combining frames into one stable point cloud...")  # Shows a message in the console.

        depth_median = np.median(np.stack(depth_stack, axis=0), axis=0).astype(np.uint16)  # Stores the middle depth value from many frames to reduce noise.
        color_mean = np.mean(np.stack(color_stack, axis=0), axis=0).astype(np.uint8)  # Stores the average color from many frames.

        rgbd = self.make_rgbd(color_mean, depth_median)  # Stores a combined color-and-depth image.

        point_cloud = o3d.geometry.PointCloud.create_from_rgbd_image(  # Stores the 3D points captured by the camera.
            rgbd,  # Adds one item to the multi-line value.
            self.intrinsic_o3d,  # Adds one item to the multi-line value.
        )  # Closes the multi-line code started above.

        if len(point_cloud.points) == 0:  # Checks if there are no items to work with.
            return None  # Gives this result back to the part of the code that called it.

        return point_cloud  # Gives this result back to the part of the code that called it.
