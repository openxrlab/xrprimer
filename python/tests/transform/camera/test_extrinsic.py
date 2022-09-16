import os
import shutil

import cv2
import mmcv
import numpy as np
import pytest

from xrprimer.data_structure.camera import PinholeCameraParameter
from xrprimer.ops.projection.builder import build_projector
from xrprimer.transform.camera.extrinsic import rotate_camera, translate_camera

input_dir = 'tests/data/transform/camera/test_extrinsic'
output_dir = 'tests/data/output/transform/camera/test_extrinsic'


@pytest.fixture(scope='module', autouse=True)
def fixture():
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=False)


def test_rotate_camera():
    src_cam_param = PinholeCameraParameter.fromfile(
        os.path.join(input_dir, 'cam_006.json'))
    flip_rot_mat = np.array([
        [1, 0, 0],
        [0, -0.598, 0.801],
        [0, -0.801, -0.598],
    ])
    # test extrinsic direction
    rot_cam_param = rotate_camera(src_cam_param, flip_rot_mat)
    assert rot_cam_param.world2cam == src_cam_param.world2cam
    src_cam_param.inverse_extrinsic()
    rot_inv_cam_param = rotate_camera(src_cam_param, flip_rot_mat)
    assert rot_inv_cam_param.world2cam == src_cam_param.world2cam
    # visualize with projection
    keypoints3d = np.load(
        os.path.join(input_dir, 'keypoints3d.npz'), allow_pickle=True)
    keypoints3d = dict(keypoints3d)
    projector_config = dict(
        mmcv.Config.fromfile('config/ops/projection/opencv_projector.py'))
    projector_config['camera_parameters'] = [
        rot_cam_param,
    ]
    projector = build_projector(projector_config)
    points3d = np.array(keypoints3d['keypoints'][0, 0, :, :3])
    for point_idx, point_loc in enumerate(points3d):
        points3d[point_idx] = np.matmul(flip_rot_mat, point_loc)
    points3d_mask = np.expand_dims(keypoints3d['mask'][0, 0, :], axis=-1)
    projected_points = projector.project(points3d, points_mask=points3d_mask)
    canvas = cv2.imread(os.path.join(input_dir, '000006.png'))
    valid_idxs = np.where(points3d_mask == 1)
    for point_idx in valid_idxs[0]:
        cv2.circle(
            img=canvas,
            center=projected_points[0, point_idx].astype(np.int32),
            radius=2,
            color=(0, 0, 255))
    cv2.imwrite(
        filename=os.path.join(output_dir, 'projected_kps_rotation.jpg'),
        img=canvas)


def test_translate_camera():
    src_cam_param = PinholeCameraParameter.fromfile(
        os.path.join(input_dir, 'cam_006.json'))
    translation = np.array([200, 0, 0], )
    # test extrinsic direction
    transl_cam_param = translate_camera(src_cam_param, translation)
    assert transl_cam_param.world2cam == src_cam_param.world2cam
    src_cam_param.inverse_extrinsic()
    transl_inv_cam_param = translate_camera(src_cam_param, translation)
    assert transl_inv_cam_param.world2cam == src_cam_param.world2cam
    # visualize with projection
    keypoints3d = np.load(
        os.path.join(input_dir, 'keypoints3d.npz'), allow_pickle=True)
    keypoints3d = dict(keypoints3d)
    projector_config = dict(
        mmcv.Config.fromfile('config/ops/projection/opencv_projector.py'))
    projector_config['camera_parameters'] = [
        transl_cam_param,
    ]
    projector = build_projector(projector_config)
    points3d = np.array(keypoints3d['keypoints'][0, 0, :, :3])
    points3d = points3d + np.expand_dims(translation, 0).repeat(
        len(points3d), 0)
    points3d_mask = np.expand_dims(keypoints3d['mask'][0, 0, :], axis=-1)
    projected_points = projector.project(points3d, points_mask=points3d_mask)
    canvas = cv2.imread(os.path.join(input_dir, '000006.png'))
    valid_idxs = np.where(points3d_mask == 1)
    for point_idx in valid_idxs[0]:
        cv2.circle(
            img=canvas,
            center=projected_points[0, point_idx].astype(np.int32),
            radius=2,
            color=(0, 0, 255))
    cv2.imwrite(
        filename=os.path.join(output_dir, 'projected_kps_translation.jpg'),
        img=canvas)
