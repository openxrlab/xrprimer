import glob
import os
import shutil

import cv2
import mmcv
import numpy as np
import pytest

from xrprimer.data_structure.camera import PinholeCameraParameter
from xrprimer.ops.triangulation.builder import build_triangulator  # noqa:E501

input_dir = 'tests/data/ops/test_triangulation'
output_dir = 'tests/data/output/ops/test_triangulation'


@pytest.fixture(scope='module', autouse=True)
def fixture():
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=False)


def test_opencv_triangulator():
    n_view = len(glob.glob(os.path.join(input_dir, '*.json')))
    kps2d_list = []
    mask_list = []
    for view_idx in range(n_view):
        npz_path = os.path.join(input_dir, f'keypoints_2d_{view_idx:02d}.npz')
        npz_dict = dict(np.load(npz_path, allow_pickle=True))
        kps2d_list.append(npz_dict['keypoints'][0, 0, :, :2])
        mask_list.append(npz_dict['mask'][0, 0, :])
    keypoints2d = np.asarray(kps2d_list)
    keypoints2d_mask = np.asarray(mask_list, dtype=keypoints2d.dtype)
    cam_param_list = []
    for view_idx in range(n_view):
        cam_param_path = os.path.join(input_dir, f'cam_{view_idx:03d}.json')
        cam_param = PinholeCameraParameter()
        cam_param.load(cam_param_path)
        cam_param_list.append(cam_param)
    triangulator_config = dict(
        mmcv.Config.fromfile(
            'config/ops/triangulation/opencv_triangulator.py'))
    triangulator_config['camera_parameters'] = cam_param_list
    triangulator = build_triangulator(triangulator_config)
    # test kp2d np
    keypoints3d = triangulator.triangulate(keypoints2d)
    assert keypoints3d.shape[0] == keypoints2d.shape[1]
    # test kp2d list
    keypoints3d = triangulator.triangulate(keypoints2d.tolist())
    assert keypoints3d.shape[0] == keypoints2d.shape[1]
    # test kp2d tuple
    keypoints3d = triangulator.triangulate(tuple(map(tuple, keypoints2d)))
    assert keypoints3d.shape[0] == keypoints2d.shape[1]
    # test mask np
    points_mask = np.ones_like(keypoints2d[..., 0:1])
    keypoints3d = triangulator.triangulate(
        points=keypoints2d, points_mask=points_mask)
    assert keypoints3d.shape[0] == keypoints2d.shape[1]
    # test mask list
    keypoints3d = triangulator.triangulate(
        points=keypoints2d, points_mask=points_mask.tolist())
    assert keypoints3d.shape[0] == keypoints2d.shape[1]
    # test mask tuple
    keypoints3d = triangulator.triangulate(
        points=keypoints2d, points_mask=tuple(map(tuple, points_mask)))
    assert keypoints3d.shape[0] == keypoints2d.shape[1]
    # test slice
    int_triangulator = triangulator[0]
    assert len(int_triangulator.camera_parameters) == 1
    list_triangulator = triangulator[[0, 1]]
    assert len(list_triangulator.camera_parameters) == 2
    tuple_triangulator = triangulator[(0, 1)]
    assert len(tuple_triangulator.camera_parameters) == 2
    slice_triangulator = triangulator[:2]
    assert len(slice_triangulator.camera_parameters) == 2
    slice_triangulator = triangulator[::2]
    assert len(slice_triangulator.camera_parameters) >= 2
    # test error
    keypoints3d = triangulator.triangulate(keypoints2d)
    error = triangulator.get_reprojection_error(
        points2d=keypoints2d, points3d=keypoints3d)
    assert np.all(error.shape == keypoints2d[..., :2].shape)
    # triangulate and visualize
    keypoints3d = triangulator.triangulate(
        points=keypoints2d, points_mask=np.expand_dims(keypoints2d_mask, -1))
    projector = triangulator.get_projector()
    projected_points = projector.project(keypoints3d)
    for cam_idx in range(n_view):
        canvas = cv2.imread(os.path.join(input_dir, f'{cam_idx:06}.png'))
        valid_idxs = np.where(keypoints2d_mask == 1)
        for point_idx in valid_idxs[1]:
            cv2.circle(
                img=canvas,
                center=projected_points[cam_idx, point_idx].astype(np.int32),
                radius=2,
                color=(0, 0, 255))
        cv2.imwrite(
            filename=os.path.join(output_dir, f'projected_kps_{cam_idx}.jpg'),
            img=canvas)
