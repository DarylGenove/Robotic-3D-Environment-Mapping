# Create the FileValidator class to group related steps together.
class FileValidator:
    # Create the validate file exists function.
    def validate_file_exists(self, file_path):
        # Check if this file path does not exist.
        if not file_path.exists():
            # Stop the program because an important file or folder is missing.
            raise FileNotFoundError(f"File not found: {file_path}")

    # Create the validate scan files function.
    def validate_scan_files(self, config):
        # Use the colored OBJ scan if it exists.
        if config.COLORED_SCAN_OBJ_FILE.exists():
            # Check that the matching material file exists beside the OBJ file.
            self.validate_file_exists(config.COLORED_SCAN_MTL_FILE)
            # Return the OBJ scan file path.
            return config.COLORED_SCAN_OBJ_FILE

        # Use the colored PLY scan if the OBJ file is missing.
        if config.COLORED_SCAN_PLY_FILE.exists():
            # Return the PLY scan file path.
            return config.COLORED_SCAN_PLY_FILE

        # Stop the program because an important file or folder is missing.
        raise FileNotFoundError(
            # Run this line as one small step in the program.
            "No colored scan file found. Expected OBJ or PLY:\n"
            # Run this line as one small step in the program.
            f"{config.COLORED_SCAN_OBJ_FILE}\n"
            # Run this line as one small step in the program.
            f"{config.COLORED_SCAN_PLY_FILE}"
        )

    # Create the validate cad file function.
    def validate_cad_file(self, config):
        # Check that the matching material file exists beside the OBJ file.
        self.validate_file_exists(config.ALIGNED_CAD_STL_FILE)
        # Return the CAD STL file path.
        return config.ALIGNED_CAD_STL_FILE
