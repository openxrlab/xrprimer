import logging
from typing import List, Union

import cv2
import numpy as np

from xrprimer.data_structure.camera import FisheyeCameraParameter
from .base_calibrator import BaseCalibrator


class SviewFisheyeDistortionCalibrator(BaseCalibrator):
    """Single-view distortion calibrator for distorted fisheye camera.

    It takes an init intrinsic, fix it and calibrate distortion coefficients.
    """

    def __init__(self,
                 chessboard_width: int,
                 chessboard_height: int,
                 logger: Union[None, str, logging.Logger] = None) -> None:
        """Initialization for SviewFisheyeDistortionCalibrator class.

        Args:
            chessboard_width (int):
                How many internal corners along the
                horizontal edge of the chessboard.
            chessboard_height (int):
                How many internal corners along the
                vertical edge of the chessboard.
            logger (Union[None, str, logging.Logger], optional):
                Logger for logging. If None, root logger will be selected.
                Defaults to None.
        """
        BaseCalibrator.__init__(self, logger=logger)
        self.chessboard_width = chessboard_width
        self.chessboard_height = chessboard_height

    def calibrate(
        self,
        frames: List[str],
        fisheye_param: FisheyeCameraParameter,
    ) -> FisheyeCameraParameter:
        """Calibrate FisheyeCameraParameter with a chessboard. It takes
        intrinsics from fisheye_param, calibrates only distortion coefficients
        on undistorted frames.

        Args:
            frames (List[str]):
                A list of distorted image paths.
            fisheye_param (FisheyeCameraParameter):
                An instance of FisheyeCameraParameter. Intrinsic matrix
                is necessary for calibration, and the input instance
                will not be modified.

        Returns:
            FisheyeCameraParameter:
                An instance of FisheyeCameraParameter. Distortion coefficients
                are the only difference from input.
        """
        if len(frames) <= 0:
            self.logger.error('Frames are necessary for fisheye distortion' +
                              ' calibration.')
            raise ValueError
        # termination criteria
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30,
                    0.001)
        # prepare object points in (x, y, 0),
        # like (0,0,0), (1,0,0), (2,0,0), ...
        sframe_obj_points = np.zeros(
            (self.chessboard_width * self.chessboard_height, 3), np.float32)
        sframe_obj_points[:, :2] = np.mgrid[
            0:self.chessboard_width,
            0:self.chessboard_height].T.reshape(-1, 2)
        mframe_obj_points = []  # 3d point in real world space
        mframe_img_points = []  # 2d points in image plane.
        for _, frame_path in enumerate(frames):
            img = cv2.imread(frame_path)
            if len(img.shape) == 3 and img.shape[-1] == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            height, width = img.shape
            # Find the chess board corners
            pattern_found, corners = cv2.findChessboardCorners(
                img, (self.chessboard_width, self.chessboard_height), None)
            # If found, add object points, image points (after refining them)
            if pattern_found:
                mframe_obj_points.append(sframe_obj_points.copy())
                better_conners = cv2.cornerSubPix(img, corners, (11, 11),
                                                  (-1, -1), criteria)
                mframe_img_points.append(better_conners)
        # use preset-intrinsic and fix fx, fy, cx, cy
        calib_flags = cv2.CALIB_USE_INTRINSIC_GUESS + \
            cv2.CALIB_FIX_PRINCIPAL_POINT + \
            cv2.CALIB_FIX_FOCAL_LENGTH
        _, _, dist_coeff, _, _ = cv2.calibrateCamera(
            objectPoints=mframe_obj_points,
            imagePoints=mframe_img_points,
            imageSize=(width, height),
            cameraMatrix=np.asarray(fisheye_param.get_intrinsic(3)),
            distCoeffs=None,
            flags=calib_flags)
        ret_fisheye_param = fisheye_param.clone()
        dist_coeff = dist_coeff.tolist()[0]
        ret_fisheye_param.set_dist_coeff(
            dist_coeff_k=dist_coeff[:2] + dist_coeff[-1:],
            dist_coeff_p=dist_coeff[2:4])
        return ret_fisheye_param
