import os
import shutil

import numpy as np
import pytest

from xrprimer.utils.ffmpeg_utils import (
    array_to_images,
    array_to_video,
    video_to_array,
)
from xrprimer.visualization.opencv.plot_video import plot_video
from xrprimer.visualization.palette import LinePalette, PointPalette

output_dir = 'tests/data/output/visualization/opencv/test_plot_video'
img_dir = os.path.join(output_dir, 'input_img_dir')
video_path = os.path.join(output_dir, 'input_video.mp4')


@pytest.fixture(scope='module', autouse=True)
def fixture():
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=False)
    img_arr = np.zeros(shape=(5, 64, 128, 3), dtype=np.uint8)
    for i in range(5):
        img_arr[i] = 50 * i
    array_to_images(image_array=img_arr, output_folder=img_dir)
    array_to_video(image_array=img_arr, output_path=video_path)


def test_output_args():
    img_arr = video_to_array(video_path)
    point_palette = PointPalette(point_array=np.zeros(shape=(1, 2)), )
    mframe_point_data = np.zeros(shape=(5, 1, 2))
    for i in range(5):
        mframe_point_data[i] += i * 10
    # test write video correctly
    output_path = os.path.join(output_dir, 'test_output_args_video.mp4')
    ret_value = plot_video(
        output_path=output_path,
        mframe_point_data=mframe_point_data,
        point_palette=point_palette,
        background_arr=img_arr)
    assert ret_value is None
    # test write video return array
    output_path = os.path.join(output_dir, 'test_output_args_video.mp4')
    ret_value = plot_video(
        output_path=output_path,
        mframe_point_data=mframe_point_data,
        point_palette=point_palette,
        background_arr=img_arr,
        return_array=True)
    assert ret_value.shape[0] == 5
    # test write video fps
    output_path = os.path.join(output_dir, 'test_output_args_fps.mp4')
    ret_value = plot_video(
        output_path=output_path,
        mframe_point_data=mframe_point_data,
        point_palette=point_palette,
        background_arr=img_arr,
        fps=0.9,
        return_array=True)
    assert ret_value.shape[0] == 5
    # test write img dir correctly
    output_path = os.path.join(output_dir, 'test_output_args_img_dir')
    plot_video(
        output_path=output_path,
        mframe_point_data=mframe_point_data,
        point_palette=point_palette,
        background_arr=img_arr)
    # test write img dir img_format
    output_path = os.path.join(output_dir, 'test_output_args_img_format')
    plot_video(
        output_path=output_path,
        mframe_point_data=mframe_point_data,
        point_palette=point_palette,
        img_format='%02d.jpg',
        background_arr=img_arr)
    # test missing parent
    output_path = os.path.join(output_dir, 'test_output_args_missing_parent',
                               'test_output_args_missing_parent.mp4')
    with pytest.raises(FileNotFoundError):
        plot_video(
            output_path=output_path,
            mframe_point_data=mframe_point_data,
            point_palette=point_palette,
            background_arr=img_arr)
    # test not overwrite
    output_path = os.path.join(output_dir, 'test_output_args_video.mp4')
    with pytest.raises(FileExistsError):
        plot_video(
            output_path=output_path,
            mframe_point_data=mframe_point_data,
            point_palette=point_palette,
            background_arr=img_arr,
            overwrite=False)


def test_background_args():
    img_arr = video_to_array(video_path)
    point_palette = PointPalette(point_array=np.zeros(shape=(1, 2)), )
    mframe_point_data = np.zeros(shape=(5, 1, 2))
    for i in range(5):
        mframe_point_data[i] += i * 10
    # test background_arr
    output_path = os.path.join(output_dir, 'background_args_arr.mp4')
    plot_video(
        output_path=output_path,
        mframe_point_data=mframe_point_data,
        point_palette=point_palette,
        background_arr=img_arr)
    # test background_dir
    output_path = os.path.join(output_dir, 'background_args_dir.mp4')
    plot_video(
        output_path=output_path,
        mframe_point_data=mframe_point_data,
        point_palette=point_palette,
        background_dir=img_dir)
    # test background_video
    output_path = os.path.join(output_dir, 'background_args_video.mp4')
    plot_video(
        output_path=output_path,
        mframe_point_data=mframe_point_data,
        point_palette=point_palette,
        background_video=video_path)
    # test resolution
    output_path = os.path.join(output_dir, 'background_args_resolution.mp4')
    plot_video(
        output_path=output_path,
        mframe_point_data=mframe_point_data,
        point_palette=point_palette,
        height=64,
        width=128)
    # test duplicate source
    output_path = os.path.join(output_dir, 'background_duplicate_source.mp4')
    with pytest.raises(ValueError):
        plot_video(
            output_path=output_path,
            mframe_point_data=mframe_point_data,
            point_palette=point_palette,
            background_video=video_path,
            height=64,
            width=128)
    # test zero source
    output_path = os.path.join(output_dir, 'background_duplicate_source.mp4')
    with pytest.raises(ValueError):
        plot_video(
            output_path=output_path,
            mframe_point_data=mframe_point_data,
            point_palette=point_palette)


def test_plot_args():
    img_arr = video_to_array(video_path)
    point_palette = PointPalette(point_array=np.zeros(shape=(1, 2)), )
    mframe_point_data = np.zeros(shape=(5, 1, 2))
    for i in range(5):
        mframe_point_data[i] += i * 10
    line_palette = LinePalette(
        point_array=np.zeros(shape=(2, 2)), conn_array=np.array([[0, 1]]))
    mframe_line_data = np.zeros(shape=(5, 2, 2))
    mframe_line_data[:, 0, 0] += 5
    mframe_line_data[:, 0, 1] += 10
    mframe_line_data[:, 1, 0] += 10
    mframe_line_data[:, 1, 1] += 5
    for i in range(5):
        mframe_line_data[i] += i * 10
    # test plot points
    output_path = os.path.join(output_dir, 'plot_args_points.mp4')
    plot_video(
        output_path=output_path,
        mframe_point_data=mframe_point_data,
        point_palette=point_palette,
        background_arr=img_arr)
    # test plot lines
    output_path = os.path.join(output_dir, 'plot_args_lines.mp4')
    plot_video(
        output_path=output_path,
        mframe_line_data=mframe_line_data,
        line_palette=line_palette,
        background_arr=img_arr)
    # test plot both
    output_path = os.path.join(output_dir, 'plot_args_both.mp4')
    plot_video(
        output_path=output_path,
        mframe_point_data=mframe_point_data,
        point_palette=point_palette,
        mframe_line_data=mframe_line_data,
        line_palette=line_palette,
        background_arr=img_arr)
    # test plot neither
    output_path = os.path.join(output_dir, 'plot_args_neither.mp4')
    with pytest.raises(ValueError):
        plot_video(output_path=output_path, background_arr=img_arr)
