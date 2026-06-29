import numpy as np


class ColoredVoxelObjWriter:
    def __init__(self, color_material_service):
        self.color_material_service = color_material_service

    def write(
        self,
        point_cloud,
        obj_file,
        mtl_file,
        voxel_size_m=0.01,
        color_levels=12
    ):
        if len(point_cloud.points) == 0:
            raise Exception("Point cloud is empty.")

        if not point_cloud.has_colors():
            raise Exception(
                "The cleaned scan PCD does not contain color data. "
                "The color was already lost before this conversion step."
            )

        point_cloud = point_cloud.voxel_down_sample(voxel_size_m)

        if len(point_cloud.points) == 0:
            raise Exception("Point cloud became empty after voxel downsampling.")

        if not point_cloud.has_colors():
            raise Exception("Point cloud lost color after voxel downsampling.")

        points = np.asarray(point_cloud.points)
        colors = np.asarray(point_cloud.colors)

        voxel_size_mm = voxel_size_m * 1000.0
        half_size_mm = voxel_size_mm / 2.0

        cube_offsets = self._create_cube_offsets(half_size_mm)
        cube_faces = self._create_cube_faces()

        material_by_color = {}
        material_lines = []
        obj_lines = []

        obj_lines.append(f"mtllib {mtl_file.name}")
        obj_lines.append("o Colored_Cleaned_Scan")

        vertex_index = 1

        for point, color in zip(points, colors):
            point_mm = point * 1000.0
            quantized_color = self.color_material_service.quantize_color(
                color,
                levels=color_levels
            )

            if quantized_color not in material_by_color:
                material_name = self.color_material_service.create_material_name(
                    len(material_by_color)
                )
                material_by_color[quantized_color] = material_name

                material_lines.extend(
                    self.color_material_service.create_material_lines(
                        material_name,
                        quantized_color
                    )
                )

            material_name = material_by_color[quantized_color]

            vertex_index = self._append_voxel_to_obj(
                obj_lines,
                point_mm,
                cube_offsets,
                cube_faces,
                material_name,
                vertex_index
            )

        obj_file.write_text("\n".join(obj_lines), encoding="utf-8")
        mtl_file.write_text("\n".join(material_lines), encoding="utf-8")

        print("OBJ voxel points used:", len(points))
        print("OBJ material count:", len(material_by_color))

    def _create_cube_offsets(self, half_size_mm):
        return np.array(
            [
                [-half_size_mm, -half_size_mm, -half_size_mm],
                [half_size_mm, -half_size_mm, -half_size_mm],
                [half_size_mm, half_size_mm, -half_size_mm],
                [-half_size_mm, half_size_mm, -half_size_mm],
                [-half_size_mm, -half_size_mm, half_size_mm],
                [half_size_mm, -half_size_mm, half_size_mm],
                [half_size_mm, half_size_mm, half_size_mm],
                [-half_size_mm, half_size_mm, half_size_mm],
            ],
            dtype=np.float64
        )

    def _create_cube_faces(self):
        return [
            [1, 2, 3, 4],
            [5, 8, 7, 6],
            [1, 5, 6, 2],
            [2, 6, 7, 3],
            [3, 7, 8, 4],
            [4, 8, 5, 1],
        ]

    def _append_voxel_to_obj(
        self,
        obj_lines,
        point_mm,
        cube_offsets,
        cube_faces,
        material_name,
        vertex_index
    ):
        for offset in cube_offsets:
            vertex = point_mm + offset

            obj_lines.append(
                f"v {vertex[0]:.6f} {vertex[1]:.6f} {vertex[2]:.6f}"
            )

        obj_lines.append(f"usemtl {material_name}")

        for face in cube_faces:
            face_indices = [
                vertex_index + local_index - 1
                for local_index in face
            ]

            obj_lines.append(
                "f " + " ".join(str(face_index) for face_index in face_indices)
            )

        return vertex_index + 8
