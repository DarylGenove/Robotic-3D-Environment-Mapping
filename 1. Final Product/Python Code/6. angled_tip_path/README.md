# Angled Tip Path OOP

This project refactors the RoboDK angled dry-run tip path script into smaller classes.

## What this program does

The robot moves to a safe center camera view, creates seam points in the camera frame, converts those points into the robot base frame, then generates TCP poses where the tool points toward the seam.

This is a dry-run path only. It does not trigger a welding machine or welding arc.

## File structure

```text
angled_tip_path
│
├── main.py
├── config.py
├── transform_utils.py
├── camera_calibration.py
├── robot_controller.py
├── seam_path_generator.py
├── angled_tcp_pose_builder.py
├── debug_target_service.py
└── angled_tip_path_service.py
```

## How to run in RoboDK

Open only `main.py` in RoboDK.

Update this path inside `main.py`:

```python
PROJECT_FOLDER = Path(
    r"C:\Users\daryl\Documents\RoboDK\angled_tip_path"
)
```

It must point to the real folder where `config.py` is saved.

## Class responsibilities

- `Config`: stores all settings, safety values, seam values, and calibration values.
- `TransformUtils`: converts RoboDK matrices to NumPy matrices and back.
- `CameraCalibration`: builds TCP-to-camera transforms.
- `RobotController`: handles RoboDK connection, movement, FK, J6 seed logic, and safety checks.
- `SeamPathGenerator`: creates seam points in the camera frame and transforms them to the robot base frame.
- `AngledTcpPoseBuilder`: builds TCP poses angled toward the seam.
- `DebugTargetService`: creates RoboDK debug targets for the TCP targets and seam points.
- `AngledTipPathService`: runs the full workflow.
