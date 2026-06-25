class RoboDKImportService:
    def __init__(self, config, file_validator, robodk_item_service):
        self.config = config
        self.file_validator = file_validator
        self.robodk_item_service = robodk_item_service

    def run(self):
        self._delete_old_items()

        imported_scan_file = self.file_validator.validate_scan_files(
            self.config
        )

        imported_cad_file = self.file_validator.validate_cad_file(
            self.config
        )

        cleaned_scan = self.robodk_item_service.import_file(
            imported_scan_file,
            self.config.SCAN_ITEM_NAME
        )

        aligned_cad = self.robodk_item_service.import_file(
            imported_cad_file,
            self.config.CAD_ITEM_NAME
        )

        self.robodk_item_service.set_item_color(
            aligned_cad,
            self.config.CAD_COLOR
        )

        self._print_import_summary(
            cleaned_scan,
            aligned_cad,
            imported_scan_file,
            imported_cad_file
        )

    def _delete_old_items(self):
        self.robodk_item_service.delete_existing_item(
            self.config.SCAN_ITEM_NAME
        )

        self.robodk_item_service.delete_existing_item(
            self.config.CAD_ITEM_NAME
        )

    def _print_import_summary(
        self,
        cleaned_scan,
        aligned_cad,
        imported_scan_file,
        imported_cad_file
    ):
        print("")
        print("=" * 70)
        print("IMPORTED INTO ROBODK")
        print("=" * 70)
        print("Colored scan:", cleaned_scan.Name())
        print("Scan file   :", imported_scan_file)
        print("")
        print("Aligned CAD :", aligned_cad.Name())
        print("CAD file    :", imported_cad_file)
        print("")
        print(
            "The colored scan should keep its scanned color "
            "if RoboDK reads the OBJ/MTL material."
        )
        print("The CAD model is imported as transparent red.")
        print("Both files are already scaled to millimeters.")
        print("They should appear in the robot base coordinate position.")
