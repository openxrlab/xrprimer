import os
import shutil

import cv2
import numpy as np
import pytest

from xrprimer.visualization.matplotlib import plot_frame
from xrprimer.visualization.palette.line_palette import LinePalette
from xrprimer.visualization.palette.point_palette import PointPalette

input_dir = 'tests/data/visualization/matplotlib/test_plot_frame'
output_dir = 'tests/data/output/visualization/matplotlib/test_plot_frame'
RGB_COLORS = dict(
    red=[255, 0, 0],
    green=[0, 255, 0],
    blue=[0, 0, 255],
)


@pytest.fixture(scope='module', autouse=True)
def fixture():
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=False)


def test_plot_points():
    # test default marksize, R/G/B points
    start_locations = np.array([10.0, 10.0, 10.0])
    visual_range = np.array([[0, 150], [0, 150], [0, 150]])
    for color_str, color_list in RGB_COLORS.items():
        location_list = []
        for offset in [1, 5, 10, 20]:
            location = start_locations + 5 * np.array([offset, offset, offset])
            location_list.append(location)
        point_palette = PointPalette(
            point_array=np.asarray(location_list), color_array=color_list)
        img_arr = plot_frame(
            point_palette=point_palette, visual_range=visual_range)
        cv2.imwrite(
            os.path.join(output_dir, f'{color_str}_manual_markersize.jpg'),
            img_arr)
    # test mask
    point_palette = PointPalette(
        point_array=[[20, 20, 1], [620, 20, 1], [20, 460, 1], [620, 460, 1]],
        color_array=[255, 0, 0])
    img_arr = plot_frame(point_palette=point_palette)
    cv2.imwrite(os.path.join(output_dir, 'points_before_mask.jpg'), img_arr)
    point_palette.set_point_mask([0, 1, 1, 1])
    img_arr = plot_frame(point_palette=point_palette)
    cv2.imwrite(os.path.join(output_dir, 'points_after_mask.jpg'), img_arr)


def test_plot_lines():
    # test default linewidth, R/G/B lines
    for color_str, color_list in RGB_COLORS.items():
        start_location = np.array([10.0, 10.0, 10.0])
        offset = np.array([20, 20, 20])
        point_array = np.array([start_location, start_location + offset])
        line_palette = LinePalette(
            conn_array=[0, 1], point_array=point_array, color_array=color_list)
        img_arr = plot_frame(line_palette=line_palette)
        cv2.imwrite(
            os.path.join(output_dir, f'{color_str}_default_linewidth.jpg'),
            img_arr)
    # test mask
    line_palette = LinePalette(
        conn_array=[[0, 1], [2, 3]],
        point_array=[[20.0, 20.0, 1.0], [620.0, 20.0, 1.0], [20.0, 460.0, 1.0],
                     [620.0, 460.0, 1.0]],
        color_array=[255, 0, 0])
    img_arr = plot_frame(line_palette=line_palette)
    cv2.imwrite(os.path.join(output_dir, 'lines_before_mask.jpg'), img_arr)
    line_palette.set_conn_mask([0, 1])
    img_arr = plot_frame(line_palette=line_palette)
    cv2.imwrite(os.path.join(output_dir, 'lines_after_mask.jpg'), img_arr)


def test_points_and_lines():
    point_palette = PointPalette(
        point_array=[[300, 300, 300], [200, 400, 200], [400, 400, 400]],
        color_array=[255, 0, 0])
    line_palette = LinePalette(
        conn_array=[[0, 1], [1, 2], [2, 0]],
        point_array=point_palette.point_array,
        color_array=[0, 255, 0])
    img_arr = plot_frame(
        point_palette=point_palette, line_palette=line_palette)
    cv2.imwrite(os.path.join(output_dir, 'points_and_lines.jpg'), img_arr)


test_points_and_lines()
