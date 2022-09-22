import json
import logging
from typing import List, Union

from xrprimer.data_structure.camera import PinholeCameraParameter
from xrprimer_cpp import \
    VectorPinholeCameraParameter as VectorPinholeCameraParameter_cpp
from xrprimer_cpp import calibrator as calibrator_cpp
from .base_calibrator import BaseCalibrator


class MviewPinholeCalibrator(BaseCalibrator):
    """Multi-view extrinsic calibrator for pinhole cameras."""

    def __init__(self,
                 chessboard_width: int,
                 chessboard_height: int,
                 chessboard_square_size: int,
                 calibrate_intrinsic: bool = False,
                 calibrate_extrinsic: bool = True,
                 logger: Union[None, str, logging.Logger] = None) -> None:
        """Initialization for MviewPinholeCalibrator class.

        Args:
            chessboard_width (int):
                How many internal corners along the
                horizontal edge of the chessboard.
            chessboard_height (int):
                How many internal corners along the
                vertical edge of the chessboard.
            chessboard_square_size (int):
                The edge length of a unit square in millimeter.
            calibrate_intrinsic (bool, optional):
                Whether to calibrate intrinsic. Defaults to False.
            calibrate_extrinsic (bool, optional):
                Whether to calibrate extrinsic. Defaults to True.
            logger (Union[None, str, logging.Logger], optional):
                Logger for logging. If None, root logger will be selected.
                Defaults to None.
        """
        BaseCalibrator.__init__(self, logger=logger)
        self.chessboard_width = chessboard_width
        self.chessboard_height = chessboard_height
        self.chessboard_square_size = chessboard_square_size
        if calibrate_intrinsic:
            self.logger.error('Intrinsic calibration not implemented yet.')
            raise NotImplementedError
        if (calibrate_intrinsic or calibrate_extrinsic) is False:
            self.logger.error(
                'Please select at least one parameter to calibrate.')
            raise ValueError
        self.calibrate_intrinsic = calibrate_intrinsic
        self.calibrate_extrinsic = calibrate_extrinsic

    def calibrate(
        self,
        frames: List[List[str]],
        pinhole_param_list: List[PinholeCameraParameter],
    ) -> List[PinholeCameraParameter]:
        """Calibrate multi-PinholeCameraParameters with a chessboard.

        Args:
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

        if len(frames) <= 0:
            self.logger.error('Frames are necessary for pinhole extrinsic' +
                              ' calibration.')
            raise ValueError
        if len(frames[0]) != len(pinhole_param_list):
            self.logger.error(
                'n_view of frames must be equal to len(pinhole_param_list).')
            raise ValueError
        chessboard_config_dict = dict(
            chessboard_width=self.chessboard_width,
            chessboard_height=self.chessboard_height,
            chessboard_square_size=self.chessboard_square_size)
        ret_list = []
        if self.calibrate_extrinsic:
            chessboard_config_str = json.dumps(chessboard_config_dict)
            pinhole_vector = VectorPinholeCameraParameter_cpp(
                pinhole_param_list)
            calibrator_cpp.CalibrateMultiPinholeCamera(chessboard_config_str,
                                                       frames, pinhole_vector)
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
