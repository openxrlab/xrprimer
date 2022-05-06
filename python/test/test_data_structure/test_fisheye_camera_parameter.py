import os
import shutil

import pytest

from xrprimer.data_structure.camera.fisheye_camera import \
    FisheyeCameraParameter  # noqa:E501

input_dir = 'test/data/test_data_structure/camera_parameter'
output_dir = 'test/data/output/test_fisheye_camera_parameter'


@pytest.fixture(scope='module', autouse=True)
def fixture():
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=False)


def test_load():
    input_json_path = os.path.join(input_dir,
                                   'xrprimer_fishe_cam_param_dump_0.json')
    camera_parameter = FisheyeCameraParameter(name='load_json')
    camera_parameter.load(input_json_path)


def test_dump():
    input_json_path = os.path.join(input_dir,
                                   'xrprimer_fishe_cam_param_dump_0.json')
    output_json_path = os.path.join(output_dir,
                                    'xrprimer_fishe_cam_param_dump_0.json')
    camera_parameter = FisheyeCameraParameter(name='dump_json')
    camera_parameter.load(input_json_path)
    camera_parameter.dump(output_json_path)
    assert os.path.exists(output_json_path)
    os.remove(output_json_path)


def test_set_distortion():
    camera_parameter = FisheyeCameraParameter(name='set_distortion')
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
