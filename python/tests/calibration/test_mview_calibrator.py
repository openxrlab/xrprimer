import glob
import json
import os
import shutil

import mmcv
import numpy as np
import pytest

from xrprimer.calibration.builder import build_calibrator
from xrprimer.data_structure.camera import (
    FisheyeCameraParameter,
    PinholeCameraParameter,
)
from xrprimer.utils.path_utils import Existence, check_path_existence

input_dir = 'tests/data/calib_pinhole_camera/input'
output_dir = 'tests/data/output/calibration/test_mview_extrinsic_calibrator'


@pytest.fixture(scope='module', autouse=True)
def fixture():
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=False)


def get_frame_list(n_view: int) -> list:
    n_frame = len(glob.glob(os.path.join(input_dir, 'images', '*_cam00.jpg')))
    mframe_list = []
    for frame_idx in range(n_frame):
        mview_list = []
        for view_idx in range(n_view):
            img_path = os.path.join(
                input_dir, 'images',
                f'img{frame_idx:04d}_cam{view_idx:02d}.jpg')
            if check_path_existence(img_path) == Existence.FileExist:
                mview_list.append(img_path)
            else:
                mview_list.append('')
        mframe_list.append(mview_list)
    return mframe_list


def test_mview_pinhole_calibrator():
    # init pinhole parameters with intrinsic
    init_param_dir = os.path.join(input_dir, 'config')
    file_names = sorted(glob.glob(os.path.join(init_param_dir, '*.json')))
    pinhole_list = []
    for cam_idx, file_path in enumerate(file_names):
        with open(file_path, 'r') as f_read:
            param_dict = json.load(f_read)
        init_k = np.asarray(param_dict['intrinsic'])
        pinhole_param = PinholeCameraParameter(
            K=init_k, name=f'pinhole_{cam_idx:02d}', convention='opencv')
        pinhole_list.append(pinhole_param)
    n_view = len(pinhole_list)
    mframe_list = get_frame_list(n_view)
    # test dict config
    calibrator_config = dict(
        mmcv.Config.fromfile('config/calibration/' +
                             'mview_pinhole_calibrator.py'))
    calibrator = build_calibrator(calibrator_config)
    pinhole_list = calibrator.calibrate(mframe_list, pinhole_list)
    for pinhole_param in pinhole_list:
        pinhole_param.dump(
            os.path.join(output_dir, f'{pinhole_param.name}.json'))


def test_mview_fisheye_calibrator():
    # init pinhole parameters with intrinsic
    init_param_dir = os.path.join(input_dir, 'config')
    file_names = sorted(glob.glob(os.path.join(init_param_dir, '*.json')))
    fisheye_list = []
    for cam_idx, file_path in enumerate(file_names):
        with open(file_path, 'r') as f_read:
            param_dict = json.load(f_read)
        init_k = np.asarray(param_dict['intrinsic'])
        fisheye_param = FisheyeCameraParameter(
            K=init_k, name=f'fisheye_{cam_idx:02d}', convention='opencv')
        fisheye_param.set_dist_coeff([
            1e-4,
        ] * 6, [
            1e-4,
        ] * 2)
        fisheye_list.append(fisheye_param)
    n_view = len(fisheye_list)
    mframe_list = get_frame_list(n_view)
    # test dict config
    calibrator_config = dict(
        mmcv.Config.fromfile('config/calibration/' +
                             'mview_fisheye_calibrator.py'))
    # calibrate only extrinsic
    calibrator_config['calibrate_intrinsic'] = False
    calibrator_config['calibrate_distortion'] = False
    calibrator_config['calibrate_extrinsic'] = True
    calibrator_config['work_dir'] = os.path.join(
        output_dir, 'mview_fisheye_extrinsic_calibrator_temp')
    calibrator = build_calibrator(calibrator_config)
    fisheye_list = calibrator.calibrate(mframe_list, fisheye_list)
    for fisheye_param in fisheye_list:
        fisheye_param.dump(
            os.path.join(output_dir, f'fisheye_calibext_{cam_idx:02d}.json'))
    # calibrate only distortion
    calibrator_config['calibrate_intrinsic'] = False
    calibrator_config['calibrate_distortion'] = True
    calibrator_config['calibrate_extrinsic'] = False
    calibrator_config['work_dir'] = os.path.join(
        output_dir, 'mview_fisheye_extrinsic_calibrator_temp')
    calibrator = build_calibrator(calibrator_config)
    fisheye_list = calibrator.calibrate(mframe_list, fisheye_list)
    for fisheye_param in fisheye_list:
        fisheye_param.dump(
            os.path.join(output_dir, f'fisheye_calibdist_{cam_idx:02d}.json'))
    # calibrate distortion and extrinsic
    calibrator_config['calibrate_intrinsic'] = False
    calibrator_config['calibrate_distortion'] = True
    calibrator_config['calibrate_extrinsic'] = True
    calibrator_config['work_dir'] = os.path.join(
        output_dir, 'mview_fisheye_extrinsic_calibrator_temp')
    calibrator = build_calibrator(calibrator_config)
    fisheye_list = calibrator.calibrate(mframe_list, fisheye_list)
    for fisheye_param in fisheye_list:
        fisheye_param.dump(
            os.path.join(output_dir,
                         f'fisheye_calibdistext_{cam_idx:02d}.json'))
