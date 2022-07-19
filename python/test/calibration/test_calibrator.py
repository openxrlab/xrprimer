import glob
import json
import os
import shutil

import numpy as np
import pytest

from xrprimer.calibration.calibrator import Calibrator
from xrprimer.data_structure.camera import PinholeCameraParameter
from xrprimer.utils.path_utils import Existence, check_path_existence

input_dir = 'test/data/calib_pinhole_camera/input'
output_dir = 'test/data/output/calibration/test_calibrator'


@pytest.fixture(scope='module', autouse=True)
def fixture():
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=False)


def test_calibrate_multi_pinhole_camera():
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
    # test dict config
    calib_config = dict(
        chessboard_width=6, chessboard_height=7, chessboard_square_size=100)
    pinhole_list = Calibrator.calibrate_multi_pinhole_camera(
        calib_config, mframe_list, pinhole_list)
    for pinhole_param in pinhole_list:
        pinhole_param.dump(
            os.path.join(output_dir, f'{pinhole_param.name}.json'))
    # test str config
    calib_config = """
        {
        "chessboard_width": 6,
        "chessboard_height": 7,
        "chessboard_square_size": 100
        }
    """
    Calibrator.calibrate_multi_pinhole_camera(calib_config, mframe_list,
                                              pinhole_list)
