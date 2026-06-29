# RoboDK Export Converter OOP

This project converts the cleaned colored scan and aligned CAD file into RoboDK-friendly files.

## Main flow

1. Load the cleaned colored scan PCD.
2. Save a millimeter-scaled colored PLY.
3. Convert the colored scan points into a voxel OBJ and MTL.
4. Load the aligned CAD STL.
5. Scale the CAD STL from meters to millimeters.
6. Print which files should be imported into RoboDK.

## File structure

```text
robodk_export_converter
│
├── main.py
├── config.py
├── point_cloud_scaler.py
├── color_material_service.py
├── colored_voxel_obj_writer.py
├── colored_scan_exporter.py
├── cad_exporter.py
└── robodk_conversion_service.py
```

## How to run in RoboDK

Open only `main.py` in RoboDK.

If RoboDK runs the file from Temp, update this line in `main.py`:

```python
PROJECT_FOLDER = Path(
    r"C:\Users\daryl\Documents\RoboDK\robodk_export_converter"
)
```

It must point to the real folder that contains `config.py`.
