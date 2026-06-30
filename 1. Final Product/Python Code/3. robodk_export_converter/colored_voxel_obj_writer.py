# Use NumPy to do math with lists of numbers.
import numpy as np


# Create the ColoredVoxelObjWriter class to group related code together.
class ColoredVoxelObjWriter:
    # Set up this object when it is created.
    def __init__(self, color_material_service):
        # Save this value inside the object as color_material_service.
        self.color_material_service = color_material_service

    # Create the write function.
    def write(
        # Add this value to the list or function call.
        self,
        # Add this value to the list or function call.
        point_cloud,
        # Add this value to the list or function call.
        obj_file,
        # Add this value to the list or function call.
        mtl_file,
        # Store this value in voxel_size_m.
        voxel_size_m=0.01,
        # Store this value in color_levels.
        color_levels=12
    # This line helps the program do the next small step.
    ):
        # Check if this condition is true.
        if len(point_cloud.points) == 0:
            # Stop the program and show a clear problem message.
            raise Exception("Point cloud is empty.")

        # Check if this condition is true.
        if not point_cloud.has_colors():
            # Stop the program and show a clear problem message.
            raise Exception(
                # Add this text value.
                "The cleaned scan PCD does not contain color data. "
                # Add this text value.
                "The color was already lost before this conversion step."
            )

        # Make the point cloud smaller by grouping nearby points.
        point_cloud = point_cloud.voxel_down_sample(voxel_size_m)

        # Check if this condition is true.
        if len(point_cloud.points) == 0:
            # Stop the program and show a clear problem message.
            raise Exception("Point cloud became empty after voxel downsampling.")

        # Check if this condition is true.
        if not point_cloud.has_colors():
            # Stop the program and show a clear problem message.
            raise Exception("Point cloud lost color after voxel downsampling.")

        # Store this value in points.
        points = np.asarray(point_cloud.points)
        # Store this value in colors.
        colors = np.asarray(point_cloud.colors)

        # Store this value in voxel_size_mm.
        voxel_size_mm = voxel_size_m * 1000.0
        # Store this value in half_size_mm.
        half_size_mm = voxel_size_mm / 2.0

        # Store this value in cube_offsets.
        cube_offsets = self._create_cube_offsets(half_size_mm)
        # Store this value in cube_faces.
        cube_faces = self._create_cube_faces()

        # Store this value in material_by_color.
        material_by_color = {}
        # Store text lines in material_lines.
        material_lines = []
        # Store text lines in obj_lines.
        obj_lines = []

        # Call this function to do one job.
        obj_lines.append(f"mtllib {mtl_file.name}")
        # Call this function to do one job.
        obj_lines.append("o Colored_Cleaned_Scan")

        # Store the current number in vertex_index.
        vertex_index = 1

        # Repeat this code for each item.
        for point, color in zip(points, colors):
            # Store this value in point_mm.
            point_mm = point * 1000.0
            # Store this value in quantized_color.
            quantized_color = self.color_material_service.quantize_color(
                # Add this value to the list or function call.
                color,
                # Store this value in levels.
                levels=color_levels
            )

            # Check if this condition is true.
            if quantized_color not in material_by_color:
                # Store a name in material_name.
                material_name = self.color_material_service.create_material_name(
                    # Call this function to do one job.
                    len(material_by_color)
                )
                # Store this value in material_by_color[quantized_color].
                material_by_color[quantized_color] = material_name

                # This line helps the program do the next small step.
                material_lines.extend(
                    # This line helps the program do the next small step.
                    self.color_material_service.create_material_lines(
                        # Add this value to the list or function call.
                        material_name,
                        # This line helps the program do the next small step.
                        quantized_color
                    )
                )

            # Store a name in material_name.
            material_name = material_by_color[quantized_color]

            # Store the current number in vertex_index.
            vertex_index = self._append_voxel_to_obj(
                # Add this value to the list or function call.
                obj_lines,
                # Add this value to the list or function call.
                point_mm,
                # Add this value to the list or function call.
                cube_offsets,
                # Add this value to the list or function call.
                cube_faces,
                # Add this value to the list or function call.
                material_name,
                # This line helps the program do the next small step.
                vertex_index
            )

        # Write the text into this file.
        obj_file.write_text("\n".join(obj_lines), encoding="utf-8")
        # Write the text into this file.
        mtl_file.write_text("\n".join(material_lines), encoding="utf-8")

        # Show a message on the screen.
        print("OBJ voxel points used:", len(points))
        # Show a message on the screen.
        print("OBJ material count:", len(material_by_color))

    # Create a helper step named _create_cube_offsets.
    def _create_cube_offsets(self, half_size_mm):
        # Give this value back to the code that asked for it.
        return np.array(
            [
                # Add this value to the list or function call.
                [-half_size_mm, -half_size_mm, -half_size_mm],
                # Add this value to the list or function call.
                [half_size_mm, -half_size_mm, -half_size_mm],
                # Add this value to the list or function call.
                [half_size_mm, half_size_mm, -half_size_mm],
                # Add this value to the list or function call.
                [-half_size_mm, half_size_mm, -half_size_mm],
                # Add this value to the list or function call.
                [-half_size_mm, -half_size_mm, half_size_mm],
                # Add this value to the list or function call.
                [half_size_mm, -half_size_mm, half_size_mm],
                # Add this value to the list or function call.
                [half_size_mm, half_size_mm, half_size_mm],
                # Add this value to the list or function call.
                [-half_size_mm, half_size_mm, half_size_mm],
            ],
            # Store this value in dtype.
            dtype=np.float64
        )

    # Create a helper step named _create_cube_faces.
    def _create_cube_faces(self):
        # Give this value back to the code that asked for it.
        return [
            # Add this value to the list or function call.
            [1, 2, 3, 4],
            # Add this value to the list or function call.
            [5, 8, 7, 6],
            # Add this value to the list or function call.
            [1, 5, 6, 2],
            # Add this value to the list or function call.
            [2, 6, 7, 3],
            # Add this value to the list or function call.
            [3, 7, 8, 4],
            # Add this value to the list or function call.
            [4, 8, 5, 1],
        ]

    # Create a helper step named _append_voxel_to_obj.
    def _append_voxel_to_obj(
        # Add this value to the list or function call.
        self,
        # Add this value to the list or function call.
        obj_lines,
        # Add this value to the list or function call.
        point_mm,
        # Add this value to the list or function call.
        cube_offsets,
        # Add this value to the list or function call.
        cube_faces,
        # Add this value to the list or function call.
        material_name,
        # This line helps the program do the next small step.
        vertex_index
    # This line helps the program do the next small step.
    ):
        # Repeat this code for each item.
        for offset in cube_offsets:
            # Store this value in vertex.
            vertex = point_mm + offset

            # This line helps the program do the next small step.
            obj_lines.append(
                # Add this text value.
                f"v {vertex[0]:.6f} {vertex[1]:.6f} {vertex[2]:.6f}"
            )

        # Call this function to do one job.
        obj_lines.append(f"usemtl {material_name}")

        # Repeat this code for each item.
        for face in cube_faces:
            # Store this value in face_indices.
            face_indices = [
                # This line helps the program do the next small step.
                vertex_index + local_index - 1
                # Repeat this code for each item.
                for local_index in face
            ]

            # This line helps the program do the next small step.
            obj_lines.append(
                # Call this function to do one job.
                "f " + " ".join(str(face_index) for face_index in face_indices)
            )

        # Give this value back to the code that asked for it.
        return vertex_index + 8
