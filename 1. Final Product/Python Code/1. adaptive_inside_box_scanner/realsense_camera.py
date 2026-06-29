import numpy as np
import open3d as o3d
import pyrealsense2 as rs


class RealSenseCamera:
    def __init__(self, config):
        self.config = config
        self.pipeline = None
        self.align = None
        self.depth_scale = None
        self.intrinsic_o3d = None
        self.spatial_filter = None
        self.temporal_filter = None
        self.hole_filling_filter = None

    def start(self):
        print("\nStarting Intel RealSense D455f...")

        self.pipeline = rs.pipeline()
        rs_config = rs.config()

        rs_config.enable_stream(
            rs.stream.depth,
            self.config.RS_WIDTH,
            self.config.RS_HEIGHT,
            rs.format.z16,
            self.config.RS_FPS,
        )
        rs_config.enable_stream(
            rs.stream.color,
            self.config.RS_WIDTH,
            self.config.RS_HEIGHT,
            rs.format.rgb8,
            self.config.RS_FPS,
        )

        profile = self.pipeline.start(rs_config)
        depth_sensor = profile.get_device().first_depth_sensor()

        self._configure_depth_sensor(depth_sensor)

        self.depth_scale = depth_sensor.get_depth_scale()
        print("Depth scale:", self.depth_scale)

        self.spatial_filter = rs.spatial_filter()
        self.temporal_filter = rs.temporal_filter()
        self.hole_filling_filter = rs.hole_filling_filter()

        self.spatial_filter.set_option(rs.option.filter_magnitude, 2)
        self.spatial_filter.set_option(rs.option.filter_smooth_alpha, 0.5)
        self.spatial_filter.set_option(rs.option.filter_smooth_delta, 20)
        self.hole_filling_filter.set_option(rs.option.holes_fill, 1)

        self.align = rs.align(rs.stream.color)

        print(f"Warming up RealSense for {self.config.WARMUP_FRAMES} frames...")
        for _ in range(self.config.WARMUP_FRAMES):
            self.pipeline.wait_for_frames()

        color_stream = profile.get_stream(rs.stream.color).as_video_stream_profile()
        intrinsics = color_stream.get_intrinsics()

        self.intrinsic_o3d = o3d.camera.PinholeCameraIntrinsic(
            intrinsics.width,
            intrinsics.height,
            intrinsics.fx,
            intrinsics.fy,
            intrinsics.ppx,
            intrinsics.ppy,
        )

        print(f"RealSense ready: fx={intrinsics.fx:.1f}, fy={intrinsics.fy:.1f}")

    def _configure_depth_sensor(self, depth_sensor):
        if depth_sensor.supports(rs.option.visual_preset):
            try:
                depth_sensor.set_option(
                    rs.option.visual_preset,
                    int(rs.rs400_visual_preset.high_density),
                )
                print("Visual preset: HIGH_DENSITY")
            except Exception as error:
                print("Could not set HIGH_DENSITY preset:", error)

        if depth_sensor.supports(rs.option.emitter_enabled):
            try:
                depth_sensor.set_option(rs.option.emitter_enabled, 1)
                print("Emitter enabled.")
            except Exception as error:
                print("Could not enable emitter:", error)

        if depth_sensor.supports(rs.option.laser_power):
            try:
                laser_range = depth_sensor.get_option_range(rs.option.laser_power)
                depth_sensor.set_option(rs.option.laser_power, laser_range.max)
                print("Laser power set to max:", laser_range.max)
            except Exception as error:
                print("Could not set laser power:", error)

    def stop(self):
        if self.pipeline is not None:
            self.pipeline.stop()
            print("\nRealSense stopped.")

    def get_aligned_frame(self):
        frames = self.pipeline.wait_for_frames()
        aligned_frames = self.align.process(frames)

        depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()

        if not depth_frame or not color_frame:
            return None, None, None

        depth_image = np.asanyarray(depth_frame.get_data())
        color_image_rgb = np.asanyarray(color_frame.get_data())

        return depth_frame, color_image_rgb, depth_image

    def make_rgbd(self, color_image, depth_image):
        color_o3d = o3d.geometry.Image(color_image.astype(np.uint8))
        depth_o3d = o3d.geometry.Image(depth_image.astype(np.uint16))

        return o3d.geometry.RGBDImage.create_from_color_and_depth(
            color_o3d,
            depth_o3d,
            depth_scale=1.0 / self.depth_scale,
            depth_trunc=self.config.DEPTH_TRUNC_MAX,
            convert_rgb_to_intensity=False,
        )

    def capture_stable_pointcloud(self, frames_to_capture=None):
        if frames_to_capture is None:
            frames_to_capture = self.config.CAPTURE_FRAMES_PER_POSITION

        color_stack = []
        depth_stack = []

        print(f"Capturing {frames_to_capture} frames...")

        for frame_index in range(frames_to_capture):
            frames = self.pipeline.wait_for_frames()
            aligned_frames = self.align.process(frames)

            depth_frame = aligned_frames.get_depth_frame()
            color_frame = aligned_frames.get_color_frame()

            if not depth_frame or not color_frame:
                print(f"Frame {frame_index + 1}: skipped because depth or color is missing.")
                continue

            depth_frame = self.spatial_filter.process(depth_frame)
            depth_frame = self.temporal_filter.process(depth_frame)
            depth_frame = self.hole_filling_filter.process(depth_frame)

            depth_stack.append(np.asanyarray(depth_frame.get_data()).astype(np.uint16))
            color_stack.append(np.asanyarray(color_frame.get_data()).astype(np.uint8))

            print(f"Frame {frame_index + 1}/{frames_to_capture} captured.")

        if not depth_stack:
            return None

        print("Combining frames into one stable point cloud...")

        depth_median = np.median(np.stack(depth_stack, axis=0), axis=0).astype(np.uint16)
        color_mean = np.mean(np.stack(color_stack, axis=0), axis=0).astype(np.uint8)

        rgbd = self.make_rgbd(color_mean, depth_median)

        point_cloud = o3d.geometry.PointCloud.create_from_rgbd_image(
            rgbd,
            self.intrinsic_o3d,
        )

        if len(point_cloud.points) == 0:
            return None

        return point_cloud
