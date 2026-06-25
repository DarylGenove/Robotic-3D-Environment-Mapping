import numpy as np


class ColorMaterialService:
    def quantize_color(self, color, levels=12):
        color = np.clip(color, 0.0, 1.0)

        quantized_color = np.round(color * (levels - 1)) / (levels - 1)

        return tuple(quantized_color.tolist())

    def create_material_name(self, material_index):
        return f"scan_color_{material_index:04d}"

    def create_material_lines(self, material_name, color):
        red, green, blue = color

        return [
            f"newmtl {material_name}",
            f"Ka {red:.6f} {green:.6f} {blue:.6f}",
            f"Kd {red:.6f} {green:.6f} {blue:.6f}",
            "Ks 0.000000 0.000000 0.000000",
            "Ns 10.000000",
            "d 1.000000",
            "illum 1",
            "",
        ]
