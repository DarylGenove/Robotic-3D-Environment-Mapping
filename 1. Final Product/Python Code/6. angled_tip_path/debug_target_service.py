# Bring in the sys toolbox so this file can use it.
import sys

# Bring in the numpy toolbox so this file can use it.
import numpy as np

# Add the RoboDK Python folder so RoboDK tools can be imported.
sys.path.append("C:/RoboDK/Python")

# Bring in ITEM_TYPE_TARGET from robodk.robolink so we can use it here.
from robodk.robolink import ITEM_TYPE_TARGET

# Bring in TransformUtils from transform_utils so we can use it here.
from transform_utils import TransformUtils


# Create the DebugTargetService object that groups related actions together.
class DebugTargetService:
    # Start the   init   function.
    def __init__(self, config, rdk):
        # Save config so the program can use it later.
        self.config = config
        # Save rdk so the program can use it later.
        self.rdk = rdk

    # Start the create debug targets function.
    def create_debug_targets(self, targets):
        # Check if this condition is true.
        if not self.config.CREATE_DEBUG_TARGETS:
            # Go back without sending a value.
            return

        # Repeat this step for every item in the group.
        for index, (_, tcp_pose_base, seam_point_base) in enumerate(
            # This line helps the program do the next small step.
            targets,
            # Save start so the program can use it later.
            start=1
        # This line helps the program do the next small step.
        ):
            # Start a multi-line command.
            self.create_target_marker(
                # This line helps the program do the next small step.
                f"ANGLED_TCP_TARGET_{index:02d}",
                # This line helps the program do the next small step.
                tcp_pose_base
            # Close this group of values.
            )

            # Start a multi-line command.
            self.create_point_marker(
                # This line helps the program do the next small step.
                f"ANGLED_SEAM_POINT_{index:02d}",
                # This line helps the program do the next small step.
                seam_point_base
            # Close this group of values.
            )

    # Start the create point marker function.
    def create_point_marker(self, name, position_base):
        # Create a blank 3D transform that starts as no movement.
        target_pose_base = np.eye(4, dtype=np.float64)
        # Save target pose base[:3, 3] so the program can use it later.
        target_pose_base[:3, 3] = position_base

        # Send this result back to the place that called the function.
        return self.create_target_marker(
            # This line helps the program do the next small step.
            name,
            # This line helps the program do the next small step.
            target_pose_base
        # Close this group of values.
        )

    # Start the create target marker function.
    def create_target_marker(self, name, target_pose_base):
        # Check if this condition is true.
        if not self.config.CREATE_DEBUG_TARGETS:
            # Send this result back to the place that called the function.
            return None

        # This line helps the program do the next small step.
        self.delete_existing_item(name, ITEM_TYPE_TARGET)

        # Create a temporary target inside RoboDK.
        target = self.rdk.AddTarget(name)
        # Save the 3D position and rotation inside the RoboDK target.
        target.setPose(TransformUtils.numpy_to_robodk_mat(target_pose_base))

        # Send this result back to the place that called the function.
        return target

    # Start the delete existing item function.
    def delete_existing_item(self, name, item_type):
        # Save item so the program can use it later.
        item = self.rdk.Item(name, item_type)

        # Check if this condition is true.
        if item.Valid():
            # Remove the temporary RoboDK item after using it.
            item.Delete()
