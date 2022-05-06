import os
import shutil

import pytest

from xrprimer.data_structure.camera.pinhole_camera import \
    PinholeCameraParameter  # noqa:E501

input_dir = 'test/data/test_data_structure/camera_parameter'
output_dir = 'test/data/output/test_pinhole_camera_parameter'


@pytest.fixture(scope='module', autouse=True)
def fixture():
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=False)


def test_load():
    input_json_path = os.path.join(input_dir,
                                   'xrprimer_pinh_cam_param_dump_0.json')
    camera_parameter = PinholeCameraParameter(name='load_json')
    camera_parameter.load(input_json_path)


def test_dump():
    input_json_path = os.path.join(input_dir,
                                   'xrprimer_pinh_cam_param_dump_0.json')
    output_json_path = os.path.join(output_dir,
                                    'xrprimer_pinh_cam_param_dump_0.json')
    camera_parameter = PinholeCameraParameter(name='dump_json')
    camera_parameter.load(input_json_path)
    camera_parameter.dump(output_json_path)
    assert os.path.exists(output_json_path)
    os.remove(output_json_path)


def test_inverse():
    input_json_path = os.path.join(input_dir,
                                   'xrprimer_pinh_cam_param_dump_1.json')
    camera_parameter = PinholeCameraParameter(name='load_json')
    camera_parameter.load(input_json_path)
    origin_world2cam = camera_parameter.world2cam
    origin_intrinsic00 = camera_parameter.intrinsic[0][0]
    origin_r02 = camera_parameter.extrinsic_r[0][2]
    camera_parameter.inverse_extrinsic()
    eps = 1e-4
    assert origin_world2cam is not camera_parameter.world2cam
    assert abs(origin_intrinsic00 - camera_parameter.intrinsic[0][0]) < eps
    assert abs(origin_r02 - camera_parameter.extrinsic_r[0][2]) >= eps
    camera_parameter.inverse_extrinsic()
    assert origin_world2cam is camera_parameter.world2cam
    assert abs(origin_intrinsic00 - camera_parameter.intrinsic[0][0]) < eps
    assert abs(origin_r02 - camera_parameter.extrinsic_r[0][2]) < eps
