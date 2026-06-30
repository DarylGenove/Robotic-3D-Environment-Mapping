# Create the RoboDKConversionService class to group related code together.
class RoboDKConversionService:
    # Set up this object when it is created.
    def __init__(self, config, colored_scan_exporter, cad_exporter):
        # Save this value inside the object as config.
        self.config = config
        # Save this value inside the object as colored_scan_exporter.
        self.colored_scan_exporter = colored_scan_exporter
        # Save this value inside the object as cad_exporter.
        self.cad_exporter = cad_exporter

    # Create the run function.
    def run(self):
        # Call a step that belongs to this object.
        self._prepare_export_folder()
        # Call a step that belongs to this object.
        self._validate_input_files()

        # Call a step that belongs to this object.
        self._print_start_message()

        # Store this value in scan_pcd.
        scan_pcd = self.colored_scan_exporter.load_colored_scan(
            # This line helps the program do the next small step.
            self.config.CLEANED_SCAN_PCD
        )

        # Show a message on the screen.
        print("")
        # Show a message on the screen.
        print("Saving colored PLY point cloud for RoboDK...")

        # This line helps the program do the next small step.
        self.colored_scan_exporter.save_colored_point_cloud_ply(
            # Add this value to the list or function call.
            scan_pcd,
            # This line helps the program do the next small step.
            self.config.COLORED_SCAN_PLY_FOR_ROBODK
        )

        # This line helps the program do the next small step.
        self.colored_scan_exporter.save_colored_voxel_obj(
            # Add this value to the list or function call.
            scan_pcd,
            # Add this value to the list or function call.
            self.config.COLORED_SCAN_OBJ_FOR_ROBODK,
            # Add this value to the list or function call.
            self.config.COLORED_SCAN_MTL_FOR_ROBODK,
            # Store this value in voxel_size_m.
            voxel_size_m=self.config.VOXEL_SIZE_M,
            # Store this value in color_levels.
            color_levels=self.config.COLOR_LEVELS
        )

        # This line helps the program do the next small step.
        self.cad_exporter.save_scaled_cad_stl(
            # Add this value to the list or function call.
            self.config.ALIGNED_CAD_STL,
            # This line helps the program do the next small step.
            self.config.CAD_STL_FOR_ROBODK
        )

        # Call a step that belongs to this object.
        self._print_done_message()

    # Create a helper step named _prepare_export_folder.
    def _prepare_export_folder(self):
        # Create this folder if it does not already exist.
        self.config.EXPORT_FOLDER.mkdir(parents=True, exist_ok=True)

    # Create a helper step named _validate_input_files.
    def _validate_input_files(self):
        # Check if this condition is true.
        if not self.config.CLEANED_SCAN_PCD.exists():
            # Stop the program and say that a needed file or folder is missing.
            raise FileNotFoundError(
                # Add this text value.
                f"Cleaned scan PCD not found: {self.config.CLEANED_SCAN_PCD}"
            )

        # Check if this condition is true.
        if not self.config.ALIGNED_CAD_STL.exists():
            # Stop the program and say that a needed file or folder is missing.
            raise FileNotFoundError(
                # Add this text value.
                f"Aligned CAD STL not found: {self.config.ALIGNED_CAD_STL}"
            )

    # Create a helper step named _print_start_message.
    def _print_start_message(self):
        # Show a message on the screen.
        print("")
        # Show a message on the screen.
        print("=" * 70)
        # Show a message on the screen.
        print("CONVERTING COLORED PCD AND CAD FILES FOR ROBODK")
        # Show a message on the screen.
        print("=" * 70)
        # Show a message on the screen.
        print("")

    # Create a helper step named _print_done_message.
    def _print_done_message(self):
        # Show a message on the screen.
        print("")
        # Show a message on the screen.
        print("=" * 70)
        # Show a message on the screen.
        print("DONE")
        # Show a message on the screen.
        print("=" * 70)
        # Show a message on the screen.
        print("Import these files into RoboDK:")
        # Show a message on the screen.
        print("")
        # Show a message on the screen.
        print("Best option for visible colors:")
        # Show a message on the screen.
        print(self.config.COLORED_SCAN_OBJ_FOR_ROBODK)
        # Show a message on the screen.
        print("")
        # Show a message on the screen.
        print("Backup option:")
        # Show a message on the screen.
        print(self.config.COLORED_SCAN_PLY_FOR_ROBODK)
        # Show a message on the screen.
        print("")
        # Show a message on the screen.
        print("CAD file:")
        # Show a message on the screen.
        print(self.config.CAD_STL_FOR_ROBODK)
        # Show a message on the screen.
        print("")
        # Show a message on the screen.
        print("Important:")
        # Show a message on the screen.
        print("Keep the OBJ and MTL files in the same folder.")
