import os
import shutil

import cv2
import numpy as np
import pytest

from xrprimer.utils.ffmpeg_utils import (
    VideoInfoReader,
    VideoWriter,
    array_to_images,
    array_to_video,
    images_to_array,
    images_to_array_opencv,
    pad_for_libx264,
    video_to_array,
)

input_dir = 'test/data/utils/test_ffmpeg_utils'
output_dir = 'test/data/output/utils/test_ffmpeg_utils'


@pytest.fixture(scope='module', autouse=True)
def fixture():
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=False)
    test_video_writter = VideoWriter(
        os.path.join(output_dir, 'test_video.mp4'),
        resolution=[256, 512],
        fps=15)
    for _ in range(75):
        test_video_writter.write(
            np.random.randint(
                low=0, high=255, size=(256, 512, 3), dtype=np.uint8))
    test_video_writter.close()
    test_frames_dir = os.path.join(output_dir, 'test_frames')
    os.mkdir(test_frames_dir)
    for i in range(25):
        test_img = np.random.randint(
            low=0, high=255, size=(256, 512, 3), dtype=np.uint8)
        cv2.imwrite(
            filename=os.path.join(test_frames_dir, f'{i:06d}.png'),
            img=test_img)


def test_pad_for_libx264():
    gray_image = np.ones(shape=[25, 45], dtype=np.uint8)
    pad_gray_image = pad_for_libx264(gray_image)
    assert pad_gray_image.shape[0] % 2 == 0
    assert pad_gray_image.shape[1] % 2 == 0

    rgb_image = np.ones(shape=[25, 45, 3], dtype=np.uint8)
    pad_rgb_image = pad_for_libx264(rgb_image)
    assert pad_rgb_image.shape[0] % 2 == 0
    assert pad_rgb_image.shape[1] % 2 == 0

    gray_array = np.ones(shape=[11, 25, 45], dtype=np.uint8)
    pad_gray_array = pad_for_libx264(gray_array)
    assert pad_gray_array.shape[1] % 2 == 0
    assert pad_gray_array.shape[2] % 2 == 0

    rgb_array = np.ones(shape=[11, 25, 45, 3], dtype=np.uint8)
    pad_rgb_array = pad_for_libx264(rgb_array)
    assert pad_rgb_array.shape[1] % 2 == 0


def test_video_to_array():
    test_video_path = os.path.join(output_dir, 'test_video.mp4')
    # test images_to_array
    img_arr = video_to_array(test_video_path)
    assert img_arr.shape == (75, 256, 512, 3)
    img_arr = video_to_array(test_video_path, resolution=(128, 128))
    assert img_arr.shape == (75, 128, 128, 3)
    img_arr = video_to_array(test_video_path, start=0, end=20)
    assert img_arr.shape == (20, 256, 512, 3)


def test_images_to_array():
    test_frames_dir = os.path.join(output_dir, 'test_frames')
    # test images_to_array
    img_arr = images_to_array(test_frames_dir)
    assert img_arr.shape == (25, 256, 512, 3)
    img_arr = images_to_array(test_frames_dir, resolution=(128, 128))
    assert img_arr.shape == (25, 128, 128, 3)
    img_arr = images_to_array(
        test_frames_dir, start=0, end=20, img_format=None)
    assert img_arr.shape == (20, 256, 512, 3)
    # test images_to_array_opencv
    img_arr = images_to_array_opencv(test_frames_dir)
    assert img_arr.shape == (25, 256, 512, 3)
    img_arr = images_to_array_opencv(test_frames_dir, resolution=(128, 128))
    assert img_arr.shape == (25, 128, 128, 3)
    img_arr = images_to_array_opencv(test_frames_dir, start=0, end=20)
    assert img_arr.shape == (20, 256, 512, 3)
    img_arr = images_to_array_opencv(test_frames_dir, start=0, end=20)
    assert img_arr.shape == (20, 256, 512, 3)


def test_array_to_images():
    img_arr = np.random.randint(
        low=0, high=255, size=(3, 256, 512, 3), dtype=np.uint8)
    # test number of images
    path = os.path.join(output_dir, 'test_array_to_images')
    array_to_images(img_arr, output_folder=path)
    assert len(os.listdir(path)) == 3
    # test img_format
    path = os.path.join(output_dir, 'test_array_to_images_format')
    array_to_images(img_arr, output_folder=path, img_format='frame_%06d.jpg')
    assert sorted(os.listdir(path))[0] == 'frame_000000.jpg'
    # test resolution
    with pytest.raises(NotImplementedError):
        path = os.path.join(output_dir, 'test_array_to_images_resolution')
        array_to_images(img_arr, output_folder=path, resolution=(512, 1024))


def test_array_to_video():
    img_arr = np.random.randint(
        low=0, high=255, size=(3, 256, 512, 3), dtype=np.uint8)
    # test number of frames
    path = os.path.join(output_dir, 'test_array_to_video.mp4')
    array_to_video(img_arr, output_path=path)
    reader = VideoInfoReader(path)
    assert int(reader['nb_frames']) == 3
    assert int(reader['height']) == 256
    assert int(reader['width']) == 512
    # test resolution
    path = os.path.join(output_dir, 'test_array_to_video_resolution.mp4')
    array_to_video(img_arr, output_path=path, resolution=(128, 256))
    reader = VideoInfoReader(path)
    assert int(reader['height']) == 128
    assert int(reader['width']) == 256
    # test fps
    path = os.path.join(output_dir, 'test_array_to_video_fps.mp4')
    array_to_video(img_arr, output_path=path, fps=10)
    reader = VideoInfoReader(path)
    assert int(reader['nb_frames']) == 3
    assert int(reader['avg_frame_rate'].split('/')[0]) == 10
