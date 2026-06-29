import sys

sys.path.append("C:/RoboDK/Python")

from robodk.robolink import Robolink


class RoboDKItemService:
    def __init__(self):
        self.rdk = Robolink()

    def delete_existing_item(self, item_name):
        existing_item = self.rdk.Item(item_name)

        if existing_item.Valid():
            existing_item.Delete()

    def import_file(self, file_path, item_name):
        item = self.rdk.AddFile(str(file_path))

        if not item.Valid():
            raise Exception(f"Could not import file into RoboDK: {file_path}")

        item.setName(item_name)
        item.setVisible(True)

        return item

    def set_item_color(self, item, color):
        item.setColor(color)
