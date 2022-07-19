import json
from typing import List, Union

from xrprimer.data_structure.camera import PinholeCameraParameter
from xrprimer_cpp import \
    VectorPinholeCameraParameter as VectorPinholeCameraParameter_cpp
from xrprimer_cpp import calibrator as calibrator_cpp


class Calibrator():

    @staticmethod
    def calibrate_multi_pinhole_camera(
        calib_config: Union[dict, str], frames: List[List[str]],
        pinhole_param_list: List[PinholeCameraParameter]
    ) -> List[PinholeCameraParameter]:
        """Calibrate multi-PinholeCameraParameters with a chessboard.

        Args:
            calib_config (Union[dict, str]):
                Config of the calibration chessboard. It shall be a
                dict or string loaded from config json, chessboard_width,
                chessboard_height, and chessboard_square_size are
                required.
            frames (List[List[str]]):
                A nested list of image paths. The shape is
                [n_frame, n_view], and each element is the path to
                an image file. '' stands for an empty image.
            pinhole_param_list (List[PinholeCameraParameter]):
                A list of PinholeCameraParameters. Intrinsic matrix
                is necessary for calibration.

        Returns:
            List[PinholeCameraParameter]:
                A list of calibrated pinhole cameras, name, logger,
                resolution will be kept.
        """
        if isinstance(calib_config, dict):
            calib_config = json.dumps(calib_config)
        pinhole_vector = VectorPinholeCameraParameter_cpp(pinhole_param_list)
        calibrator_cpp.CalibrateMultiPinholeCamera(calib_config, frames,
                                                   pinhole_vector)
        ret_list = []
        for cam_idx, pinhole_param_cpp in enumerate(pinhole_vector):
            pinhole_param = PinholeCameraParameter(
                name=pinhole_param_list[cam_idx].name,
                K=pinhole_param_cpp.intrinsic,
                R=pinhole_param_cpp.extrinsic_r,
                T=pinhole_param_cpp.extrinsic_t,
                height=pinhole_param_list[cam_idx].height,
                width=pinhole_param_list[cam_idx].width,
                world2cam=False,
                convention='opencv',
                logger=pinhole_param_list[cam_idx].logger)
            ret_list.append(pinhole_param)
        return ret_list
