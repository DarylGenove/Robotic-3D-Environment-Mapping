# Adaptive Inside Box Scanner - OOP Version

This is the OOP refactor of the original single Python script.

## Main entry file

Run only:

```text
main.py
```

## Important RoboDK note

If you run `main.py` from RoboDK, RoboDK may copy it to a Temp folder before running it.
Because of that, change this line in `main.py` to the real folder where these files are saved:

```python
PROJECT_FOLDER = Path(
    r"C:\Users\daryl\Documents\RoboDK\adaptive_inside_box_scanner"
)
```

## File responsibilities

- `config.py`: all settings and paths
- `transform_utils.py`: RoboDK matrix and transform helpers
- `robot_controller.py`: robot connection and robot movement
- `realsense_camera.py`: RealSense startup and point cloud capture
- `point_cloud_service.py`: point cloud bounds, crop, cleaning, normals, saving debug scans
- `pose_generator.py`: adaptive scan pose generation
- `auto_box_detector.py`: depth mask, ROI, box detection, OpenCV drawing
- `auto_centering_service.py`: automatic robot movement to center camera on the box
- `scanning_service.py`: full scan workflow/orchestration
- `main.py`: starts everything
