# RoboDK File Importer OOP

This project imports the converted scan and aligned CAD file into RoboDK.

## What it does

1. Checks if the colored scan OBJ exists.
2. Checks if the matching MTL file exists.
3. If OBJ is missing, it tries to import the colored PLY instead.
4. Imports the aligned CAD STL.
5. Makes the CAD transparent red.
6. Deletes older imported items before importing the new ones.

## File structure

```text
robodk_file_importer
│
├── main.py
├── config.py
├── file_validator.py
├── robodk_item_service.py
└── robodk_import_service.py
```

## How to run in RoboDK

Open only `main.py` in RoboDK.

If RoboDK runs the file from Temp, update this path in `main.py`:

```python
PROJECT_FOLDER = Path(
    r"C:\Users\daryl\Documents\RoboDK\robodk_file_importer"
)
```

It must point to the real folder that contains `config.py`.
