import os
import shutil

import cv2
import numpy as np
import pytest

from xrprimer.visualization.opencv import plot_frame
from xrprimer.visualization.palette.line_palette import LinePalette
from xrprimer.visualization.palette.point_palette import PointPalette

input_dir = 'tests/data/visualization/opencv/test_plot_frame'
output_dir = 'tests/data/output/visualization/opencv/test_plot_frame'
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
    # test manual radius, R/G/B points
    start_locations = np.array([
        [10.0, 10.0],
    ])
    for color_str, color_list in RGB_COLORS.items():
        point_palette = PointPalette(
            point_array=start_locations, color_array=color_list)
        canvas = np.ones(shape=[400, 400, 3], dtype=np.uint8)
        for point_radius in [1, 5, 10, 20]:
            location = start_locations + 5 * np.array(
                [point_radius, point_radius])
            point_palette.set_point_array(location)
            img_arr = plot_frame(
                point_palette=point_palette,
                background_arr=canvas,
                point_radius=point_radius)
        cv2.imwrite(
            os.path.join(output_dir, f'{color_str}_manual_radius.jpg'),
            img_arr)
    # test auto radius
    resolutions = dict(
        h1080=1080,
        h720=720,
        h480=480,
    )
    locations = np.array([
        [100.0, 10.0],
        [300.0, 10.0],
        [150.0, 30.0],
    ])
    for reso_str, reso_height in resolutions.items():
        point_palette = PointPalette(
            point_array=locations, color_array=[255, 0, 0])
        img_arr = plot_frame(
            point_palette=point_palette,
            width=reso_height / 9 * 16,
            height=reso_height,
            point_radius='auto')
        cv2.imwrite(
            os.path.join(output_dir, f'{reso_str}_auto_radius.jpg'), img_arr)
    # test mask
    point_palette = PointPalette(
        point_array=[[20, 20], [620, 20], [20, 460], [620, 460]],
        color_array=[255, 0, 0])
    img_arr = plot_frame(
        point_palette=point_palette,
        width=640,
        height=480,
        point_radius='auto')
    cv2.imwrite(os.path.join(output_dir, 'points_before_mask.jpg'), img_arr)
    point_palette.set_point_mask([0, 1, 1, 1])
    img_arr = plot_frame(
        point_palette=point_palette,
        width=640,
        height=480,
        point_radius='auto')
    cv2.imwrite(os.path.join(output_dir, 'points_after_mask.jpg'), img_arr)


def test_plot_lines():
    # test manual thickness, R/G/B lines
    for color_str, color_list in RGB_COLORS.items():
        start_location = np.array([10.0, 10.0], )
        line_palette = LinePalette(
            conn_array=[0, 1],
            point_array=np.zeros(shape=[2, 2]),
            color_array=color_list)
        canvas = np.ones(shape=[400, 400, 3], dtype=np.uint8)
        for thickness in [1.0, 5.0, 10.0, 20.0]:
            line_len = start_location[0] / 2
            offset = np.array([line_len, -line_len])
            point_array = np.array(
                [start_location + offset, start_location - offset])
            line_palette.set_point_array(point_array)
            img_arr = plot_frame(
                line_palette=line_palette,
                background_arr=canvas,
                line_thickness=thickness)
            start_location = start_location + \
                10 * np.array([thickness, thickness])
        cv2.imwrite(
            os.path.join(output_dir, f'{color_str}_manual_thickness.jpg'),
            img_arr)
    # test auto thickness
    resolutions = dict(
        h1080=1080,
        h720=720,
        h480=480,
    )
    locations = np.array([
        [10, 10],
        [100, 100],
    ])
    for reso_str, reso_height in resolutions.items():
        line_palette = LinePalette(
            conn_array=[0, 1],
            point_array=locations,
            color_array=[255.0, 0.0, 0.0])
        img_arr = plot_frame(
            line_palette=line_palette,
            width=reso_height / 9 * 16,
            height=reso_height,
            line_thickness='auto')
        cv2.imwrite(
            os.path.join(output_dir, f'{reso_str}_auto_thickness.jpg'),
            img_arr)
    # test mask
    line_palette = LinePalette(
        conn_array=[[0, 1], [2, 3]],
        point_array=[[20.0, 20.0], [620.0, 20.0], [20.0, 460.0],
                     [620.0, 460.0]],
        color_array=[255, 0, 0])
    img_arr = plot_frame(
        line_palette=line_palette,
        width=640,
        height=480,
        line_thickness='auto')
    cv2.imwrite(os.path.join(output_dir, 'lines_before_mask.jpg'), img_arr)
    line_palette.set_conn_mask([0, 1])
    img_arr = plot_frame(
        line_palette=line_palette,
        width=640,
        height=480,
        line_thickness='auto')
    cv2.imwrite(os.path.join(output_dir, 'lines_after_mask.jpg'), img_arr)


def test_points_and_lines():
    point_palette = PointPalette(
        point_array=[[300, 300], [200, 400], [400, 400]],
        color_array=[255, 0, 0])
    line_palette = LinePalette(
        conn_array=[[0, 1], [1, 2], [2, 0]],
        point_array=point_palette.point_array,
        color_array=[0, 255, 0])
    canvas = np.ones(shape=[640, 480], dtype=np.uint8)
    img_arr = plot_frame(
        point_palette=point_palette,
        line_palette=line_palette,
        background_arr=canvas)
    cv2.imwrite(os.path.join(output_dir, 'points_and_lines.jpg'), img_arr)
