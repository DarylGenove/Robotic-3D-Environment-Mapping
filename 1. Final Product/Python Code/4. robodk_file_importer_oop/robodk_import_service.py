# Create the RoboDKImportService class to group related steps together.
class RoboDKImportService:
    # Create the setup function that saves the tools this object needs.
    def __init__(self, config, file_validator, robodk_item_service):
        # Save the settings object inside this service.
        self.config = config
        # Save the file-checking helper inside this service.
        self.file_validator = file_validator
        # Save the RoboDK item helper inside this service.
        self.robodk_item_service = robodk_item_service

    # Create the run function.
    def run(self):
        # Remove old imported items so the new ones do not overlap.
        self._delete_old_items()

        # Save a value in imported scan file.
        imported_scan_file = self.file_validator.validate_scan_files(
            # Run this line as one small step in the program.
            self.config
        )

        # Save a value in imported cad file.
        imported_cad_file = self.file_validator.validate_cad_file(
            # Run this line as one small step in the program.
            self.config
        )

        # Save a value in cleaned scan.
        cleaned_scan = self.robodk_item_service.import_file(
            # Add this value to the current list or function call.
            imported_scan_file,
            # Run this line as one small step in the program.
            self.config.SCAN_ITEM_NAME
        )

        # Save a value in aligned cad.
        aligned_cad = self.robodk_item_service.import_file(
            # Add this value to the current list or function call.
            imported_cad_file,
            # Run this line as one small step in the program.
            self.config.CAD_ITEM_NAME
        )

        # Change the CAD item color in RoboDK.
        self.robodk_item_service.set_item_color(
            # Add this value to the current list or function call.
            aligned_cad,
            # Run this line as one small step in the program.
            self.config.CAD_COLOR
        )

        # Print a final summary of what was imported.
        self._print_import_summary(
            # Add this value to the current list or function call.
            cleaned_scan,
            # Add this value to the current list or function call.
            aligned_cad,
            # Add this value to the current list or function call.
            imported_scan_file,
            # Run this line as one small step in the program.
            imported_cad_file
        )

    # Create the  delete old items function.
    def _delete_old_items(self):
        # Delete an old RoboDK item with this name if it exists.
        self.robodk_item_service.delete_existing_item(
            # Run this line as one small step in the program.
            self.config.SCAN_ITEM_NAME
        )

        # Delete an old RoboDK item with this name if it exists.
        self.robodk_item_service.delete_existing_item(
            # Run this line as one small step in the program.
            self.config.CAD_ITEM_NAME
        )

    # Create the  print import summary function.
    def _print_import_summary(
        # Add this value to the current list or function call.
        self,
        # Add this value to the current list or function call.
        cleaned_scan,
        # Add this value to the current list or function call.
        aligned_cad,
        # Add this value to the current list or function call.
        imported_scan_file,
        # Run this line as one small step in the program.
        imported_cad_file
    # Run this line as one small step in the program.
    ):
        # Show this helpful message on the screen.
        print("")
        # Show this helpful message on the screen.
        print("=" * 70)
        # Show this helpful message on the screen.
        print("IMPORTED INTO ROBODK")
        # Show this helpful message on the screen.
        print("=" * 70)
        # Show this helpful message on the screen.
        print("Colored scan:", cleaned_scan.Name())
        # Show this helpful message on the screen.
        print("Scan file   :", imported_scan_file)
        # Show this helpful message on the screen.
        print("")
        # Show this helpful message on the screen.
        print("Aligned CAD :", aligned_cad.Name())
        # Show this helpful message on the screen.
        print("CAD file    :", imported_cad_file)
        # Show this helpful message on the screen.
        print("")
        # Show this helpful message on the screen.
        print(
            # Run this line as one small step in the program.
            "The colored scan should keep its scanned color "
            # Run this line as one small step in the program.
            "if RoboDK reads the OBJ/MTL material."
        )
        # Show this helpful message on the screen.
        print("The CAD model is imported as transparent red.")
        # Show this helpful message on the screen.
        print("Both files are already scaled to millimeters.")
        # Show this helpful message on the screen.
        print("They should appear in the robot base coordinate position.")
