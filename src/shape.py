from svgpathtools import parse_path, Path
from shapely.geometry import Point, Polygon
import numpy as np


svg_path_data = ("M322.2962,0C229.2242,0,0,229.2166,0,322.2924s229.2242,322.2962,322.2962,322.2962,322.3-229.2242,"
                 "322.3-322.2962S415.372,0,322.2962,0Zm-50.2246,"
                 "506.5903c-39.2474-10.6949-144.7678-195.2751-134.0713-234.5224,10.6966-39.2491,195.2751-144.7661,"
                 "234.5224-134.0695,39.2491,10.6949,144.7696,195.2716,134.073,234.5207-10.6966,39.2491-195.2768,"
                 "144.7678-234.5242,134.0713Z")


def scale_path(path_data, scale_factor):
    path = parse_path(path_data)
    new_path = Path()
    for segment in path:
        scaled_segment = segment.scaled(scale_factor, scale_factor)
        new_path.append(scaled_segment)
    return new_path


def parse_svg_to_polygon(path, num_points=100):
    points = []

    for segment in path:
        for t in range(num_points + 1):
            point = segment.point(t / num_points)
            points.append((point.real, point.imag))

    return Polygon(points)


scaled_path = scale_path(svg_path_data, .39)
polygon = parse_svg_to_polygon(scaled_path)


def is_point_in_shape(x, y, shape=polygon):
    point = Point(x, y)
    return shape.contains(point)


def rotate_point(x, y, angle, cx, cy):
    # Convert angle to radians
    angle_rad = np.radians(angle)
    # Translate point to origin
    x -= cx
    y -= cy
    # Apply rotation matrix
    x_rot = x * np.cos(angle_rad) - y * np.sin(angle_rad)
    y_rot = x * np.sin(angle_rad) + y * np.cos(angle_rad)
    # Translate point back
    x_rot += cx
    y_rot += cy
    return x_rot, y_rot


def rotate_polygon(angle, shape=polygon):
    # Calculate centroid
    centroid = shape.centroid
    cx, cy = centroid.x, centroid.y
    # Rotate all points
    rotated_points = [
        rotate_point(x, y, angle, cx, cy)
        for x, y in shape.exterior.coords
    ]
    return Polygon(rotated_points)

