import os
import shutil

import numpy as np
import pytest

from xrprimer.data_structure.camera import (
    FisheyeCameraParameter,
    OmniCameraParameter,
    PinholeCameraParameter,
)
from xrprimer.transform.camera.distortion import (
    undistort_camera,
    undistort_images,
    undistort_points,
)

input_dir = 'test/data/test_transform/test_camera'
output_dir = 'test/data/output/test_transform/test_camera/test_distortion'


# TODO: upload a pair of distorted image and its camera
@pytest.fixture(scope='module', autouse=True)
def fixture():
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=False)


def test_undistort_camera():
    # test only distort camera parameter
    input_json_path = os.path.join(input_dir, 'fisheye_param_at_origin.json')
    fisheye_cam_param = FisheyeCameraParameter(name='distort')
    fisheye_cam_param.load(input_json_path)
    intrinsic_backup = np.asarray(fisheye_cam_param.get_intrinsic())
    new_camera_param = undistort_camera(distorted_cam=fisheye_cam_param)
    assert isinstance(new_camera_param, PinholeCameraParameter)
    # test input not changed
    assert np.all(
        intrinsic_backup == np.asarray(fisheye_cam_param.get_intrinsic()))
    # test raises
    pytorch3d_cam = fisheye_cam_param.clone()
    pytorch3d_cam.convention = 'pytorch3d'
    with pytest.raises(NotImplementedError):
        new_camera_param, new_img = undistort_camera(
            distorted_cam=pytorch3d_cam)
    omni_cam = OmniCameraParameter(convention='opencv')
    with pytest.raises(AssertionError):
        new_camera_param = undistort_camera(distorted_cam=omni_cam)


def test_undistort_images():
    input_json_path = os.path.join(input_dir, 'fisheye_param_at_origin.json')
    fisheye_cam_param = FisheyeCameraParameter(name='distort')
    fisheye_cam_param.load(input_json_path)
    intrinsic_backup = np.asarray(fisheye_cam_param.get_intrinsic())
    test_image = np.ones(
        shape=[2, fisheye_cam_param.height, fisheye_cam_param.width, 3],
        dtype=np.uint8)
    image_backup = test_image.copy()
    new_camera_param, new_img = undistort_images(
        distorted_cam=fisheye_cam_param, image_array=test_image)
    # test input not changed
    assert np.all(
        intrinsic_backup == np.asarray(fisheye_cam_param.get_intrinsic()))
    assert np.all(image_backup == test_image)
    # test output
    assert isinstance(new_camera_param, PinholeCameraParameter)
    assert np.all(new_img.shape == test_image.shape)
    # test raises
    pytorch3d_cam = fisheye_cam_param.clone()
    pytorch3d_cam.convention = 'pytorch3d'
    with pytest.raises(NotImplementedError):
        new_camera_param, new_img = undistort_images(
            distorted_cam=pytorch3d_cam, image_array=test_image)


def test_undistort_points():
    input_json_path = os.path.join(input_dir, 'fisheye_param_at_origin.json')
    fisheye_cam_param = FisheyeCameraParameter(name='distort')
    fisheye_cam_param.load(input_json_path)
    intrinsic_backup = np.asarray(fisheye_cam_param.get_intrinsic())
    test_points = np.ones(shape=[10, 2])
    points_backup = test_points.copy()
    new_camera_param, new_points = undistort_points(
        distorted_cam=fisheye_cam_param, points=test_points)
    # test input not changed
    assert np.all(
        intrinsic_backup == np.asarray(fisheye_cam_param.get_intrinsic()))
    assert np.all(points_backup == test_points)
    # test output
    assert isinstance(new_camera_param, PinholeCameraParameter)
    assert np.all(new_points.shape == test_points.shape)
    # test another shape
    test_points = np.ones(shape=[4, 3, 2, 2])
    points_backup = test_points.copy()
    new_camera_param, new_points = undistort_points(
        distorted_cam=fisheye_cam_param, points=test_points)
    # test input not changed
    assert np.all(
        intrinsic_backup == np.asarray(fisheye_cam_param.get_intrinsic()))
    assert np.all(points_backup == test_points)
    # test output
    assert isinstance(new_camera_param, PinholeCameraParameter)
    assert np.all(new_points.shape == test_points.shape)
    # test raises
    pytorch3d_cam = fisheye_cam_param.clone()
    pytorch3d_cam.convention = 'pytorch3d'
    with pytest.raises(NotImplementedError):
        new_camera_param, new_points = undistort_points(
            distorted_cam=pytorch3d_cam, points=test_points)
