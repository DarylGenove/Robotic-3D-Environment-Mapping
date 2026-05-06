# Import the sys module so we can modify Python's import/search path.
import sys

# Import time functions for delays and timeout checking.
import time

# Import math functions like radians, sin, cos, ceil, etc.
import math

# Import tools for looping through combinations of values.
import itertools

# Import NumPy for matrix math, arrays, and numerical operations.
import numpy as np

# Add the RoboDK Python folder to Python's module search path
# so imports like robolink and robomath can be found.
sys.path.append("C:/RoboDK/Python")

# Import everything from RoboDK's main robot-linking API.
from robodk.robolink import *

# Import a helper that converts XYZ + rotation values into a RoboDK pose.
from robodk.robomath import TxyzRxyz_2_Pose

# Import the Intel RealSense SDK Python library.
import pyrealsense2 as rs

# Import Open3D for point cloud creation, filtering, visualization, and geometry work.
import open3d as o3d


# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

# Transform from robot TCP (tool center point) to the camera mount.
# Format: [x, y, z, rx, ry, rz] in mm and degrees.
TCP_TO_CAMERA_MOUNT     = [0, 0, 43,  0, 0,   0]   # mm / deg

# Transform from the camera mount frame to the optical frame of the camera.
CAMERA_MOUNT_TO_OPTICAL = [0, 0,  0,  0, 0, -90]

# RealSense color/depth stream width in pixels.
RS_WIDTH  = 848

# RealSense color/depth stream height in pixels.
RS_HEIGHT = 480

# Frames per second for the RealSense streams.
RS_FPS    = 30

# Extra wait time after robot movement so vibrations can settle.
SETTLE_TIME               = 1.5

# Maximum time to wait for robot movement to finish.
MOVE_TIMEOUT_SEC          = 30.0

# Time between robot status checks while waiting.
POLL_INTERVAL_SEC         = 0.1

# Number of frames to ignore at startup so the camera can warm up.
WARMUP_FRAMES             = 30

# Number of frames to capture per scan position and combine into one stable result.
CAPTURE_FRAMES_PER_TARGET = 10

# Define the 3D scanning area limits in meters.
ROOM_BOUNDS = {
    "x": (-4.0,  4.0),   # Minimum and maximum X coordinates.
    "y": (-4.0,  4.0),   # Minimum and maximum Y coordinates.
    "z": (-0.5,  3.0),   # Minimum and maximum Z coordinates.
}

# Size of each voxel cell in meters for the occupancy/observation map.
VOXEL_SIZE         = 0.10

# Maximum depth distance to keep from the RealSense camera in meters.
DEPTH_TRUNC        = 6.0

# Voxel size for downsampling captured surface point clouds.
SURFACE_VOXEL_SIZE = 0.005

# Candidate robot joint 1 values for Next Best View planning.
NBV_J1_STEPS = list(range(0, 360, 30))

# Candidate robot joint 5 values for Next Best View planning.
NBV_J5_STEPS = [-60, -30, 0, 30]

# Fixed value for joint 2 in candidate scan poses.
NBV_J2       = 0.0

# Fixed value for joint 3 in candidate scan poses.
NBV_J3       = 90.0

# Fixed value for joint 4 in candidate scan poses.
NBV_J4       = 0.0

# Fixed value for joint 6 in candidate scan poses.
NBV_J6       = 0.0

# Weight used for rewarding expected information gain in scoring.
W_INFO_GAIN = 1.0

# Weight used for penalizing robot travel distance in scoring.
W_TRAVEL    = 0.25

# Weight used for penalizing looking at already-seen areas.
W_REVISIT   = 0.35

# Camera horizontal field of view in degrees.
CAM_HFOV_DEG  = 87.0

# Camera vertical field of view in degrees.
CAM_VFOV_DEG  = 58.0

# Number of ray directions per dimension when simulating FOV.
RAY_SUBSAMPLE = 10

# Stop if observed voxel coverage reaches this fraction.
OBSERVED_COVERAGE_THRESHOLD = 0.88

# Minimum predicted information gain required to accept a new candidate pose.
MIN_INFO_GAIN              = 60

# Minimum actual number of newly observed voxels to consider a scan useful.
MIN_ACTUAL_NEW_OBSERVED    = 120

# Stop after this many low-gain scans in a row.
LOW_GAIN_STREAK_LIMIT      = 3

# Hard limit on number of scans.
MAX_SCANS                  = 40

# File path where the raw merged point cloud will be saved.
OUTPUT_RAW_FILE     = "C:/Users/daryl/Desktop/combined_pointcloud_raw.pcd"

# File path where the leveled/floor-aligned point cloud will be saved.
OUTPUT_LEVELED_FILE = "C:/Users/daryl/Desktop/combined_pointcloud_leveled.pcd"

# Number of neighbors used for statistical outlier removal.
OUTLIER_NB_NEIGHBORS = 20

# Standard deviation ratio used for statistical outlier removal.
OUTLIER_STD_RATIO    = 2.0

# Radius used when estimating normals on the point cloud.
NORMAL_RADIUS        = 0.02

# Maximum nearest neighbors used during normal estimation.
NORMAL_MAX_NN        = 30

# Whether to detect the floor plane and level the final cloud.
LEVEL_FINAL_CLOUD          = True

# Distance threshold for RANSAC plane detection.
PLANE_DISTANCE_THRESHOLD   = 0.02

# Number of points sampled per RANSAC plane iteration.
PLANE_RANSAC_N             = 3

# Number of RANSAC iterations for plane fitting.
PLANE_NUM_ITERATIONS       = 3000

# Maximum number of planes to test when trying to find the floor.
MAX_PLANES_TO_CHECK        = 6

# Minimum number of inlier points for a plane to be considered valid.
MIN_PLANE_POINTS           = 1500

# Minimum dot product with global up vector to consider a plane horizontal enough.
HORIZONTAL_NORMAL_MIN_DOT  = 0.75

# Whether to show the raw point cloud in an Open3D viewer.
SHOW_RAW_CLOUD             = False

# Whether to show the leveled point cloud in an Open3D viewer.
SHOW_LEVELED_CLOUD         = True


# ─────────────────────────────────────────────────────────────────────────────
# VOXEL MAP
# ─────────────────────────────────────────────────────────────────────────────

# Define a class that stores the room as a 3D voxel grid.
class VoxelMap:
    # Constant meaning a voxel has not been observed yet.
    UNKNOWN = 0

    # Constant meaning a voxel is free/empty space.
    FREE    = 1

    # Constant meaning a voxel contains a seen surface.
    SEEN    = 2

    # Constructor: create the voxel grid using bounds and voxel size.
    def __init__(self, bounds, voxel_size):
        # Store the voxel size.
        self.vs = voxel_size

        # Store X coordinate bounds.
        self.bx = bounds["x"]

        # Store Y coordinate bounds.
        self.by = bounds["y"]

        # Store Z coordinate bounds.
        self.bz = bounds["z"]

        # Compute number of voxels along X.
        self.nx = math.ceil((self.bx[1] - self.bx[0]) / self.vs)

        # Compute number of voxels along Y.
        self.ny = math.ceil((self.by[1] - self.by[0]) / self.vs)

        # Compute number of voxels along Z.
        self.nz = math.ceil((self.bz[1] - self.bz[0]) / self.vs)

        # Create the 3D voxel grid, initially all UNKNOWN.
        self.grid = np.zeros((self.nx, self.ny, self.nz), dtype=np.uint8)

        # Print a summary of the voxel map size.
        print(
            f"Voxel map: {self.nx}×{self.ny}×{self.nz} = "
            f"{self.nx * self.ny * self.nz:,} cells at {voxel_size*100:.0f} cm"
        )

    # Convert one 3D world point into one voxel index.
    def world_to_idx_single(self, pt):
        # Compute X voxel index from world X.
        ix = int((pt[0] - self.bx[0]) / self.vs)

        # Compute Y voxel index from world Y.
        iy = int((pt[1] - self.by[0]) / self.vs)

        # Compute Z voxel index from world Z.
        iz = int((pt[2] - self.bz[0]) / self.vs)

        # Return voxel indices as a tuple.
        return ix, iy, iz

    # Convert an array of world points into voxel indices.
    def world_to_idx_array(self, pts_world):
        # Compute all X indices.
        ix = ((pts_world[:, 0] - self.bx[0]) / self.vs).astype(int)

        # Compute all Y indices.
        iy = ((pts_world[:, 1] - self.by[0]) / self.vs).astype(int)

        # Compute all Z indices.
        iz = ((pts_world[:, 2] - self.bz[0]) / self.vs).astype(int)

        # Combine X, Y, Z indices into one Nx3 array.
        return np.stack([ix, iy, iz], axis=1)

    # Return a mask telling which indices are inside the voxel grid.
    def valid_mask(self, idx):
        # Check lower and upper bounds for all three coordinates.
        return (
            (idx[:, 0] >= 0) & (idx[:, 0] < self.nx) &
            (idx[:, 1] >= 0) & (idx[:, 1] < self.ny) &
            (idx[:, 2] >= 0) & (idx[:, 2] < self.nz)
        )

    # Check whether one voxel index triplet is inside the map bounds.
    def idx_in_bounds(self, ix, iy, iz):
        # Return True only if all indices are inside valid ranges.
        return (
            0 <= ix < self.nx and
            0 <= iy < self.ny and
            0 <= iz < self.nz
        )

    # Compute how much of the voxel map has been observed (FREE or SEEN).
    def coverage_observed(self):
        # Count how many voxels are not UNKNOWN.
        observed = np.count_nonzero(self.grid != self.UNKNOWN)

        # Return observed fraction.
        return observed / self.grid.size

    # Count how many voxels are still UNKNOWN.
    def n_unknown(self):
        # Return count of unknown voxels.
        return np.count_nonzero(self.grid == self.UNKNOWN)

    # Count how many voxels are observed (FREE or SEEN).
    def n_observed(self):
        # Return count of non-unknown voxels.
        return np.count_nonzero(self.grid != self.UNKNOWN)

    # Count how many voxels are marked as SEEN surfaces.
    def n_seen(self):
        # Return count of seen surface voxels.
        return np.count_nonzero(self.grid == self.SEEN)

    # Simulate the camera field of view from a given position and orientation
    # to estimate how many unknown and seen voxels would be intersected.
    def simulate_fov(self, cam_pos_world, cam_rot_world,
                     hfov_deg=CAM_HFOV_DEG, vfov_deg=CAM_VFOV_DEG,
                     n_rays=RAY_SUBSAMPLE, max_range=DEPTH_TRUNC):
        # Convert half horizontal FOV to radians.
        hfov = math.radians(hfov_deg / 2.0)

        # Convert half vertical FOV to radians.
        vfov = math.radians(vfov_deg / 2.0)

        # Create evenly spaced horizontal ray angles.
        h_angles = np.linspace(-hfov, hfov, n_rays)

        # Create evenly spaced vertical ray angles.
        v_angles = np.linspace(-vfov, vfov, n_rays)

        # Store unique unknown voxels hit by rays.
        unknown_hit = set()

        # Store unique already-seen voxels hit by rays.
        seen_hit    = set()

        # Define marching step size along each ray.
        step = self.vs * 0.8

        # Loop through every horizontal/vertical ray combination.
        for h, v in itertools.product(h_angles, v_angles):
            # Build a ray direction in camera coordinates.
            d_cam = np.array([
                math.sin(h) * math.cos(v),
                math.sin(v),
                math.cos(h) * math.cos(v),
            ], dtype=np.float64)

            # Rotate the ray direction into world coordinates.
            d_world = cam_rot_world @ d_cam

            # Normalize the world ray direction.
            d_world /= np.linalg.norm(d_world)

            # March along the ray until max range.
            for t in np.arange(step, max_range, step):
                # Compute a world point along the ray.
                pt = cam_pos_world + t * d_world

                # Convert that world point to voxel indices.
                ix, iy, iz = self.world_to_idx_single(pt)

                # Stop if the ray leaves the voxel map.
                if not self.idx_in_bounds(ix, iy, iz):
                    break

                # Read voxel state at this cell.
                state = self.grid[ix, iy, iz]

                # Create a hashable key for the voxel.
                key = (ix, iy, iz)

                # If unknown, record it as potentially new information.
                if state == self.UNKNOWN:
                    unknown_hit.add(key)

                # If already seen surface, record revisit and stop ray.
                elif state == self.SEEN:
                    seen_hit.add(key)
                    break

        # Return counts of unique unknown and seen voxels reached.
        return len(unknown_hit), len(seen_hit)

    # Integrate a point cloud into the voxel map by ray-tracing from the camera position
    # to each point to mark FREE space and SEEN surface cells.
    def integrate_pointcloud_with_rays(self, pcd_world, cam_pos_world, ray_stride=8):
        # If point cloud is empty, nothing to integrate.
        if len(pcd_world.points) == 0:
            return 0, 0

        # Convert point cloud points into a NumPy array.
        pts = np.asarray(pcd_world.points)

        # Optionally use only every Nth point to reduce computation.
        if ray_stride > 1:
            pts = pts[::ray_stride]

        # Counter for newly observed voxels (FREE or first-time SEEN).
        new_observed = 0

        # Counter for newly seen surface voxels.
        new_seen = 0

        # Define marching step size for ray traversal.
        step = self.vs * 0.8

        # Process each point in the point cloud.
        for pt in pts:
            # Vector from camera to point.
            vec = pt - cam_pos_world

            # Distance from camera to point.
            dist = np.linalg.norm(vec)

            # Skip invalid/too-close/too-far points.
            if dist < 1e-6 or dist > DEPTH_TRUNC:
                continue

            # Normalize direction from camera to point.
            direction = vec / dist

            # March from camera toward the point to mark FREE space.
            for t in np.arange(step, max(0.0, dist - step), step):
                # Compute sample point along the ray.
                sample = cam_pos_world + t * direction

                # Convert sample point into voxel index.
                ix, iy, iz = self.world_to_idx_single(sample)

                # Stop if ray leaves voxel map.
                if not self.idx_in_bounds(ix, iy, iz):
                    break

                # If still unknown, mark this voxel as free/empty.
                if self.grid[ix, iy, iz] == self.UNKNOWN:
                    self.grid[ix, iy, iz] = self.FREE
                    new_observed += 1

            # Convert the final surface point to voxel index.
            ix, iy, iz = self.world_to_idx_single(pt)

            # If surface voxel is inside bounds, update it.
            if self.idx_in_bounds(ix, iy, iz):
                # If it was unknown, it is now both observed and seen.
                if self.grid[ix, iy, iz] == self.UNKNOWN:
                    new_observed += 1
                    new_seen += 1

                # If it was free, turning it into seen adds one seen voxel.
                elif self.grid[ix, iy, iz] == self.FREE:
                    new_seen += 1

                # Mark final voxel as a seen surface.
                self.grid[ix, iy, iz] = self.SEEN

        # Return counts of newly observed and newly seen voxels.
        return new_observed, new_seen


# ─────────────────────────────────────────────────────────────────────────────
# NBV PLANNER
# ─────────────────────────────────────────────────────────────────────────────

# Define a class that selects the Next Best View (NBV) for scanning.
class NBVPlanner:
    # Constructor: store dependencies and generate candidate joint poses.
    def __init__(self, voxel_map, robot, rdk,
                 T_tcp_mount, T_mount_optical,
                 j1_steps=NBV_J1_STEPS, j5_steps=NBV_J5_STEPS,
                 j2=NBV_J2, j3=NBV_J3, j4=NBV_J4, j6=NBV_J6):
        # Store the voxel map.
        self.vmap        = voxel_map

        # Store the robot item.
        self.robot       = robot

        # Store the RoboDK link.
        self.rdk         = rdk

        # Store transform from TCP to camera mount.
        self.T_tcp_mount = T_tcp_mount

        # Store transform from mount to optical frame.
        self.T_mount_opt = T_mount_optical

        # Prepare a list to hold all candidate joint configurations.
        self.candidates = []

        # Create candidate poses by combining J1 and J5 values while others stay fixed.
        for j1 in j1_steps:
            for j5 in j5_steps:
                self.candidates.append([float(j1), float(j2), float(j3), float(j4), float(j5), float(j6)])

        # Keep track of candidates already used so they are not selected again.
        self.used_indices = set()

        # Print how many candidate poses were generated.
        print(f"NBV candidate pool: {len(self.candidates)} poses")

    # Compute forward kinematics for a joint pose and return camera pose in base frame.
    def _fk(self, joints_deg):
        # Solve forward kinematics using RoboDK.
        mat = self.robot.SolveFK(joints_deg)

        # Convert RoboDK matrix to a 4x4 NumPy matrix.
        T_base_tcp = robodk_mat_to_numpy(mat)

        # Return base-to-camera transform by chaining TCP->mount and mount->optical transforms.
        return T_base_tcp @ self.T_tcp_mount @ self.T_mount_opt

    # Score one candidate pose using predicted info gain, travel cost, and revisit penalty.
    def _score(self, joints, current_joints):
        # Compute camera transform for this candidate.
        T_cam = self._fk(joints)

        # Extract camera position.
        cam_pos = T_cam[:3, 3]

        # Extract camera rotation matrix.
        cam_rot = T_cam[:3, :3]

        # Simulate field of view to estimate unknown and already-seen voxels.
        unknown, seen = self.vmap.simulate_fov(cam_pos, cam_rot)

        # Compute simple travel cost as sum of absolute joint changes.
        travel = sum(abs(a - b) for a, b in zip(joints, current_joints))

        # Compute total score:
        # more unknown is better,
        # more travel is worse,
        # more revisiting seen areas is worse.
        score = (
            W_INFO_GAIN * unknown
            - W_TRAVEL * travel
            - W_REVISIT * seen
        )

        # Return score and predicted unknown gain.
        return score, unknown

    # Pick the next best unused candidate pose.
    def pick_next(self, current_joints):
        # Start with worst possible score.
        best_score = -np.inf

        # Placeholder for best candidate joints.
        best_joints = None

        # Placeholder for best predicted gain.
        best_gain = 0

        # Placeholder for best candidate index.
        best_index = None

        # Evaluate every candidate.
        for i, cand in enumerate(self.candidates):
            # Skip candidates already used before.
            if i in self.used_indices:
                continue

            # Try to score candidate. Skip if any error occurs.
            try:
                score, gain = self._score(cand, current_joints)
            except Exception:
                continue

            # Update best candidate if this one scores higher.
            if score > best_score:
                best_score = score
                best_joints = cand
                best_gain = gain
                best_index = i

        # If no good candidate found or gain is too low, return None.
        if best_joints is None or best_gain < MIN_INFO_GAIN:
            return None, best_gain

        # Mark chosen candidate as used.
        self.used_indices.add(best_index)

        # Return best candidate and its predicted gain.
        return best_joints, best_gain


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

# Convert a RoboDK pose matrix into a 4x4 NumPy transform matrix.
def robodk_mat_to_numpy(mat):
    # Start with identity matrix.
    arr = np.eye(4, dtype=np.float64)

    # Copy rotation and translation from RoboDK matrix.
    for r in range(3):
        # Copy the 3x3 rotation part.
        for c in range(3):
            arr[r, c] = mat[r, c]

        # Copy translation, converting mm to meters.
        arr[r, 3] = mat[r, 3] / 1000.0

    # Return NumPy transform matrix.
    return arr

# Convert [x, y, z, rx, ry, rz] pose values into a 4x4 NumPy transform.
def xyzrxryrz_to_numpy(pose_values):
    # Convert pose values into a RoboDK pose,
    # converting rotations from degrees to radians.
    pose = TxyzRxyz_2_Pose([
        pose_values[0], pose_values[1], pose_values[2],
        np.radians(pose_values[3]),
        np.radians(pose_values[4]),
        np.radians(pose_values[5]),
    ])

    # Convert RoboDK pose to NumPy 4x4 matrix.
    return robodk_mat_to_numpy(pose)

# Convert various possible joint containers into a regular Python list.
def joints_to_list(joints_mat):
    # Try RoboDK's .list() method first.
    try:
        return list(joints_mat.list())

    # If that fails, try direct list conversion.
    except Exception:
        try:
            return list(joints_mat)

        # If that also fails, build the list manually.
        except Exception:
            return [joints_mat[i] for i in range(len(joints_mat))]

# Connect to the real robot through RoboDK.
def connect_robot(robot, rdk):
    # Switch RoboDK to real robot execution mode.
    rdk.setRunMode(RUNMODE_RUN_ROBOT)

    # Attempt a safe connection to the robot.
    status = robot.ConnectSafe()

    # Print the returned connection status.
    print("ConnectSafe status:", status)

    # If robot is not ready, stop with an error.
    if status != ROBOTCOM_READY:
        raise Exception("Robot not READY. Check connection settings.")

# Wait until the robot is no longer busy/moving.
def wait_until_robot_stops(robot, timeout_sec=MOVE_TIMEOUT_SEC):
    # Record the start time.
    start = time.time()

    # Poll until robot reports it is no longer busy.
    while True:
        try:
            # If robot is not busy, movement is complete.
            if not robot.Busy():
                return
        except Exception:
            # Ignore temporary status-reading errors.
            pass

        # If timeout is exceeded, stop with an error.
        if time.time() - start > timeout_sec:
            raise Exception("Timeout waiting for robot to stop.")

        # Wait briefly before polling again.
        time.sleep(POLL_INTERVAL_SEC)

# Read current robot joints, retrying briefly if needed.
def get_robot_joints_when_ready(robot, timeout_sec=5.0):
    # Record the start time.
    start = time.time()

    # Keep trying until joints are available or timeout happens.
    while True:
        try:
            # Read robot joints and convert them to a Python list.
            return joints_to_list(robot.Joints())
        except Exception:
            # If timeout is exceeded, raise an error.
            if time.time() - start > timeout_sec:
                raise Exception("Could not read robot joints.")

            # Wait briefly and try again.
            time.sleep(POLL_INTERVAL_SEC)

# Move robot to a joint target and wait until it has settled.
def move_robot_and_wait(robot, rdk, joints_deg, label=""):
    # Create a temporary target in RoboDK.
    target = rdk.AddTarget(f"_nbv_{label}")

    # Mark this target as a joint-space target.
    target.setAsJointTarget()

    # Set the target's joint values.
    target.setJoints(joints_deg)

    # Print where the robot is moving.
    print(f"  Moving to {label}: J={[round(j, 1) for j in joints_deg]}")

    # Start joint movement without blocking Python execution.
    robot.MoveJ(target, blocking=False)

    # Wait until robot motion is finished.
    wait_until_robot_stops(robot)

    # Delete the temporary RoboDK target.
    target.Delete()

    # Print arrival message and wait a bit for vibrations to settle.
    print(f"  Arrived. Settling {SETTLE_TIME:.1f}s...")
    time.sleep(SETTLE_TIME)

    # Return the actual robot joints after motion.
    return get_robot_joints_when_ready(robot)

# Create an Open3D RGBD image from color and depth images.
def make_rgbd(color_image, depth_image, depth_scale_value):
    # Convert NumPy color image to Open3D image type.
    color_o3d = o3d.geometry.Image(color_image.astype(np.uint8))

    # Convert NumPy depth image to Open3D image type.
    depth_o3d = o3d.geometry.Image(depth_image.astype(np.uint16))

    # Create and return an Open3D RGBD image.
    return o3d.geometry.RGBDImage.create_from_color_and_depth(
        color_o3d,
        depth_o3d,
        depth_scale=1.0 / depth_scale_value,
        depth_trunc=DEPTH_TRUNC,
        convert_rgb_to_intensity=False,
    )

# Capture multiple frames and combine them into one more stable point cloud.
def capture_stable_pointcloud(pipeline, align, intrinsic_o3d,
                              depth_scale_value,
                              frames_to_average=CAPTURE_FRAMES_PER_TARGET):
    # List to store captured color frames.
    color_stack = []

    # List to store captured depth frames.
    depth_stack = []

    # Capture several frames for averaging/median filtering.
    for _ in range(frames_to_average):
        # Wait for a new frameset from the camera.
        frames = pipeline.wait_for_frames()

        # Align depth to the color stream.
        aligned_frames = align.process(frames)

        # Extract aligned depth frame.
        depth_frame = aligned_frames.get_depth_frame()

        # Extract aligned color frame.
        color_frame = aligned_frames.get_color_frame()

        # Skip frame if either depth or color is missing.
        if not depth_frame or not color_frame:
            continue

        # Add depth frame to the stack as uint16 NumPy array.
        depth_stack.append(np.asanyarray(depth_frame.get_data()).astype(np.uint16))

        # Add color frame to the stack as uint8 NumPy array.
        color_stack.append(np.asanyarray(color_frame.get_data()).astype(np.uint8))

    # If no valid frames were collected, return None.
    if not depth_stack:
        return None

    # Compute median depth image to reduce noise/outliers.
    depth_median = np.median(np.stack(depth_stack, axis=0), axis=0).astype(np.uint16)

    # Compute mean color image.
    color_mean = np.mean(np.stack(color_stack, axis=0), axis=0).astype(np.uint8)

    # Build an RGBD image from the combined color/depth images.
    rgbd = make_rgbd(color_mean, depth_median, depth_scale_value)

    # Create a point cloud from the RGBD image using camera intrinsics.
    pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd, intrinsic_o3d)

    # Return the point cloud only if it contains points.
    return pcd if len(pcd.points) > 0 else None

# Compute a rotation matrix that rotates one vector onto another.
def rotation_matrix_from_vectors(vec_from, vec_to):
    # Normalize source vector.
    a = vec_from / np.linalg.norm(vec_from)

    # Normalize target vector.
    b = vec_to / np.linalg.norm(vec_to)

    # Compute cross product between vectors.
    cross = np.cross(a, b)

    # Compute clamped dot product between vectors.
    dot = np.clip(np.dot(a, b), -1.0, 1.0)

    # If vectors are already aligned, return identity matrix.
    if np.isclose(dot, 1.0):
        return np.eye(3)

    # If vectors are opposite, rotate 180 degrees around a perpendicular axis.
    if np.isclose(dot, -1.0):
        # Start with X axis as candidate rotation axis.
        axis = np.array([1.0, 0.0, 0.0])

        # If too parallel to source vector, use Y axis instead.
        if abs(a[0]) > 0.9:
            axis = np.array([0.0, 1.0, 0.0])

        # Remove component parallel to source vector.
        axis = axis - a * np.dot(axis, a)

        # Normalize axis.
        axis = axis / np.linalg.norm(axis)

        # Build skew-symmetric cross-product matrix.
        K = np.array([
            [0.0, -axis[2], axis[1]],
            [axis[2], 0.0, -axis[0]],
            [-axis[1], axis[0], 0.0],
        ])

        # For 180-degree rotation, use I + 2*K^2.
        return np.eye(3) + 2.0 * (K @ K)

    # Compute sine magnitude from cross product length.
    s = np.linalg.norm(cross)

    # Build skew-symmetric matrix from cross product.
    K = np.array([
        [0.0, -cross[2], cross[1]],
        [cross[2], 0.0, -cross[0]],
        [-cross[1], cross[0], 0.0],
    ])

    # Use Rodrigues' rotation formula to compute rotation matrix.
    R = np.eye(3) + K + (K @ K) * ((1.0 - dot) / (s ** 2))

    # Return rotation matrix.
    return R

# Search for the best horizontal plane in the point cloud, assumed to be the floor.
def find_floor_plane(pcd):
    # Start with the full point cloud as remaining data.
    remaining = pcd

    # Best floor candidate found so far.
    best = None

    # Try extracting up to a fixed number of planes.
    for plane_idx in range(MAX_PLANES_TO_CHECK):
        # Stop if too few points remain.
        if len(remaining.points) < MIN_PLANE_POINTS:
            break

        # Segment the dominant plane from the remaining cloud using RANSAC.
        plane_model, inliers = remaining.segment_plane(
            distance_threshold=PLANE_DISTANCE_THRESHOLD,
            ransac_n=PLANE_RANSAC_N,
            num_iterations=PLANE_NUM_ITERATIONS,
        )

        # Stop if the detected plane has too few inliers.
        if len(inliers) < MIN_PLANE_POINTS:
            break

        # Unpack plane coefficients a*x + b*y + c*z + d = 0.
        a, b, c, d = plane_model

        # Build plane normal vector.
        normal = np.array([a, b, c], dtype=np.float64)

        # Normalize the plane normal.
        normal = normal / np.linalg.norm(normal)

        # Extract the inlier points of this plane.
        inlier_cloud = remaining.select_by_index(inliers)

        # Convert inlier points to NumPy array.
        pts = np.asarray(inlier_cloud.points)

        # Compute plane centroid.
        centroid = pts.mean(axis=0)

        # Measure how horizontal the plane is by dotting with global Z axis.
        horizontal_score = abs(np.dot(normal, np.array([0.0, 0.0, 1.0])))

        # Print diagnostic information for this plane.
        print(
            f"Plane {plane_idx + 1}: "
            f"points={len(inliers):,}, "
            f"normal={np.round(normal, 4)}, "
            f"centroid={np.round(centroid, 4)}, "
            f"horizontal_score={horizontal_score:.3f}"
        )

        # Keep only sufficiently horizontal planes as floor candidates.
        if horizontal_score >= HORIZONTAL_NORMAL_MIN_DOT:
            # Build a candidate record for this plane.
            candidate = {
                "plane_model": plane_model,
                "normal": normal,
                "centroid": centroid,
                "inliers": inliers,
                "score": horizontal_score,
                "n_points": len(inliers),
            }

            # If no best plane yet, take this one.
            if best is None:
                best = candidate
            else:
                # Prefer the lower plane in Z, assuming the floor is lowest.
                if centroid[2] < best["centroid"][2]:
                    best = candidate

        # Remove this plane and continue searching remaining points.
        remaining = remaining.select_by_index(inliers, invert=True)

    # Return the best detected floor candidate, or None if not found.
    return best

# Rotate and translate the point cloud so the floor becomes flat at z=0.
def level_pointcloud_to_floor(pcd):
    # Find the floor plane.
    floor = find_floor_plane(pcd)

    # If no suitable floor found, raise an error.
    if floor is None:
        raise Exception("Could not find a suitable horizontal floor plane for leveling.")

    # Copy the detected floor normal.
    floor_normal = floor["normal"].copy()

    # Copy the detected floor centroid.
    floor_centroid = floor["centroid"].copy()

    # Flip normal upward if it points downward.
    if floor_normal[2] < 0.0:
        floor_normal = -floor_normal

    # Define the desired global up direction.
    target_up = np.array([0.0, 0.0, 1.0], dtype=np.float64)

    # Compute rotation that aligns floor normal with global up.
    R = rotation_matrix_from_vectors(floor_normal, target_up)

    # Create a copy of the input point cloud.
    leveled = o3d.geometry.PointCloud(pcd)

    # Rotate the point cloud around the origin.
    leveled.rotate(R, center=(0.0, 0.0, 0.0))

    # Rotate the floor centroid too.
    rotated_floor_centroid = R @ floor_centroid

    # Translate cloud so floor centroid lies on z=0.
    leveled.translate((0.0, 0.0, -rotated_floor_centroid[2]))

    # Build the full 4x4 leveling transform matrix.
    transform = np.eye(4, dtype=np.float64)

    # Store rotation part.
    transform[:3, :3] = R

    # Store translation part.
    transform[:3, 3] = [0.0, 0.0, -rotated_floor_centroid[2]]

    # Return leveled cloud, applied transform, and floor info.
    return leveled, transform, floor


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

# Main entry point of the script.
def main():
    # Create a RoboDK API link.
    RDK = Robolink()

    # Ask the user to select a robot from RoboDK.
    robot = RDK.ItemUserPick("Select your robot", ITEM_TYPE_ROBOT)

    # Stop if no valid robot was selected.
    if not robot.Valid():
        raise Exception("Robot not selected.")

    # Print selected robot name.
    print("Robot:", robot.Name())

    # Connect to the selected robot.
    connect_robot(robot, RDK)

    # Convert TCP-to-camera-mount transform into NumPy matrix.
    T_tcp_mount = xyzrxryrz_to_numpy(TCP_TO_CAMERA_MOUNT)

    # Convert mount-to-optical transform into NumPy matrix.
    T_mount_optical = xyzrxryrz_to_numpy(CAMERA_MOUNT_TO_OPTICAL)

    # Print RealSense startup message.
    print("\nStarting RealSense D455f...")

    # Create a RealSense pipeline object.
    pipeline = rs.pipeline()

    # Create a RealSense configuration object.
    config = rs.config()

    # Enable depth stream with chosen resolution, format, and FPS.
    config.enable_stream(rs.stream.depth, RS_WIDTH, RS_HEIGHT, rs.format.z16, RS_FPS)

    # Enable color stream with chosen resolution, format, and FPS.
    config.enable_stream(rs.stream.color, RS_WIDTH, RS_HEIGHT, rs.format.rgb8, RS_FPS)

    # Start the RealSense pipeline.
    profile = pipeline.start(config)

    # Get the first depth sensor from the connected device.
    depth_sensor = profile.get_device().first_depth_sensor()

    # If the sensor supports visual presets, try to set HIGH_ACCURACY.
    if depth_sensor.supports(rs.option.visual_preset):
        try:
            depth_sensor.set_option(
                rs.option.visual_preset,
                int(rs.rs400_visual_preset.high_accuracy)
            )
            print("Visual preset: HIGH_ACCURACY")
        except Exception as e:
            print("Could not set HIGH_ACCURACY preset:", e)

    # Try to maximize laser power if supported.
    try:
        if depth_sensor.supports(rs.option.laser_power):
            laser_max = depth_sensor.get_option_range(rs.option.laser_power).max
            depth_sensor.set_option(rs.option.laser_power, laser_max)
            print("Laser power set to max:", laser_max)
    except Exception as e:
        print("Could not set laser power:", e)

    # Read the depth scale from the sensor.
    depth_scale = depth_sensor.get_depth_scale()

    # Print depth scale.
    print("Depth scale:", depth_scale)

    # Create an align object to align depth to color.
    align = rs.align(rs.stream.color)

    # Warm up the camera by discarding some initial frames.
    print(f"Warming up ({WARMUP_FRAMES} frames)...")
    for _ in range(WARMUP_FRAMES):
        pipeline.wait_for_frames()

    # Get the color stream profile.
    color_stream = profile.get_stream(rs.stream.color).as_video_stream_profile()

    # Read camera intrinsics from the color stream.
    intrinsics = color_stream.get_intrinsics()

    # Build Open3D camera intrinsics object.
    intrinsic_o3d = o3d.camera.PinholeCameraIntrinsic(
        intrinsics.width,
        intrinsics.height,
        intrinsics.fx,
        intrinsics.fy,
        intrinsics.ppx,
        intrinsics.ppy,
    )

    # Print focal lengths for confirmation.
    print(f"RealSense ready: fx={intrinsics.fx:.1f} fy={intrinsics.fy:.1f}")

    # Create the voxel map that tracks observed/free/seen space.
    vmap = VoxelMap(ROOM_BOUNDS, VOXEL_SIZE)

    # Create the Next Best View planner.
    planner = NBVPlanner(vmap, robot, RDK, T_tcp_mount, T_mount_optical)

    # Create an empty point cloud to accumulate all scans.
    combined_pcd = o3d.geometry.PointCloud()

    # Counter for successful scans.
    scan_count = 0

    # Counter for skipped scans.
    skip_count = 0

    # Counter for consecutive low-gain scans.
    low_gain_streak = 0

    # Read the current robot joints.
    current_joints = get_robot_joints_when_ready(robot)

    # Print start banner.
    print("\n" + "=" * 60)
    print("Autonomous NBV scanning started.")
    print(f"  Observed coverage target : {OBSERVED_COVERAGE_THRESHOLD*100:.0f}%")
    print(f"  Min predicted info gain  : {MIN_INFO_GAIN}")
    print(f"  Min actual new observed  : {MIN_ACTUAL_NEW_OBSERVED}")
    print(f"  Low gain streak limit    : {LOW_GAIN_STREAK_LIMIT}")
    print(f"  Max scans                : {MAX_SCANS}")
    print("=" * 60 + "\n")

    # Main scanning loop.
    try:
        # Continue until max number of scans is reached.
        while scan_count < MAX_SCANS:
            # Compute current observed coverage.
            coverage = vmap.coverage_observed()

            # Print current coverage and voxel statistics.
            print(
                f"Observed coverage: {coverage*100:.1f}%"
                f"  |  Observed voxels: {vmap.n_observed():,}"
                f"  |  Surface voxels: {vmap.n_seen():,}"
                f"  |  Unknown voxels: {vmap.n_unknown():,}"
            )

            # Stop if enough of the room has been observed.
            if coverage >= OBSERVED_COVERAGE_THRESHOLD:
                print("Observed coverage threshold reached. Done.")
                break

            # Ask planner for the next best robot pose.
            next_joints, expected_gain = planner.pick_next(current_joints)

            # Stop if no valid candidate remains.
            if next_joints is None:
                print(f"No unused candidate offers ≥ {MIN_INFO_GAIN} predicted unknown voxels. Done.")
                break

            # Print scan number and expected gain.
            print(
                f"\n=== Scan {scan_count + 1}/{MAX_SCANS}"
                f"  (predicted gain: {expected_gain} voxels) ==="
            )

            # Ensure RoboDK is in real robot run mode.
            RDK.setRunMode(RUNMODE_RUN_ROBOT)

            # Move robot to selected scan pose and wait.
            actual_joints = move_robot_and_wait(
                robot, RDK, next_joints, label=f"s{scan_count + 1:03d}"
            )

            # Update current joints with actual reached joints.
            current_joints = actual_joints

            # Compute base-to-TCP transform from actual joints.
            T_base_tcp = robodk_mat_to_numpy(robot.SolveFK(actual_joints))

            # Compute base-to-camera transform.
            T_base_cam = T_base_tcp @ T_tcp_mount @ T_mount_optical

            # Extract camera position in world coordinates.
            cam_pos_world = T_base_cam[:3, 3]

            # Capture a stable point cloud at current robot pose.
            pcd = capture_stable_pointcloud(
                pipeline,
                align,
                intrinsic_o3d,
                depth_scale,
                CAPTURE_FRAMES_PER_TARGET,
            )

            # If no valid scan was captured, skip this iteration.
            if pcd is None:
                print("  WARNING: empty scan, skipping.")
                skip_count += 1
                continue

            # Transform point cloud from camera coordinates into robot base/world coordinates.
            pcd.transform(T_base_cam)

            # Downsample point cloud to reduce density.
            pcd = pcd.voxel_down_sample(voxel_size=SURFACE_VOXEL_SIZE)

            # If still non-empty, remove statistical outliers.
            if len(pcd.points) > 0:
                pcd, _ = pcd.remove_statistical_outlier(
                    nb_neighbors=OUTLIER_NB_NEIGHBORS,
                    std_ratio=OUTLIER_STD_RATIO,
                )

            # If point cloud became empty after filtering, skip it.
            if len(pcd.points) == 0:
                print("  WARNING: scan became empty after filtering, skipping.")
                skip_count += 1
                continue

            # Integrate this scan into the voxel map.
            new_observed, new_seen = vmap.integrate_pointcloud_with_rays(
                pcd, cam_pos_world, ray_stride=8
            )

            # Merge current scan into the combined point cloud.
            combined_pcd += pcd

            # Increment successful scan count.
            scan_count += 1

            # Update low-gain streak depending on actual new observed voxels.
            if new_observed < MIN_ACTUAL_NEW_OBSERVED:
                low_gain_streak += 1
            else:
                low_gain_streak = 0

            # Print scan result summary.
            print(
                f"  Captured {len(pcd.points):,} pts"
                f"  |  new observed voxels: {new_observed:,}"
                f"  |  new seen surface voxels: {new_seen:,}"
                f"  |  low gain streak: {low_gain_streak}/{LOW_GAIN_STREAK_LIMIT}"
                f"  |  total pts: {len(combined_pcd.points):,}"
            )

            # Stop if several scans in a row produced low gain.
            if low_gain_streak >= LOW_GAIN_STREAK_LIMIT:
                print("Low-gain stop triggered. Done.")
                break

    # Handle Ctrl+C cleanly.
    except KeyboardInterrupt:
        print("\nInterrupted by user.")

    # Always stop the camera at the end.
    finally:
        pipeline.stop()
        print("\nRealSense stopped.")

    # Print scan summary.
    print(f"\nScanned: {scan_count}  Skipped: {skip_count}")

    # Print total points before final cleanup.
    print(f"Total points before final cleanup: {len(combined_pcd.points):,}")

    # Stop if nothing was captured at all.
    if len(combined_pcd.points) == 0:
        raise Exception("No points captured. Combined cloud is empty.")

    # Remove outliers from the merged point cloud.
    combined_pcd, _ = combined_pcd.remove_statistical_outlier(
        nb_neighbors=OUTLIER_NB_NEIGHBORS,
        std_ratio=OUTLIER_STD_RATIO,
    )

    # Downsample the merged point cloud.
    combined_pcd = combined_pcd.voxel_down_sample(voxel_size=SURFACE_VOXEL_SIZE)

    # Estimate normals on the merged point cloud.
    combined_pcd.estimate_normals(
        search_param=o3d.geometry.KDTreeSearchParamHybrid(
            radius=NORMAL_RADIUS,
            max_nn=NORMAL_MAX_NN,
        )
    )

    # Print final point count after cleanup.
    print(f"After cleanup: {len(combined_pcd.points):,} points")

    # Save raw merged point cloud to disk.
    o3d.io.write_point_cloud(OUTPUT_RAW_FILE, combined_pcd)

    # Print raw file path.
    print("Saved raw cloud to:", OUTPUT_RAW_FILE)

    # Show raw point cloud if enabled.
    if SHOW_RAW_CLOUD:
        o3d.visualization.draw_geometries(
            [combined_pcd],
            window_name=f"Autonomous 3D Scan - Raw ({scan_count} positions)",
        )

    # If leveling is enabled, detect floor and align cloud.
    if LEVEL_FINAL_CLOUD:
        print("\nDetecting floor plane and leveling final point cloud...")

        # Compute leveled point cloud and corresponding transform.
        leveled_pcd, leveling_transform, floor = level_pointcloud_to_floor(combined_pcd)

        # Re-estimate normals on leveled point cloud.
        leveled_pcd.estimate_normals(
            search_param=o3d.geometry.KDTreeSearchParamHybrid(
                radius=NORMAL_RADIUS,
                max_nn=NORMAL_MAX_NN,
            )
        )

        # Print chosen floor plane normal.
        print("Chosen floor plane normal:", np.round(floor["normal"], 6))

        # Print chosen floor plane centroid.
        print("Chosen floor plane centroid:", np.round(floor["centroid"], 6))

        # Print the final leveling transform.
        print("Leveling transform:")
        print(leveling_transform)

        # Save leveled point cloud to disk.
        o3d.io.write_point_cloud(OUTPUT_LEVELED_FILE, leveled_pcd)

        # Print leveled file path.
        print("Saved leveled cloud to:", OUTPUT_LEVELED_FILE)

        # Show leveled cloud if enabled.
        if SHOW_LEVELED_CLOUD:
            o3d.visualization.draw_geometries(
                [leveled_pcd],
                window_name=f"Autonomous 3D Scan - Leveled ({scan_count} positions)",
            )

    # Final done message.
    print("Done!")


# Run main() only if this file is executed directly.
if __name__ == "__main__":
    # Call the main function.
    main()