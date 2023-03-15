import os
import shutil

import numpy as np
import pytest

from xrprimer.visualization.matplotlib import plot_video
from xrprimer.visualization.palette import LinePalette, PointPalette

output_dir = 'tests/data/output/visualization/matplotlib/test_plot_video'


@pytest.fixture(scope='module', autouse=True)
def fixture() -> None:
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=False)


def test_output_args() -> None:
    point_palette = PointPalette(point_array=np.zeros(shape=(1, 3)), )
    n_frames = 10
    mframe_point_data = np.zeros(shape=(n_frames, 1, 3))
    for i in range(n_frames):
        mframe_point_data[i] += i * 10
    # test write video correctly
    output_path = os.path.join(output_dir, 'test_output_args_video.mp4')
    ret_value = plot_video(
        output_path=output_path,
        mframe_point_data=mframe_point_data,
        point_palette=point_palette,
        dpi=50)
    assert ret_value is None
    # test write video return array
    output_path = os.path.join(output_dir, 'test_output_args_video.mp4')
    ret_value = plot_video(
        output_path=output_path,
        mframe_point_data=mframe_point_data,
        point_palette=point_palette,
        return_array=True,
        dpi=50)
    assert ret_value.shape[0] == n_frames
    # test write img dir correctly
    output_path = os.path.join(output_dir, 'test_output_args_img_dir')
    plot_video(
        output_path=output_path,
        mframe_point_data=mframe_point_data,
        point_palette=point_palette,
        dpi=50)
    # test missing parent
    output_path = os.path.join(output_dir, 'test_output_args_missing_parent',
                               'test_output_args_missing_parent.mp4')
    with pytest.raises(FileNotFoundError):
        plot_video(
            output_path=output_path,
            mframe_point_data=mframe_point_data,
            point_palette=point_palette)
    # test not overwrite
    output_path = os.path.join(output_dir, 'test_output_args_video.mp4')
    with pytest.raises(FileExistsError):
        plot_video(
            output_path=output_path,
            mframe_point_data=mframe_point_data,
            point_palette=point_palette,
            overwrite=False)


def test_plot_args():
    n_frames = 10
    point_palette = PointPalette(point_array=np.zeros(shape=(1, 3)), )
    mframe_point_data = np.zeros(shape=(n_frames, 1, 3))
    for i in range(n_frames):
        mframe_point_data[i] += i * 2
    # x-y-z coordinates
    line_palette = LinePalette(
        point_array=np.zeros(shape=(4, 3)),
        conn_array=np.array([[0, 1], [0, 2], [0, 3]]),
        color_array=((255, 0, 0), (0, 255, 0), (0, 0, 255)))
    mframe_line_data = np.zeros(shape=(n_frames, 4, 3))
    mframe_line_data[:, 1, 0] += 5
    mframe_line_data[:, 2, 1] += 5
    mframe_line_data[:, 3, 2] += 5
    for i in range(n_frames):
        mframe_line_data[i] += i * 2
    # test plot points
    output_path = os.path.join(output_dir, 'plot_args_points.mp4')
    plot_video(
        output_path=output_path,
        mframe_point_data=mframe_point_data,
        point_palette=point_palette)
    # test plot lines
    output_path = os.path.join(output_dir, 'plot_args_lines.mp4')
    plot_video(
        output_path=output_path,
        mframe_line_data=mframe_line_data,
        line_palette=line_palette)
    # test plot both
    output_path = os.path.join(output_dir, 'plot_args_both.mp4')
    plot_video(
        output_path=output_path,
        mframe_point_data=mframe_point_data,
        point_palette=point_palette,
        mframe_line_data=mframe_line_data,
        line_palette=line_palette)
    # test plot neither
    output_path = os.path.join(output_dir, 'plot_args_neither.mp4')
    with pytest.raises(ValueError):
        plot_video(output_path=output_path)
