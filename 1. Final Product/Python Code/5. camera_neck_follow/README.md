# Camera Neck Follow OOP

This project refactors the RoboDK camera neck-follow script into smaller classes.

## What this program does

The robot moves to a safe center camera view. From that position, it creates a virtual line in the camera frame. Then it rotates the camera view from the left side of that line, to the center, and then to the right side.

The camera position stays fixed. Only the camera orientation changes.

## File structure

```text
camera_neck_follow
│
├── main.py
├── config.py
├── transform_utils.py
├── camera_calibration.py
├── robot_controller.py
├── look_line_generator.py
├── camera_pose_builder.py
├── debug_target_service.py
└── camera_neck_follow_service.py
```

## How to run

Open only `main.py` in RoboDK.

Update this path inside `main.py`:

```python
PROJECT_FOLDER = Path(
    r"C:\Users\daryl\Documents\RoboDK\camera_neck_follow"
)
```

It must point to the real folder where `config.py` is saved.
