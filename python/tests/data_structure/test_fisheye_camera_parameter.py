import os
import shutil

import numpy as np
import pytest

from xrprimer.data_structure.camera.fisheye_camera import \
    FisheyeCameraParameter  # noqa:E501

input_dir = 'tests/data/data_structure/camera_parameter'
output_dir = 'tests/data/output/data_structure/test_fisheye_camera_parameter'
eps = 1e-4
focal_length_x = 954.5469360351562


@pytest.fixture(scope='module', autouse=True)
def fixture():
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=False)


def test_load():
    input_json_path = os.path.join(input_dir, 'fisheye_param_at_origin.json')
    camera_parameter = FisheyeCameraParameter(name='test_LoadFile')
    ret_val = camera_parameter.LoadFile(input_json_path)
    assert ret_val is True
    assert camera_parameter.get_intrinsic(k_dim=4)[0][0] - focal_length_x < eps
    camera_parameter = FisheyeCameraParameter(name='test_load')
    camera_parameter.load(input_json_path)
    assert camera_parameter.get_intrinsic(k_dim=4)[0][0] - focal_length_x < eps
    k33_0 = camera_parameter.intrinsic33()
    k33_1 = np.asarray(camera_parameter.get_intrinsic(3))
    assert np.sum(k33_1 - k33_0) < eps
    with pytest.raises(FileNotFoundError):
        camera_parameter.load('/no_file.json')
    with pytest.raises(ValueError):
        camera_parameter.load(
            os.path.join(input_dir, 'omni_param_at_origin.json'))
    camera_parameter = FisheyeCameraParameter.fromfile(input_json_path)
    assert camera_parameter.get_intrinsic(k_dim=4)[0][0] - focal_length_x < eps


def test_dump():
    input_json_path = os.path.join(input_dir, 'fisheye_param_at_origin.json')
    output_json_path = os.path.join(output_dir, 'fisheye_param_at_origin.json')
    camera_parameter = FisheyeCameraParameter(name='test_dump')
    camera_parameter.load(input_json_path)
    camera_parameter.dump(output_json_path)
    assert os.path.exists(output_json_path)
    os.remove(output_json_path)
    camera_parameter = FisheyeCameraParameter(name='test_SaveFile')
    camera_parameter.load(input_json_path)
    camera_parameter.SaveFile(output_json_path)
    assert os.path.exists(output_json_path)
    os.remove(output_json_path)


def test_set_distortion():
    camera_parameter = FisheyeCameraParameter(name='test_set_distortion')
    # set correctly
    camera_parameter.set_dist_coeff(
        dist_coeff_k=[1, 2, 3, 4, 5, 6], dist_coeff_p=[1, 2])
    # set half
    camera_parameter.set_dist_coeff(
        dist_coeff_k=[11, 12, 13], dist_coeff_p=[11])
    assert camera_parameter.k2 == 12
    assert camera_parameter.k5 == 5
    assert camera_parameter.p1 == 11
    assert camera_parameter.p2 == 2
    # set more
    with pytest.raises(AssertionError):
        camera_parameter.set_dist_coeff(
            dist_coeff_k=[1, 2, 3, 4, 5, 6, 7], dist_coeff_p=[1, 2])
    with pytest.raises(AssertionError):
        camera_parameter.set_dist_coeff(
            dist_coeff_k=[1, 2, 3, 4, 5, 6], dist_coeff_p=[1, 2, 3])


def test_inverse():
    input_json_path = os.path.join(input_dir,
                                   'fisheye_param_not_at_origin.json')
    camera_parameter = FisheyeCameraParameter(name='test_inverse')
    camera_parameter.load(input_json_path)
    origin_world2cam = camera_parameter.world2cam
    origin_intrinsic00 = camera_parameter.get_intrinsic(k_dim=4)[0][0]
    origin_r02 = camera_parameter.get_extrinsic_r()[0][2]
    camera_parameter.inverse_extrinsic()
    assert origin_world2cam is not camera_parameter.world2cam
    assert abs(origin_intrinsic00 -
               camera_parameter.get_intrinsic(k_dim=4)[0][0]) < eps
    assert abs(origin_r02 - camera_parameter.get_extrinsic_r()[0][2]) >= eps
    camera_parameter.inverse_extrinsic()
    assert origin_world2cam is camera_parameter.world2cam
    assert abs(origin_intrinsic00 -
               camera_parameter.get_intrinsic(k_dim=4)[0][0]) < eps
    assert abs(origin_r02 - camera_parameter.get_extrinsic_r()[0][2]) < eps


def test_clone():
    input_json_path = os.path.join(input_dir,
                                   'fisheye_param_not_at_origin.json')
    camera_parameter = FisheyeCameraParameter(name='test_clone')
    camera_parameter.load(input_json_path)
    cloned_camera_parameter = camera_parameter.clone()
    assert isinstance(cloned_camera_parameter, FisheyeCameraParameter)
    cloned_k = np.asarray(cloned_camera_parameter.get_intrinsic(k_dim=4))
    src_k = np.asarray(camera_parameter.get_intrinsic(k_dim=4))
    assert np.allclose(cloned_k, src_k)
    assert id(cloned_k) != id(src_k)
