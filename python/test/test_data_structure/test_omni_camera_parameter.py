import os
import shutil

import numpy as np
import pytest

from xrprimer.data_structure.camera.omni_camera import \
    OmniCameraParameter  # noqa:E501

input_dir = 'test/data/test_data_structure/camera_parameter'
output_dir = 'test/data/output/test_omni_camera_parameter'
eps = 1e-4
focal_length_x = 954.5469360351562


@pytest.fixture(scope='module', autouse=True)
def fixture():
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=False)


def test_load():
    input_json_path = os.path.join(input_dir,
                                   'xrprimer_omni_cam_param_dump_0.json')
    camera_parameter = OmniCameraParameter(name='load')
    camera_parameter.load(input_json_path)
    assert camera_parameter.get_intrinsic(k_dim=4)[0][0] - focal_length_x < eps
    camera_parameter = OmniCameraParameter(name='LoadFile')
    camera_parameter.LoadFile(input_json_path)
    assert camera_parameter.get_intrinsic(k_dim=4)[0][0] - focal_length_x < eps
    k33_0 = camera_parameter.intrinsic33()
    k33_1 = np.asarray(camera_parameter.get_intrinsic(3))
    assert np.sum(k33_1 - k33_0) < eps


def test_dump():
    input_json_path = os.path.join(input_dir,
                                   'xrprimer_omni_cam_param_dump_0.json')
    output_json_path = os.path.join(output_dir,
                                    'xrprimer_omni_cam_param_dump_0.json')
    camera_parameter = OmniCameraParameter(name='dump')
    camera_parameter.load(input_json_path)
    camera_parameter.dump(output_json_path)
    assert os.path.exists(output_json_path)
    os.remove(output_json_path)
    camera_parameter = OmniCameraParameter(name='SaveFile')
    camera_parameter.load(input_json_path)
    camera_parameter.SaveFile(output_json_path)
    assert os.path.exists(output_json_path)
    os.remove(output_json_path)


def test_set_distortion():
    camera_parameter = OmniCameraParameter(name='set_distortion')
    # set correctly
    camera_parameter.set_distortion_coefficients(
        dist_coeff_k=[1, 2, 3, 4, 5, 6], dist_coeff_p=[1, 2])
    # set half
    camera_parameter.set_distortion_coefficients(
        dist_coeff_k=[11, 12, 13], dist_coeff_p=[11])
    assert camera_parameter.k2 == 12
    assert camera_parameter.k5 == 5
    assert camera_parameter.p1 == 11
    assert camera_parameter.p2 == 2
    # set more
    with pytest.raises(AssertionError):
        camera_parameter.set_distortion_coefficients(
            dist_coeff_k=[1, 2, 3, 4, 5, 6, 7], dist_coeff_p=[1, 2])
    with pytest.raises(AssertionError):
        camera_parameter.set_distortion_coefficients(
            dist_coeff_k=[1, 2, 3, 4, 5, 6], dist_coeff_p=[1, 2, 3])


def test_set_omni_param():
    camera_parameter = OmniCameraParameter(name='set_omni_param')
    # set correctly
    camera_parameter.set_omni_param(xi=1.0, D=[1, 2, 3, 4])
    # set half
    camera_parameter.set_omni_param(xi=1.0, D=[11, 12])
    assert camera_parameter.D[0] == 11
    assert camera_parameter.D[3] == 0
    # set xi
    camera_parameter.set_omni_param(xi=2.0)
    assert camera_parameter.xi == 2.0
    # set D
    camera_parameter.set_omni_param(D=[4, 3, 2, 1])
    assert camera_parameter.D[2] == 2
    # set more
    with pytest.raises(AssertionError):
        camera_parameter.set_omni_param(xi=1.0, D=[1, 2, 3, 4, 5])


def test_inverse():
    input_json_path = os.path.join(input_dir,
                                   'xrprimer_omni_cam_param_dump_1.json')
    camera_parameter = OmniCameraParameter(name='load_json')
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
                                   'xrprimer_omni_cam_param_dump_1.json')
    camera_parameter = OmniCameraParameter(name='src')
    camera_parameter.load(input_json_path)
    cloned_camera_parameter = camera_parameter.clone()
    assert isinstance(cloned_camera_parameter, OmniCameraParameter)
    cloned_k = np.asarray(cloned_camera_parameter.get_intrinsic(k_dim=4))
    src_k = np.asarray(camera_parameter.get_intrinsic(k_dim=4))
    assert np.allclose(cloned_k, src_k)
    assert id(cloned_k) != id(src_k)
