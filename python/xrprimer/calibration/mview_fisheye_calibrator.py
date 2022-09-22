import logging
import os
import shutil
from typing import List, Tuple, Union

import cv2
import numpy as np

from xrprimer.data_structure.camera import FisheyeCameraParameter
from xrprimer.transform.camera.distortion import undistort_images
from xrprimer.utils.path_utils import (
    Existence,
    check_path_existence,
    prepare_output_path,
)
from .mview_pinhole_calibrator import MviewPinholeCalibrator
from .sview_fisheye_calibrator import SviewFisheyeDistortionCalibrator


class MviewFisheyeCalibrator(MviewPinholeCalibrator):
    """Multi-view extrinsic calibrator for distorted fisheye cameras."""

    def __init__(self,
                 chessboard_width: int,
                 chessboard_height: int,
                 chessboard_square_size: int,
                 work_dir: str,
                 calibrate_intrinsic: bool = False,
                 calibrate_distortion: bool = False,
                 calibrate_extrinsic: bool = True,
                 logger: Union[None, str, logging.Logger] = None) -> None:
        """Initialization for MviewFisheyeCalibrator class.

        Args:
            chessboard_width (int):
                How many internal corners along the
                horizontal edge of the chessboard.
            chessboard_height (int):
                How many internal corners along the
                vertical edge of the chessboard.
            chessboard_square_size (int):
                The edge length of a unit square in millimeter.
            work_dir (str):
                A path to an empty dir or nonexistent dir, undistorted
                frames will be saved there.
            calibrate_intrinsic (bool, optional):
                Whether to calibrate intrinsic. Defaults to False.
            calibrate_distortion (bool, optional):
                Whether to calibrate distortion coefficients.
                Defaults to False.
            calibrate_extrinsic (bool, optional):
                Whether to calibrate extrinsic. Defaults to True.
            logger (Union[None, str, logging.Logger], optional):
                Logger for logging. If None, root logger will be selected.
                Defaults to None.
        """
        MviewPinholeCalibrator.__init__(
            self,
            chessboard_width=chessboard_width,
            chessboard_height=chessboard_height,
            chessboard_square_size=chessboard_square_size,
            logger=logger)
        self.work_dir = work_dir
        if calibrate_intrinsic:
            self.logger.error('Intrinsic calibration not implemented yet.')
            raise NotImplementedError
        if (calibrate_intrinsic or calibrate_distortion
                or calibrate_extrinsic) is False:
            self.logger.error(
                'Please select at least one parameter to calibrate.')
            raise ValueError
        self.calibrate_intrinsic = calibrate_intrinsic
        self.calibrate_distortion = calibrate_distortion
        self.calibrate_extrinsic = calibrate_extrinsic

    def calibrate(
        self,
        frames: List[List[str]],
        fisheye_param_list: List[FisheyeCameraParameter],
    ) -> List[FisheyeCameraParameter]:
        """Calibrate multi-FisheyeCameraParameters with a chessboard. It takes
        intrinsics and distortion coefficients from fisheye_param_list,
        calibrates only extrinsics on undistorted frames.

        Args:
            frames (List[List[str]]):
                A nested list of distorted image paths. The shape is
                [n_frame, n_view], and each element is the path to
                an image file. '' stands for an empty image.
            fisheye_param_list (List[FisheyeCameraParameter]):
                A list of FisheyeCameraParameters. Intrinsic matrix
                and distortion coefficients are necessary for calibration.

        Returns:
            List[FisheyeCameraParameter]:
                A list of calibrated fisheye cameras, name, logger,
                resolution will be kept.
        """
        prepare_output_path(
            output_path=self.work_dir,
            path_type='dir',
            overwrite=False,
            logger=self.logger)
        if len(frames) <= 0:
            self.logger.error('Frames are necessary for fisheye extrinsic' +
                              ' calibration.')
            raise ValueError
        if len(frames[0]) != len(fisheye_param_list):
            self.logger.error(
                'n_view of frames must be equal to len(fisheye_param_list).')
            raise ValueError
        ret_list = [fisheye_param for fisheye_param in fisheye_param_list]
        if self.calibrate_distortion:
            sview_distortion_calibrator = SviewFisheyeDistortionCalibrator(
                chessboard_width=self.chessboard_width,
                chessboard_height=self.chessboard_height,
                logger=self.logger)
            for view_idx, fisheye_param in enumerate(ret_list):
                sview_frames = []
                for mview_frames in frames:
                    if len(mview_frames[view_idx]) > 0:
                        sview_frames.append(mview_frames[view_idx])
                calibrated_fisheye_param = \
                    sview_distortion_calibrator.calibrate(
                        frames=sview_frames,
                        fisheye_param=fisheye_param)
                ret_list[view_idx] = calibrated_fisheye_param
        if self.calibrate_extrinsic:
            undistorted_frames, pinhole_param_list = \
                self.__prepare_undistorted_frames__(
                    frames=frames,
                    fisheye_param_list=ret_list)
            pinhole_param_list = MviewPinholeCalibrator.calibrate(
                self,
                frames=undistorted_frames,
                pinhole_param_list=pinhole_param_list,
            )
            self.__remove_work_dir__()
            for view_idx, pinhole_param in enumerate(pinhole_param_list):
                fisheye_param = ret_list[view_idx].clone()
                fisheye_param.convention = 'opencv'
                fisheye_param.set_KRT(
                    R=pinhole_param.get_extrinsic_r(),
                    T=pinhole_param.get_extrinsic_t(),
                    world2cam=False)
                ret_list[view_idx] = fisheye_param
        return ret_list

    def __prepare_undistorted_frames__(
        self,
        frames: List[List[str]],
        fisheye_param_list: List[FisheyeCameraParameter],
    ) -> Tuple[List[List[str]], List[FisheyeCameraParameter]]:
        """Undistort images in frames, return paths to undistorted images and
        undistorted pinhole cameras.

        Args:
            frames (List[List[str]]):
                A nested list of distorted image paths. The shape is
                [n_frame, n_view], and each element is the path to
                an image file. '' stands for an empty image.
            fisheye_param_list (List[FisheyeCameraParameter]):
                A list of FisheyeCameraParameters. Intrinsic matrix
                and distortion coefficients are necessary for calibration.

        Returns:
            undistorted_frames (List[List[str]]):
                A nested list of undistorted image paths.
            pinhole_param_list (List[FisheyeCameraParameter]):
                A list of PinholeCameraParameters
        """
        n_view = len(fisheye_param_list)
        pinhole_param_list = []
        undistorted_frames = [[] for _ in range(len(frames))]
        for view_idx in range(n_view):
            sview_path_list = []
            default_shape = None
            for frame_idx, mview_paths in enumerate(frames):
                img_path = mview_paths[view_idx]
                if default_shape is None and len(img_path) > 0:
                    default_shape = cv2.imread(img_path).shape
                sview_path_list.append(img_path)
            sview_img_list = []
            sview_idx_list = []
            for frame_idx, img_path in enumerate(sview_path_list):
                if len(img_path) > 0:
                    img = cv2.imread(img_path)
                    sview_img_list.append(img)
                    sview_idx_list.append(frame_idx)
            sview_img_arr = np.asarray(sview_img_list)
            pinhole_param, undist_img_arr = undistort_images(
                distorted_cam=fisheye_param_list[view_idx],
                image_array=sview_img_arr)
            pinhole_param_list.append(pinhole_param)
            for img, frame_idx in zip(sview_img_list, sview_idx_list):
                path = os.path.join(
                    self.work_dir,
                    f'frame_{frame_idx:06d}_view_{view_idx:03d}.png')
                cv2.imwrite(path, img)
            for frame_idx, img_path in enumerate(sview_path_list):
                path = os.path.join(
                    self.work_dir,
                    f'frame_{frame_idx:06d}_view_{view_idx:03d}.png')
                if len(img_path) > 0:
                    undistorted_frames[frame_idx].append(path)
                else:
                    undistorted_frames[frame_idx].append('')
        return undistorted_frames, pinhole_param_list

    def __remove_work_dir__(self):
        """Remove temp files in self.work_dir."""
        if check_path_existence(self.work_dir) == \
                Existence.DirectoryExistEmpty or \
                check_path_existence(self.work_dir) == \
                Existence.DirectoryExistNotEmpty:
            shutil.rmtree(self.work_dir)
