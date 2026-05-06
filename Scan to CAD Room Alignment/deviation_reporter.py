import numpy as np


class DeviationReporter:
    """
    Compares detected scan planes with detected CAD planes and prints deviation in centimeters.
    """

    def __init__(self, plane_detector):
        self.plane_detector = plane_detector

    def get_oriented_plane_model(self, plane, label):
        a, b, c, d = plane["plane_model"]

        normal = np.array([a, b, c], dtype=np.float64)

        if label == "Floor" and normal[2] < 0:
            normal = -normal
            d = -d

        elif label == "Wall X-min" and normal[0] > 0:
            normal = -normal
            d = -d

        elif label == "Wall X-max" and normal[0] < 0:
            normal = -normal
            d = -d

        elif label == "Wall Y-min" and normal[1] > 0:
            normal = -normal
            d = -d

        elif label == "Wall Y-max" and normal[1] < 0:
            normal = -normal
            d = -d

        return np.array([normal[0], normal[1], normal[2], d], dtype=np.float64)

    def calculate_plane_deviation(self, scan_plane, cad_plane, label):
        cad_plane_model = self.get_oriented_plane_model(cad_plane, label)

        a, b, c, d = cad_plane_model
        normal = np.array([a, b, c], dtype=np.float64)

        normal_length = np.linalg.norm(normal)

        if normal_length == 0:
            raise Exception("Invalid CAD plane normal.")

        points = np.asarray(scan_plane["cloud"].points)

        signed_distances = (points @ normal + d) / normal_length
        absolute_distances = np.abs(signed_distances)

        return {
            "mean_abs_m": float(np.mean(absolute_distances)),
            "median_abs_m": float(np.median(absolute_distances)),
            "rmse_m": float(np.sqrt(np.mean(signed_distances ** 2))),
            "max_abs_m": float(np.max(absolute_distances)),
            "signed_mean_m": float(np.mean(signed_distances)),
            "scan_points": len(points),
        }

    def print_room_deviation_report(self, scan_pcd, cad_pcd):
        print("")
        print("Measuring wall and floor deviation...")

        scan_planes = self.plane_detector.detect_planes(scan_pcd)
        cad_planes = self.plane_detector.detect_planes(cad_pcd)

        cad_center = np.asarray(cad_pcd.points).mean(axis=0)

        scan_labelled = self.plane_detector.label_room_planes(
            scan_planes,
            cad_center
        )

        cad_labelled = self.plane_detector.label_room_planes(
            cad_planes,
            cad_center
        )

        labels = [
            "Floor",
            "Wall X-min",
            "Wall X-max",
            "Wall Y-min",
            "Wall Y-max",
        ]

        print("")
        print("Room deviation report:")
        print("Reference: STL/CAD model")
        print("Measured : PCD scan")
        print("Unit     : centimeters")
        print("")

        for label in labels:

            if label not in cad_labelled:
                print(f"{label}: CAD plane not found.")
                print("")
                continue

            if label not in scan_labelled:
                print(f"{label}: scan plane not found.")
                print("")
                continue

            result = self.calculate_plane_deviation(
                scan_labelled[label],
                cad_labelled[label],
                label
            )

            print(label)
            print(f"  Mean absolute difference : {result['mean_abs_m'] * 100:.2f} cm")
            print(f"  Median difference        : {result['median_abs_m'] * 100:.2f} cm")
            print(f"  RMSE                     : {result['rmse_m'] * 100:.2f} cm")
            print(f"  Maximum difference       : {result['max_abs_m'] * 100:.2f} cm")
            print(f"  Signed mean difference   : {result['signed_mean_m'] * 100:.2f} cm")
            print(f"  Scan points used         : {result['scan_points']}")
            print("")