import glob
import os
import shutil

import mmcv
import numpy as np
import pytest

from xrprimer.calibration.builder import build_calibrator
from xrprimer.data_structure.camera import FisheyeCameraParameter

input_dir = 'test/data/calibration/test_sview_intrinsic_calibrator'
output_dir = 'test/data/output/calibration/test_sview_intrinsic_calibrator'
eps = 1e-4


@pytest.fixture(scope='module', autouse=True)
def fixture():
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=False)


def test_sview_fisheye_distortion_calibrator():
    fisheye_param = FisheyeCameraParameter.fromfile(
        os.path.join(input_dir, 'init_fisheye_param.json'))
    frame_list = sorted(glob.glob(os.path.join(input_dir, 'images', '*.jpg')))
    # test dict config
    calibrator_config = dict(
        mmcv.Config.fromfile('config/calibration/' +
                             'sview_fisheye_distortion_calibrator.py'))
    calibrator = build_calibrator(calibrator_config)
    calibrated_fisheye_param = calibrator.calibrate(frame_list, fisheye_param)
    assert abs(calibrated_fisheye_param.k1 - 0.0) > eps
    assert abs(calibrated_fisheye_param.k2 - 0.0) > eps
    assert abs(calibrated_fisheye_param.k3 - 0.0) > eps
    assert abs(calibrated_fisheye_param.p1 - 0.0) > eps
    assert abs(calibrated_fisheye_param.p2 - 0.0) > eps
    assert abs(calibrated_fisheye_param.k4 - 0.0) < eps
    assert abs(calibrated_fisheye_param.k5 - 0.0) < eps
    assert np.all(
        np.asarray(calibrated_fisheye_param.get_intrinsic(3)) == np.asarray(
            fisheye_param.get_intrinsic(3)))
    calibrated_fisheye_param.dump(
        os.path.join(output_dir, 'calibrated_fisheye_param.json'))
