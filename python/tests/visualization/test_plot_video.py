import os
import shutil

import numpy as np
import pytest

from xrprimer.utils.ffmpeg_utils import (
    array_to_images,
    array_to_video,
    video_to_array,
)
from xrprimer.visualization.palette.point_palette import PointPalette
from xrprimer.visualization.plot_video import plot_video

output_dir = 'tests/data/output/visualization/test_plot_video'
img_dir = os.path.join(output_dir, 'input_img_dir')
video_path = os.path.join(output_dir, 'input_video.mp4')

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
        backgroud_arr=img_arr)
    assert ret_value is None
    # test write video return array
    output_path = os.path.join(output_dir, 'test_output_args_video.mp4')
    ret_value = plot_video(
        output_path=output_path,
        mframe_point_data=mframe_point_data,
        point_palette=point_palette,
        backgroud_arr=img_arr,
        return_array=True)
    assert ret_value.shape[0] == 5
    # test write img dir correctly
    output_path = os.path.join(output_dir, 'test_output_args_img_dir')
    plot_video(
        output_path=output_path,
        mframe_point_data=mframe_point_data,
        point_palette=point_palette,
        backgroud_arr=img_arr)
    # test missing parent
    output_path = os.path.join(output_dir, 'test_output_args_missing_parent',
                               'test_output_args_missing_parent.mp4')
    with pytest.raises(FileNotFoundError):
        plot_video(
            output_path=output_path,
            mframe_point_data=mframe_point_data,
            point_palette=point_palette,
            backgroud_arr=img_arr)
    # test not overwrite
    output_path = os.path.join(output_dir, 'test_output_args_video.mp4')
    with pytest.raises(FileExistsError):
        plot_video(
            output_path=output_path,
            mframe_point_data=mframe_point_data,
            point_palette=point_palette,
            backgroud_arr=img_arr,
            overwrite=False)


def test_backgroud_args():
    img_arr = video_to_array(video_path)
    point_palette = PointPalette(point_array=np.zeros(shape=(1, 2)), )
    mframe_point_data = np.zeros(shape=(5, 1, 2))
    for i in range(5):
        mframe_point_data[i] += i * 10
    # test backgroud_arr
    output_path = os.path.join(output_dir, 'backgroud_args_arr.mp4')
    plot_video(
        output_path=output_path,
        mframe_point_data=mframe_point_data,
        point_palette=point_palette,
        backgroud_arr=img_arr)
    # test backgroud_dir
    output_path = os.path.join(output_dir, 'backgroud_args_dir.mp4')
    plot_video(
        output_path=output_path,
        mframe_point_data=mframe_point_data,
        point_palette=point_palette,
        backgroud_dir=img_dir)
    # test backgroud_video
    output_path = os.path.join(output_dir, 'backgroud_args_video.mp4')
    plot_video(
        output_path=output_path,
        mframe_point_data=mframe_point_data,
        point_palette=point_palette,
        backgroud_video=video_path)
    # test resolution
    output_path = os.path.join(output_dir, 'backgroud_args_resolution.mp4')
    plot_video(
        output_path=output_path,
        mframe_point_data=mframe_point_data,
        point_palette=point_palette,
        height=64,
        width=128)
