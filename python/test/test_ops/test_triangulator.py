import os

import mmcv
import numpy as np

from xrprimer.data_structure.camera.fisheye_camera import \
    FisheyeCameraParameter  # noqa:E501
from xrprimer.ops.triangulation.builder import build_triangulator  # noqa:E501

input_dir = 'test/data/test_ops/test_triangulation'
output_dir = 'test/data/output/test_ops/test_triangulation'


def test_opencv_triangulator():
    keypoints2d = np.load(os.path.join(input_dir, 'keypoints2d.npz'))['arr_0']
    view_n = keypoints2d.shape[0]
    keypoints2d = keypoints2d[..., :2].reshape(view_n, -1, 2)
    cam_param_list = []
    for kinect_index in range(view_n):
        cam_param_path = os.path.join(input_dir,
                                      f'cam_{kinect_index:02d}.json')
        cam_param = FisheyeCameraParameter()
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
