from transform_utils import clamp, make_local_offset_transform  # Gets clamp, make_local_offset_transform from transform_utils so this file can use it.


class AdaptivePoseGenerator:  # Makes a toolbox that creates extra scan positions around the cabinet.
    def __init__(self, config):  # Makes a function named   init  .
        self.config = config  # Stores the scanner settings so the program can use them.

    def generate_scan_offsets(self, adaptive_bounds):  # Creates movement offsets around the cabinet center.
        extent_x = adaptive_bounds["extent_x"]  # Stores extent x for use in the next steps.
        extent_y = adaptive_bounds["extent_y"]  # Stores extent y for use in the next steps.

        center_x = adaptive_bounds["center_x"]  # Stores the horizontal center of the detected box.
        center_y = adaptive_bounds["center_y"]  # Stores the vertical center of the detected box.
        center_z = adaptive_bounds["center_z"]  # Stores center z for use in the next steps.

        side_offset = clamp(  # Stores side offset for use in the next steps.
            extent_x * 0.35,  # Adds one item to the multi-line value.
            self.config.MIN_SIDE_OFFSET_M,  # Adds one item to the multi-line value.
            self.config.MAX_SIDE_OFFSET_M,  # Adds one item to the multi-line value.
        )  # Closes the multi-line code started above.

        vertical_offset = clamp(  # Stores vertical offset for use in the next steps.
            extent_y * 0.35,  # Adds one item to the multi-line value.
            self.config.MIN_VERTICAL_OFFSET_M,  # Adds one item to the multi-line value.
            self.config.MAX_VERTICAL_OFFSET_M,  # Adds one item to the multi-line value.
        )  # Closes the multi-line code started above.

        forward_offset = clamp(  # Stores forward offset for use in the next steps.
            center_z * 0.12,  # Adds one item to the multi-line value.
            self.config.MIN_FORWARD_OFFSET_M,  # Adds one item to the multi-line value.
            self.config.MAX_FORWARD_OFFSET_M,  # Adds one item to the multi-line value.
        )  # Closes the multi-line code started above.

        print("")  # Shows a message in the console.
        print("Adaptive scan movement offsets:")  # Shows a message in the console.
        print(f"Side offset: {side_offset:.4f} m")  # Shows a message in the console.
        print(f"Vertical offset: {vertical_offset:.4f} m")  # Shows a message in the console.
        print(f"Forward offset: {forward_offset:.4f} m")  # Shows a message in the console.

        return [  # Gives this result back to the part of the code that called it.
            ("Reference_Center", 0.00, 0.00, 0.00),  # Adds one item to the multi-line value.
            ("Left_Inside_Area", center_x - side_offset, center_y, 0.00),  # Adds one item to the multi-line value.
            ("Right_Inside_Area", center_x + side_offset, center_y, 0.00),  # Adds one item to the multi-line value.
            ("Upper_Inside_Area", center_x, center_y - vertical_offset, 0.00),  # Adds one item to the multi-line value.
            ("Lower_Inside_Area", center_x, center_y + vertical_offset, 0.00),  # Adds one item to the multi-line value.
            ("Upper_Left_Inside_Area", center_x - side_offset, center_y - vertical_offset, 0.00),  # Adds one item to the multi-line value.
            ("Upper_Right_Inside_Area", center_x + side_offset, center_y - vertical_offset, 0.00),  # Adds one item to the multi-line value.
            ("Lower_Left_Inside_Area", center_x - side_offset, center_y + vertical_offset, 0.00),  # Adds one item to the multi-line value.
            ("Lower_Right_Inside_Area", center_x + side_offset, center_y + vertical_offset, 0.00),  # Adds one item to the multi-line value.
            ("Closer_Center", center_x, center_y, forward_offset),  # Adds one item to the multi-line value.
            ("Closer_Left", center_x - side_offset * 0.70, center_y, forward_offset),  # Adds one item to the multi-line value.
            ("Closer_Right", center_x + side_offset * 0.70, center_y, forward_offset),  # Adds one item to the multi-line value.
            ("Closer_Upper", center_x, center_y - vertical_offset * 0.70, forward_offset),  # Adds one item to the multi-line value.
            ("Closer_Lower", center_x, center_y + vertical_offset * 0.70, forward_offset),  # Adds one item to the multi-line value.
        ]  # Closes the multi-line code started above.

    def generate_scan_camera_poses_from_center(self, T_base_camera_center, adaptive_bounds):  # Creates camera poses from the center scan position.
        generated_poses = []  # Stores generated poses for use in the next steps.
        adaptive_offsets = self.generate_scan_offsets(adaptive_bounds)  # Stores adaptive offsets for use in the next steps.

        print("\nGenerating adaptive scan poses from center reference...")  # Shows a message in the console.
        print("Center camera position in robot base frame:")  # Shows a message in the console.
        print(f"X: {T_base_camera_center[0, 3] * 1000.0:.1f} mm")  # Shows a message in the console.
        print(f"Y: {T_base_camera_center[1, 3] * 1000.0:.1f} mm")  # Shows a message in the console.
        print(f"Z: {T_base_camera_center[2, 3] * 1000.0:.1f} mm")  # Shows a message in the console.

        for label, offset_x, offset_y, offset_z in adaptive_offsets:  # Repeats the next indented lines for each item.
            T_camera_offset = make_local_offset_transform(offset_x, offset_y, offset_z)  # Stores a small camera movement from the current camera position.
            T_base_camera_target = T_base_camera_center @ T_camera_offset  # Stores where the camera should move next.

            print("")  # Shows a message in the console.
            print(f"Generated camera pose: {label}")  # Shows a message in the console.
            print(f"Local offset X: {offset_x * 1000.0:.1f} mm")  # Shows a message in the console.
            print(f"Local offset Y: {offset_y * 1000.0:.1f} mm")  # Shows a message in the console.
            print(f"Local offset Z: {offset_z * 1000.0:.1f} mm")  # Shows a message in the console.
            print("Generated camera position in robot base frame:")  # Shows a message in the console.
            print(f"X: {T_base_camera_target[0, 3] * 1000.0:.1f} mm")  # Shows a message in the console.
            print(f"Y: {T_base_camera_target[1, 3] * 1000.0:.1f} mm")  # Shows a message in the console.
            print(f"Z: {T_base_camera_target[2, 3] * 1000.0:.1f} mm")  # Shows a message in the console.

            generated_poses.append((label, T_base_camera_target))  # Runs this line as one small step in the program.

        return generated_poses  # Gives this result back to the part of the code that called it.
