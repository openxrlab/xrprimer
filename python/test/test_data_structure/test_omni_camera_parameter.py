import os
import shutil

import pytest

from xrprimer.data_structure.camera.omni_camera import \
    OmniCameraParameter  # noqa:E501

input_dir = 'test/data/test_data_structure/camera_parameter'
output_dir = 'test/data/output/test_omni_camera_parameter'


@pytest.fixture(scope='module', autouse=True)
def fixture():
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=False)


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
