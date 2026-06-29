class FileValidator:
    def validate_file_exists(self, file_path):
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

    def validate_scan_files(self, config):
        if config.COLORED_SCAN_OBJ_FILE.exists():
            self.validate_file_exists(config.COLORED_SCAN_MTL_FILE)
            return config.COLORED_SCAN_OBJ_FILE

        if config.COLORED_SCAN_PLY_FILE.exists():
            return config.COLORED_SCAN_PLY_FILE

        raise FileNotFoundError(
            "No colored scan file found. Expected OBJ or PLY:\n"
            f"{config.COLORED_SCAN_OBJ_FILE}\n"
            f"{config.COLORED_SCAN_PLY_FILE}"
        )

    def validate_cad_file(self, config):
        self.validate_file_exists(config.ALIGNED_CAD_STL_FILE)
        return config.ALIGNED_CAD_STL_FILE
