# Bring in sys so Python can change where it searches for files.
import sys

# Bring in NumPy so the code can do 3D math with numbers.
import numpy as np

# Add this folder so Python can import the needed RoboDK or project files.
sys.path.append("C:/RoboDK/Python")

# Run this line as one small step in the program.
from robodk.robolink import ITEM_TYPE_TARGET

# Bring in TransformUtils so this file can reuse 3D transform helpers.
from transform_utils import TransformUtils


# Create the DebugTargetService class so related code stays together.
class DebugTargetService:
    # Create the setup function that saves the things this object needs.
    def __init__(self, config, rdk):
        # Save a value in config.
        self.config = config
        # Save a value in rdk.
        self.rdk = rdk

    # Create the function that draws helper targets in RoboDK.
    def create_debug_targets(
        # Add this value to the current list or function call.
        self,
        # Add this value to the current list or function call.
        look_points_base,
        # Add this value to the current list or function call.
        camera_position_base,
        # Run this line as one small step in the program.
        tcp_pose_targets
    # Run this line as one small step in the program.
    ):
        # Check this condition before continuing.
        if not self.config.CREATE_DEBUG_TARGETS:
            # Run this line as one small step in the program.
            return

        # Create a marker point in RoboDK.
        self.create_point_marker(
            # Add this value to the current list or function call.
            "NECK_CAMERA_FIXED_POSITION",
            # Run this line as one small step in the program.
            camera_position_base
        )

        # Go through each look point and give it a number.
        for index, look_point in enumerate(look_points_base, start=1):
            # Create a marker point in RoboDK.
            self.create_point_marker(
                # Add this value to the current list or function call.
                f"NECK_LOOK_POINT_{index:02d}",
                # Run this line as one small step in the program.
                look_point
            )

        # Go through each TCP pose and give it a number.
        for index, tcp_pose_base in enumerate(tcp_pose_targets, start=1):
            # Create a target marker in RoboDK.
            self.create_target_marker(
                # Add this value to the current list or function call.
                f"NECK_TCP_TARGET_{index:02d}",
                # Run this line as one small step in the program.
                tcp_pose_base
            )

    # Create the function that makes a small marker at one 3D point.
    def create_point_marker(self, name, position_base):
        # Create a simple 4x4 pose matrix for the marker.
        target_pose_base = np.eye(4, dtype=np.float64)
        # Put the marker position into the pose matrix.
        target_pose_base[:3, 3] = position_base

        # Give this result back to the code that asked for it.
        return self.create_target_marker(
            # Add this value to the current list or function call.
            name,
            # Run this line as one small step in the program.
            target_pose_base
        )

    # Create the function that creates one RoboDK target marker.
    def create_target_marker(self, name, target_pose_base):
        # Delete any old marker with the same name first.
        self.delete_existing_item(name, ITEM_TYPE_TARGET)

        # Create a new RoboDK target with this name.
        target = self.rdk.AddTarget(name)
        # Set the marker pose after converting it to RoboDK format.
        target.setPose(TransformUtils.numpy_to_robodk_mat(target_pose_base))

        # Give back the RoboDK target that was created.
        return target

    # Create the function that removes an old RoboDK item with the same name.
    def delete_existing_item(self, name, item_type):
        # Ask RoboDK if an item with this name already exists.
        item = self.rdk.Item(name, item_type)

        # Check if an old RoboDK item with this name exists.
        if item.Valid():
            # Delete the old item from RoboDK.
            item.Delete()
