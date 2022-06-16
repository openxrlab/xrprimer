import os

import numpy as np
import pytest

from xrprimer.data_structure.camera import FisheyeCameraParameter
from xrprimer.transform.convention.camera import (
    convert_camera_parameter,
    downgrade_k_4x4,
    upgrade_k_3x3,
)

cam_param_dir = 'test/data/test_data_structure/camera_parameter'


def test_intrinsic():
    # test one k
    intrinsic44 = np.asarray([[954.5469360351562, 0.0, 955.3258056640625, 0.0],
                              [0.0, 953.5127563476562, 552.7735595703125, 0.0],
                              [0.0, 0.0, 0.0, 1.0], [0.0, 0.0, 1.0, 0.0]])
    intrinsic33 = downgrade_k_4x4(intrinsic44)
    assert len(intrinsic33) == 3
    assert intrinsic33[2][2] == 1
    intrinsic44_back = upgrade_k_3x3(intrinsic33, is_perspective=True)
    assert np.allclose(intrinsic44_back, intrinsic44)
    # test batched k
    intrinsic44 = np.expand_dims(intrinsic44, axis=0).repeat(5, axis=0)
    intrinsic33 = downgrade_k_4x4(intrinsic44)
    assert len(intrinsic33) == 5
    assert len(intrinsic33[0]) == 3
    assert intrinsic33[0][2][2] == 1
    intrinsic44_back = upgrade_k_3x3(intrinsic33, is_perspective=True)
    assert np.allclose(intrinsic44_back, intrinsic44)


def test_convert_camera():
    fisheye_path = os.path.join(cam_param_dir,
                                'fisheye_param_not_at_origin.json')
    fisheye_opencv_param = FisheyeCameraParameter()
    fisheye_opencv_param.load(fisheye_path)
    # test opencv to opencv
    converted_param = convert_camera_parameter(
        cam_param=fisheye_opencv_param, dst='opencv')
    assert np.allclose(
        np.asarray(converted_param.get_extrinsic_r()),
        np.asarray(fisheye_opencv_param.get_extrinsic_r()))
    # test opencv to blender, world2cam
    if not fisheye_opencv_param.world2cam:
        fisheye_opencv_param.inverse_extrinsic()
    cam_backup = fisheye_opencv_param.clone()
    converted_param = convert_camera_parameter(
        cam_param=fisheye_opencv_param, dst='blender')
    # direction not changed
    assert converted_param.world2cam == fisheye_opencv_param.world2cam
    # input not changed
    assert np.all(
        np.asarray(fisheye_opencv_param.get_extrinsic_r()) == np.asarray(
            cam_backup.get_extrinsic_r()))
    # test opencv to blender, cam2world
    if fisheye_opencv_param.world2cam:
        fisheye_opencv_param.inverse_extrinsic()
    cam_backup = fisheye_opencv_param.clone()
    converted_param = convert_camera_parameter(
        cam_param=fisheye_opencv_param, dst='blender')
    # direction not changed
    assert converted_param.world2cam == fisheye_opencv_param.world2cam
    # input not changed
    assert np.all(
        np.asarray(fisheye_opencv_param.get_extrinsic_r()) == np.asarray(
            cam_backup.get_extrinsic_r()))
    # type not changed
    assert type(fisheye_opencv_param) == type(converted_param)
    with pytest.raises(NotImplementedError):
        converted_param = convert_camera_parameter(
            cam_param=fisheye_opencv_param, dst='ue5')
    with pytest.raises(NotImplementedError):
        converted_param.convention = 'ue5'
        converted_param = convert_camera_parameter(
            cam_param=converted_param, dst='opencv')
