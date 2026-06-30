import sys  # Loads sys so the code can change where Python looks for files.

import numpy as np  # Loads NumPy as np so the code can do fast number and matrix math.

sys.path.append("C:/RoboDK/Python")  # Runs this line as one small step in the program.

from robodk.robomath import Mat, TxyzRxyz_2_Pose  # Gets Mat, TxyzRxyz_2_Pose from robodk.robomath so this file can use it.


def robodk_mat_to_numpy(mat):  # Changes a RoboDK matrix into a NumPy transform matrix.
    transform = np.eye(4, dtype=np.float64)  # Stores a 4 by 4 movement table.

    for row in range(3):  # Repeats the next indented lines for each item.
        for col in range(3):  # Repeats the next indented lines for each item.
            transform[row, col] = mat[row, col]  # Runs this line as one small step in the program.

        transform[row, 3] = mat[row, 3] / 1000.0  # Runs this line as one small step in the program.

    return transform  # Gives this result back to the part of the code that called it.


def numpy_to_robodk_mat(transform):  # Changes a NumPy transform matrix into a RoboDK matrix.
    return Mat([  # Gives this result back to the part of the code that called it.
        [  # Starts a multi-line value.
            transform[0, 0],  # Adds one item to the multi-line value.
            transform[0, 1],  # Adds one item to the multi-line value.
            transform[0, 2],  # Adds one item to the multi-line value.
            transform[0, 3] * 1000.0,  # Adds one item to the multi-line value.
        ],  # Closes the multi-line code started above.
        [  # Starts a multi-line value.
            transform[1, 0],  # Adds one item to the multi-line value.
            transform[1, 1],  # Adds one item to the multi-line value.
            transform[1, 2],  # Adds one item to the multi-line value.
            transform[1, 3] * 1000.0,  # Adds one item to the multi-line value.
        ],  # Closes the multi-line code started above.
        [  # Starts a multi-line value.
            transform[2, 0],  # Adds one item to the multi-line value.
            transform[2, 1],  # Adds one item to the multi-line value.
            transform[2, 2],  # Adds one item to the multi-line value.
            transform[2, 3] * 1000.0,  # Adds one item to the multi-line value.
        ],  # Closes the multi-line code started above.
        [0, 0, 0, 1],  # Adds one item to the multi-line value.
    ])  # Closes the multi-line code started above.


def xyzrxryrz_to_numpy(pose_values):  # Changes XYZ and rotation values into a transform matrix.
    pose = TxyzRxyz_2_Pose([  # Stores a RoboDK pose made from position and rotation values.
        pose_values[0],  # Adds one item to the multi-line value.
        pose_values[1],  # Adds one item to the multi-line value.
        pose_values[2],  # Adds one item to the multi-line value.
        np.radians(pose_values[3]),  # Adds one item to the multi-line value.
        np.radians(pose_values[4]),  # Adds one item to the multi-line value.
        np.radians(pose_values[5]),  # Adds one item to the multi-line value.
    ])  # Closes the multi-line code started above.

    return robodk_mat_to_numpy(pose)  # Gives this result back to the part of the code that called it.


def make_local_offset_transform(offset_x, offset_y, offset_z):  # Creates a small movement matrix from X, Y, and Z offsets.
    transform = np.eye(4, dtype=np.float64)  # Stores a 4 by 4 movement table.
    transform[0, 3] = offset_x  # Runs this line as one small step in the program.
    transform[1, 3] = offset_y  # Runs this line as one small step in the program.
    transform[2, 3] = offset_z  # Runs this line as one small step in the program.
    return transform  # Gives this result back to the part of the code that called it.


def joints_to_list(joints_mat):  # Changes robot joints into a normal Python list.
    try:  # Tries the next steps because they might fail.
        return list(joints_mat.list())  # Gives this result back to the part of the code that called it.
    except Exception:  # Runs this part if something goes wrong.
        try:  # Tries the next steps because they might fail.
            return list(joints_mat)  # Gives this result back to the part of the code that called it.
        except Exception:  # Runs this part if something goes wrong.
            return [joints_mat[index] for index in range(len(joints_mat))]  # Gives this result back to the part of the code that called it.


def clamp(value, minimum_value, maximum_value):  # Keeps a number inside a safe minimum and maximum range.
    return max(minimum_value, min(value, maximum_value))  # Gives this result back to the part of the code that called it.


def print_transform(name, transform):  # Prints a transform matrix with a clear name.
    print(f"\n{name}:")  # Shows a message in the console.
    print(np.round(transform, 6))  # Shows a message in the console.
