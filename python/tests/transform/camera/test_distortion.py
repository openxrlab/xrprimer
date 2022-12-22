import os
import shutil

import cv2
import numpy as np
import pytest

from xrprimer.data_structure.camera import (
    FisheyeCameraParameter,
    OmniCameraParameter,
    PinholeCameraParameter,
)
from xrprimer.transform.camera.distortion import (
    FastImageUndistortor,
    undistort_camera,
    undistort_images,
    undistort_points,
)

input_dir = 'tests/data/transform/camera/test_distortion'
output_dir = 'tests/data/output/transform/camera/test_distortion'


@pytest.fixture(scope='module', autouse=True)
def fixture():
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=False)


def test_undistort_camera():
    # test only distort camera parameter
    input_json_path = os.path.join(input_dir, 'dist_fisheye_param.json')
    fisheye_param = FisheyeCameraParameter(name='distort')
    fisheye_param.load(input_json_path)
    fisheye_param.set_KRT(R=np.eye(3))
    intrinsic_backup = np.asarray(fisheye_param.get_intrinsic())
    new_cam_param = undistort_camera(distorted_cam=fisheye_param)
    assert isinstance(new_cam_param, PinholeCameraParameter)
    # test input not changed
    assert np.all(
        intrinsic_backup == np.asarray(fisheye_param.get_intrinsic()))
    # test raises
    pytorch3d_cam = fisheye_param.clone()
    pytorch3d_cam.convention = 'pytorch3d'
    with pytest.raises(NotImplementedError):
        new_cam_param, new_img = undistort_camera(distorted_cam=pytorch3d_cam)
    omni_cam = OmniCameraParameter(convention='opencv')
    with pytest.raises(AssertionError):
        new_cam_param = undistort_camera(distorted_cam=omni_cam)


def test_undistort_images():
    fisheye_param = FisheyeCameraParameter(name='distort')
    fisheye_param.load(os.path.join(input_dir, 'dist_fisheye_param.json'))
    fisheye_param.set_KRT(R=np.eye(3))
    intrinsic_backup = np.asarray(fisheye_param.get_intrinsic())
    test_img = cv2.imread(filename=os.path.join(input_dir, 'dist_img.png'))
    test_imgs = np.expand_dims(test_img, axis=0)
    test_imgs = np.repeat(test_imgs, 2, axis=0)
    img_backup = test_img.copy()
    new_cam_param, new_img = undistort_images(
        distorted_cam=fisheye_param, image_array=test_imgs)
    # test input not changed
    assert np.all(
        intrinsic_backup == np.asarray(fisheye_param.get_intrinsic()))
    assert np.all(img_backup == test_imgs)
    # test output
    assert isinstance(new_cam_param, PinholeCameraParameter)
    assert np.all(new_img.shape == test_imgs.shape)
    undist_img = new_img[0]
    cv2.imwrite(
        filename=os.path.join(output_dir, 'undist_img.jpg'), img=undist_img)
    # test raises
    pytorch3d_cam = fisheye_param.clone()
    pytorch3d_cam.convention = 'pytorch3d'
    with pytest.raises(NotImplementedError):
        new_cam_param, new_img = undistort_images(
            distorted_cam=pytorch3d_cam, image_array=test_imgs)


def test_undistort_points():
    fisheye_param = FisheyeCameraParameter(name='distort')
    fisheye_param.load(os.path.join(input_dir, 'dist_fisheye_param.json'))
    fisheye_param.set_KRT(R=np.eye(3))
    intrinsic_backup = np.asarray(fisheye_param.get_intrinsic())
    corners_points = np.array([[791, 78], [1196, 19], [1215, 494], [1167, 534],
                               [851, 529], [808, 491]],
                              dtype=np.int32)
    points_backup = corners_points.copy()
    new_cam_param, new_points = undistort_points(
        distorted_cam=fisheye_param, points=corners_points)
    # test input not changed
    assert np.all(
        intrinsic_backup == np.asarray(fisheye_param.get_intrinsic()))
    assert np.all(points_backup == corners_points)
    # test output
    assert isinstance(new_cam_param, PinholeCameraParameter)
    assert np.all(new_points.shape == corners_points.shape)
    # visualize results
    distort_img = cv2.imread(filename=os.path.join(input_dir, 'dist_img.png'))
    _, new_img = undistort_images(
        distorted_cam=fisheye_param,
        image_array=np.expand_dims(distort_img, axis=0))
    for point in corners_points.astype(np.int32):
        cv2.circle(img=distort_img, center=point, radius=3, color=(0, 0, 255))
    cv2.imwrite(
        filename=os.path.join(output_dir, 'dist_img_with_points.jpg'),
        img=distort_img)
    new_img = new_img[0]
    for point in new_points.astype(np.int32):
        cv2.circle(img=new_img, center=point, radius=3, color=(0, 0, 255))
    cv2.imwrite(
        filename=os.path.join(output_dir, 'undist_img_with_points.jpg'),
        img=new_img)
    # test another shape
    test_points = np.ones(shape=[4, 3, 2, 2])
    points_backup = test_points.copy()
    new_cam_param, new_points = undistort_points(
        distorted_cam=fisheye_param, points=test_points)
    # test input not changed
    assert np.all(
        intrinsic_backup == np.asarray(fisheye_param.get_intrinsic()))
    assert np.all(points_backup == test_points)
    # test output
    assert isinstance(new_cam_param, PinholeCameraParameter)
    assert np.all(new_points.shape == test_points.shape)
    # test raises
    pytorch3d_cam = fisheye_param.clone()
    pytorch3d_cam.convention = 'pytorch3d'
    with pytest.raises(NotImplementedError):
        new_cam_param, new_points = undistort_points(
            distorted_cam=pytorch3d_cam, points=test_points)


def test_fast_undistort_images():
    fisheye_param = FisheyeCameraParameter(name='distort')
    fisheye_param.load(os.path.join(input_dir, 'dist_fisheye_param.json'))
    fisheye_param.set_KRT(R=np.eye(3))
    intrinsic_backup = np.asarray(fisheye_param.get_intrinsic())
    test_img = cv2.imread(filename=os.path.join(input_dir, 'dist_img.png'))
    img_backup = test_img.copy()
    undistortor = FastImageUndistortor(fisheye_param=fisheye_param)
    undist_img = undistortor.undistort_image(test_img)
    # test input not changed
    assert np.all(
        intrinsic_backup == np.asarray(fisheye_param.get_intrinsic()))
    assert np.all(img_backup == test_img)
    assert np.all(undist_img.shape == test_img.shape)
    cv2.imwrite(
        filename=os.path.join(output_dir, 'fast_undist_img.jpg'),
        img=undist_img)
