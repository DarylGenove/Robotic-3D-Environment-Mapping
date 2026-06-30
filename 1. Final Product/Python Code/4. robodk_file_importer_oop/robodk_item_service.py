# Bring in sys so Python can change where it looks for project files.
import sys

# Add the RoboDK Python folder so this script can use RoboDK tools.
sys.path.append("C:/RoboDK/Python")

# Bring in Robolink so Python can talk to RoboDK.
from robodk.robolink import Robolink


# Create the RoboDKItemService class to group related steps together.
class RoboDKItemService:
    # Create the setup function that saves the tools this object needs.
    def __init__(self):
        # Open a connection to the running RoboDK program.
        self.rdk = Robolink()

    # Create the delete existing item function.
    def delete_existing_item(self, item_name):
        # Ask RoboDK if an item with this name already exists.
        existing_item = self.rdk.Item(item_name)

        # Check if an old item with this name already exists in RoboDK.
        if existing_item.Valid():
            # Delete the old item from RoboDK.
            existing_item.Delete()

    # Create the import file function.
    def import_file(self, file_path, item_name):
        # Ask RoboDK to import this file.
        item = self.rdk.AddFile(str(file_path))

        # Check if RoboDK failed to create or find the item.
        if not item.Valid():
            # Stop the program because RoboDK could not import the file.
            raise Exception(f"Could not import file into RoboDK: {file_path}")

        # Rename the imported item inside RoboDK.
        item.setName(item_name)
        # Make the imported item visible in RoboDK.
        item.setVisible(True)

        # Give the imported RoboDK item back to the caller.
        return item

    # Create the set item color function.
    def set_item_color(self, item, color):
        # Apply the chosen color to this RoboDK item.
        item.setColor(color)
