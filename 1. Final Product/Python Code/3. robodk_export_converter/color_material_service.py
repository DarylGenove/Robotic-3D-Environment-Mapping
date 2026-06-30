# Use NumPy to do math with lists of numbers.
import numpy as np


# Create the ColorMaterialService class to group related code together.
class ColorMaterialService:
    # Create the quantize_color function.
    def quantize_color(self, color, levels=12):
        # Store this value in color.
        color = np.clip(color, 0.0, 1.0)

        # Store this value in quantized_color.
        quantized_color = np.round(color * (levels - 1)) / (levels - 1)

        # Give this value back to the code that asked for it.
        return tuple(quantized_color.tolist())

    # Create the create_material_name function.
    def create_material_name(self, material_index):
        # Give this value back to the code that asked for it.
        return f"scan_color_{material_index:04d}"

    # Create the create_material_lines function.
    def create_material_lines(self, material_name, color):
        # Split the color into red, green, and blue values.
        red, green, blue = color

        # Give this value back to the code that asked for it.
        return [
            # Add this text value.
            f"newmtl {material_name}",
            # Add this text value.
            f"Ka {red:.6f} {green:.6f} {blue:.6f}",
            # Add this text value.
            f"Kd {red:.6f} {green:.6f} {blue:.6f}",
            # Add this text value.
            "Ks 0.000000 0.000000 0.000000",
            # Add this text value.
            "Ns 10.000000",
            # Add this text value.
            "d 1.000000",
            # Add this text value.
            "illum 1",
            # Add this text value.
            "",
        ]
