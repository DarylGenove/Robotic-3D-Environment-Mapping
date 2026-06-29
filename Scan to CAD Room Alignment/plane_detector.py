import copy
import numpy as np


class PlaneDetector:
    """
    Detects and classifies planes in point clouds.
    """

    def __init__(self, config):
        self.config = config

    def detect_planes(self, point_cloud, max_planes=None):
        if max_planes is None:
            max_planes = self.config.MAX_PLANES_TO_CHECK

        remaining = copy.deepcopy(point_cloud)
        planes = []

        for _ in range(max_planes):

            if len(remaining.points) < self.config.MIN_PLANE_POINTS:
                break

            plane_model, inliers = remaining.segment_plane(
                distance_threshold=self.config.PLANE_DISTANCE_THRESHOLD,
                ransac_n=self.config.PLANE_RANSAC_N,
                num_iterations=self.config.PLANE_NUM_ITERATIONS
            )

            if len(inliers) < self.config.MIN_PLANE_POINTS:
                break

            a, b, c, d = plane_model

            normal = np.array([a, b, c], dtype=np.float64)
            normal = normal / np.linalg.norm(normal)

            plane_cloud = remaining.select_by_index(inliers)
            points = np.asarray(plane_cloud.points)
            centroid = points.mean(axis=0)

            planes.append({
                "plane_model": plane_model,
                "normal": normal,
                "centroid": centroid,
                "n_points": len(inliers),
                "cloud": plane_cloud,
            })

            remaining = remaining.select_by_index(inliers, invert=True)

        return planes

    def classify_floor_and_walls(self, planes):
        floor = None
        walls = []

        for plane in planes:
            normal = plane["normal"]

            horizontal_score = abs(
                np.dot(normal, np.array([0.0, 0.0, 1.0]))
            )

            if horizontal_score > 0.75:
                if floor is None or plane["centroid"][2] < floor["centroid"][2]:
                    floor = plane

            elif horizontal_score < 0.25:
                walls.append(plane)

        if floor is None:
            raise Exception("No floor plane found.")

        if len(walls) == 0:
            raise Exception("No wall plane found.")

        return floor, walls

    def label_room_planes(self, planes, room_center):
        labelled_planes = {}

        horizontal_planes = []
        vertical_planes = []

        for plane in planes:
            normal = plane["normal"]

            horizontal_score = abs(
                np.dot(normal, np.array([0.0, 0.0, 1.0]))
            )

            if horizontal_score > 0.75:
                horizontal_planes.append(plane)

            elif horizontal_score < 0.25:
                vertical_planes.append(plane)

        if len(horizontal_planes) > 0:
            floor = min(horizontal_planes, key=lambda p: p["centroid"][2])
            labelled_planes["Floor"] = floor

        for plane in vertical_planes:
            normal = plane["normal"]
            centroid = plane["centroid"]

            if abs(normal[0]) >= abs(normal[1]):
                if centroid[0] < room_center[0]:
                    label = "Wall X-min"
                else:
                    label = "Wall X-max"
            else:
                if centroid[1] < room_center[1]:
                    label = "Wall Y-min"
                else:
                    label = "Wall Y-max"

            if label not in labelled_planes:
                labelled_planes[label] = plane
            else:
                if plane["n_points"] > labelled_planes[label]["n_points"]:
                    labelled_planes[label] = plane

        return labelled_planes