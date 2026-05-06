from robodk.robolink import (
    Robolink,
    ITEM_TYPE_ROBOT,
    ITEM_TYPE_TARGET,
    ITEM_TYPE_OBJECT,
    ITEM_TYPE_FRAME,
    ITEM_TYPE_TOOL,
)
from robodk.robomath import transl
import os
import time

# -----------------------------
# Helpers
# -----------------------------
def write_open_box_obj_with_colors(path_obj: str, size_mm: float) -> None:
    """
    Writes an OPEN-TOP box (no ceiling) with colored faces.
    Bottom + 4 walls only.
    Units: mm
    """
    s = float(size_mm)
    hx = s / 2.0
    hy = s / 2.0
    z0 = 0.0
    z1 = s

    base_name = os.path.splitext(os.path.basename(path_obj))[0]
    dir_name = os.path.dirname(path_obj)
    path_mtl = os.path.join(dir_name, f"{base_name}.mtl")
    mtl_name = os.path.basename(path_mtl)

    # Vertices
    v1 = (-hx, -hy, z0)
    v2 = ( hx, -hy, z0)
    v3 = ( hx,  hy, z0)
    v4 = (-hx,  hy, z0)
    v5 = (-hx, -hy, z1)
    v6 = ( hx, -hy, z1)
    v7 = ( hx,  hy, z1)
    v8 = (-hx,  hy, z1)

    verts = [v1, v2, v3, v4, v5, v6, v7, v8]

    # Materials
    materials = [
        ("mat_bottom", (0.90, 0.20, 0.20)),  # red
        ("mat_front",  (0.20, 0.20, 0.90)),  # blue
        ("mat_back",   (0.90, 0.90, 0.20)),  # yellow
        ("mat_left",   (0.90, 0.20, 0.90)),  # magenta
        ("mat_right",  (0.20, 0.90, 0.90)),  # cyan
    ]

    with open(path_mtl, "w", encoding="utf-8") as f:
        for name, (r, g, b) in materials:
            f.write(f"newmtl {name}\n")
            f.write(f"Kd {r} {g} {b}\n")
            f.write("Ka 0.1 0.1 0.1\n")
            f.write("Ks 0.05 0.05 0.05\n")
            f.write("d 1.0\n")
            f.write("illum 2\n\n")

    # Faces (NO TOP FACE)
    face_groups = [
        ("mat_bottom", [(1, 2, 3), (1, 3, 4)]),
        ("mat_front",  [(1, 6, 2), (1, 5, 6)]),
        ("mat_back",   [(4, 3, 7), (4, 7, 8)]),
        ("mat_left",   [(1, 4, 8), (1, 8, 5)]),
        ("mat_right",  [(2, 7, 3), (2, 6, 7)]),
    ]

    with open(path_obj, "w", encoding="utf-8") as f:
        f.write(f"mtllib {mtl_name}\n\n")
        for (x, y, z) in verts:
            f.write(f"v {x} {y} {z}\n")

        f.write("\n")
        for mat, tris in face_groups:
            f.write(f"usemtl {mat}\n")
            for a, b, c in tris:
                f.write(f"f {a} {b} {c}\n")


def ensure_frame(RDK, name):
    fr = RDK.Item(name, ITEM_TYPE_FRAME)
    if not fr.Valid():
        fr = RDK.AddFrame(name)
    return fr


def import_object_fresh(RDK, name, filepath, parent):
    old = RDK.Item(name)
    if old.Valid():
        old.Delete()
    obj = RDK.AddFile(filepath, parent)
    obj.setName(name)
    return obj


# -----------------------------
# Main
# -----------------------------
time.sleep(2.0)
RDK = Robolink()

robot = RDK.Item("UR10e", ITEM_TYPE_ROBOT)
if not robot.Valid():
    raise Exception("UR10e not found")

env_frame = ensure_frame(RDK, "ENV_FRAME")
env_frame.setPose(transl(0, 0, 0))

BOX_SIZE_MM = 4000.0

script_dir = os.path.dirname(os.path.abspath(__file__))
box_path = os.path.join(script_dir, "env_open_box.obj")
write_open_box_obj_with_colors(box_path, BOX_SIZE_MM)

env_box = import_object_fresh(RDK, "ENV_BOX", box_path, env_frame)
env_box.setPose(transl(0, 0, 0))

try:
    robot.setParent(env_frame)
except Exception:
    pass
robot.setPose(transl(0, 0, 0))

# Camera as TOOL (moves with robot)
camera_tcp = RDK.Item("Camera_TCP", ITEM_TYPE_TOOL)
if not camera_tcp.Valid():
    camera_tcp = robot.AddTool(transl(0, 0, 150), "Camera_TCP")
robot.setTool(camera_tcp)

camera1 = RDK.Item("Camera 1")
camera1.setParent(camera_tcp)
camera1.setPose(transl(0, 0, 0))

targets = [f"Target {i}" for i in range(1, 11)]

robot.setSpeedJoints(10)
robot.setAccelerationJoints(20)

print("Open-top environment created. Camera moves with UR10e.")

while True:
    for t in targets:
        target = RDK.Item(t, ITEM_TYPE_TARGET)
        robot.MoveJ(target)
        robot.Pause(2.0)
