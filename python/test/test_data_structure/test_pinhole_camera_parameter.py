import os
import shutil

import numpy as np
import pytest

from xrprimer.data_structure.camera import PinholeCameraParameter  # noqa:E501

input_dir = 'test/data/test_data_structure/camera_parameter'
output_dir = 'test/data/output/test_pinhole_camera_parameter'
eps = 1e-4
focal_length_x = 954.5469360351562


@pytest.fixture(scope='module', autouse=True)
def fixture():
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=False)


def test_load():
    input_json_path = os.path.join(input_dir, 'pinhole_param_at_origin.json')
    camera_parameter = PinholeCameraParameter(name='test_load')
    camera_parameter.load(input_json_path)
    assert camera_parameter.get_intrinsic(k_dim=4)[0][0] - focal_length_x < eps
    camera_parameter = PinholeCameraParameter(name='test_LoadFile')
    camera_parameter.LoadFile(input_json_path)
    assert camera_parameter.get_intrinsic(k_dim=4)[0][0] - focal_length_x < eps
    k33_0 = camera_parameter.intrinsic33()
    k33_1 = np.asarray(camera_parameter.get_intrinsic(3))
    assert np.sum(k33_1 - k33_0) < eps


def test_dump():
    input_json_path = os.path.join(input_dir, 'pinhole_param_at_origin.json')
    output_json_path = os.path.join(output_dir, 'pinhole_param_at_origin.json')
    camera_parameter = PinholeCameraParameter(name='test_dump')
    camera_parameter.load(input_json_path)
    camera_parameter.dump(output_json_path)
    assert os.path.exists(output_json_path)
    os.remove(output_json_path)
    camera_parameter = PinholeCameraParameter(name='test_SaveFile')
    camera_parameter.load(input_json_path)
    camera_parameter.SaveFile(output_json_path)
    assert os.path.exists(output_json_path)
    os.remove(output_json_path)


def test_inverse():
    input_json_path = os.path.join(input_dir,
                                   'pinhole_param_not_at_origin.json')
    camera_parameter = PinholeCameraParameter(name='test_inverse')
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
                                   'pinhole_param_not_at_origin.json')
    camera_parameter = PinholeCameraParameter(name='test_clone')
    camera_parameter.load(input_json_path)
    cloned_camera_parameter = camera_parameter.clone()
    assert isinstance(cloned_camera_parameter, PinholeCameraParameter)
    cloned_k = np.asarray(cloned_camera_parameter.get_intrinsic(k_dim=4))
    src_k = np.asarray(camera_parameter.get_intrinsic(k_dim=4))
    assert np.allclose(cloned_k, src_k)
    assert id(cloned_k) != id(src_k)
