class RoboDKConversionService:
    def __init__(self, config, colored_scan_exporter, cad_exporter):
        self.config = config
        self.colored_scan_exporter = colored_scan_exporter
        self.cad_exporter = cad_exporter

    def run(self):
        self._prepare_export_folder()
        self._validate_input_files()

        self._print_start_message()

        scan_pcd = self.colored_scan_exporter.load_colored_scan(
            self.config.CLEANED_SCAN_PCD
        )

        print("")
        print("Saving colored PLY point cloud for RoboDK...")

        self.colored_scan_exporter.save_colored_point_cloud_ply(
            scan_pcd,
            self.config.COLORED_SCAN_PLY_FOR_ROBODK
        )

        self.colored_scan_exporter.save_colored_voxel_obj(
            scan_pcd,
            self.config.COLORED_SCAN_OBJ_FOR_ROBODK,
            self.config.COLORED_SCAN_MTL_FOR_ROBODK,
            voxel_size_m=self.config.VOXEL_SIZE_M,
            color_levels=self.config.COLOR_LEVELS
        )

        self.cad_exporter.save_scaled_cad_stl(
            self.config.ALIGNED_CAD_STL,
            self.config.CAD_STL_FOR_ROBODK
        )

        self._print_done_message()

    def _prepare_export_folder(self):
        self.config.EXPORT_FOLDER.mkdir(parents=True, exist_ok=True)

    def _validate_input_files(self):
        if not self.config.CLEANED_SCAN_PCD.exists():
            raise FileNotFoundError(
                f"Cleaned scan PCD not found: {self.config.CLEANED_SCAN_PCD}"
            )

        if not self.config.ALIGNED_CAD_STL.exists():
            raise FileNotFoundError(
                f"Aligned CAD STL not found: {self.config.ALIGNED_CAD_STL}"
            )

    def _print_start_message(self):
        print("")
        print("=" * 70)
        print("CONVERTING COLORED PCD AND CAD FILES FOR ROBODK")
        print("=" * 70)
        print("")

    def _print_done_message(self):
        print("")
        print("=" * 70)
        print("DONE")
        print("=" * 70)
        print("Import these files into RoboDK:")
        print("")
        print("Best option for visible colors:")
        print(self.config.COLORED_SCAN_OBJ_FOR_ROBODK)
        print("")
        print("Backup option:")
        print(self.config.COLORED_SCAN_PLY_FOR_ROBODK)
        print("")
        print("CAD file:")
        print(self.config.CAD_STL_FOR_ROBODK)
        print("")
        print("Important:")
        print("Keep the OBJ and MTL files in the same folder.")
