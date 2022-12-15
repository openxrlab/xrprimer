import logging
from typing import Tuple, Union

import cv2
import numpy as np

from xrprimer.data_structure.camera import (
    FisheyeCameraParameter,
    PinholeCameraParameter,
)
from xrprimer.transform.convention.camera import convert_camera_parameter
from xrprimer.utils.log_utils import get_logger


def undistort_camera(
        distorted_cam: FisheyeCameraParameter) -> PinholeCameraParameter:
    """Undistort a FisheyeCameraParameter to PinholeCameraParameter.

    Args:
        distorted_cam (FisheyeCameraParameter):
            An instance of FisheyeCameraParameter. Convention will be checked,
            resolution, intrinsic mat
            and distortion coefficients will be used.

    Raises:
        NotImplementedError: Camera convention not supported.

    Returns:
        PinholeCameraParameter:
            Undistorted camera parameter.
    """
    assert isinstance(distorted_cam, FisheyeCameraParameter), \
        'distorted_cam must be an instance of class FisheyeCameraParameter.'
    # prepare input of cv2.undistort
    if distorted_cam.convention != 'opencv':
        distorted_cam = convert_camera_parameter(
            cam_param=distorted_cam, dst='opencv')
    dist_coeff_list = distorted_cam.get_dist_coeff()
    distorted_intrinsic33 = np.array(distorted_cam.get_intrinsic(k_dim=3))
    resolution_wh = np.array([distorted_cam.width, distorted_cam.height])
    # prepare output of cv2.undistort
    corrected_intrinsic33 = np.zeros_like(distorted_intrinsic33)
    corrected_intrinsic33, _ = cv2.getOptimalNewCameraMatrix(
        distorted_intrinsic33, np.array(dist_coeff_list), resolution_wh, 0,
        resolution_wh)
    corrected_cam_param = PinholeCameraParameter(
        K=corrected_intrinsic33,
        R=distorted_cam.get_extrinsic_r(),
        T=distorted_cam.get_extrinsic_t(),
        name=f'undistort_{distorted_cam.name}',
        height=distorted_cam.height,
        width=distorted_cam.width,
        world2cam=distorted_cam.world2cam,
        convention='opencv')
    return corrected_cam_param


def undistort_images(
        distorted_cam: FisheyeCameraParameter,
        image_array: np.ndarray) -> Tuple[PinholeCameraParameter, np.ndarray]:
    """Undistort a FisheyeCameraParameter to PinholeCameraParameter, and
    undistort an array of images shot on a fisheye camera.

    Args:
        distorted_cam (FisheyeCameraParameter):
            An instance of FisheyeCameraParameter. Convention will be checked,
            resolution, intrinsic mat
            and distortion coefficients will be used.
        image_array (np.ndarray):
            An array of images, in shape [n_frame, height, width, n_channel].

    Raises:
        NotImplementedError: Camera convention not supported.

    Returns:
        Tuple[PinholeCameraParameter, np.ndarray]:
            PinholeCameraParameter:
                Undistorted camera parameter.
            np.ndarray:
                Corrected images in the same shape as input.
    """
    # prepare input of cv2.undistort
    if distorted_cam.convention != 'opencv':
        distorted_cam = convert_camera_parameter(
            cam_param=distorted_cam, dst='opencv')
    distorted_intrinsic33 = np.array(distorted_cam.get_intrinsic(k_dim=3))
    dist_coeff_list = distorted_cam.get_dist_coeff()
    dist_coeff_np = np.array(dist_coeff_list)
    corrected_cam_param = undistort_camera(distorted_cam=distorted_cam)
    corrected_intrinsic33 = np.array(
        corrected_cam_param.get_intrinsic(k_dim=3))
    corrected_image_array = np.ones_like(image_array)
    for image_index, image_np in enumerate(image_array):
        corrected_image_array[image_index] = cv2.undistort(
            image_np,
            distorted_intrinsic33,
            dist_coeff_np,
            newCameraMatrix=corrected_intrinsic33)
    return corrected_cam_param, corrected_image_array


def undistort_points(
        distorted_cam: FisheyeCameraParameter,
        points: np.ndarray) -> Tuple[PinholeCameraParameter, np.ndarray]:
    """Undistort a FisheyeCameraParameter to PinholeCameraParameter, and
    undistort an array of points in fisheye camera screen. Parameters and
    points will be casted to np.float64 before operation.

    Args:
        distorted_cam (FisheyeCameraParameter):
            An instance of FisheyeCameraParameter. Convention will be checked,
            resolution, intrinsic mat
            and distortion coefficients will be used.
        points (np.ndarray):
            An array of points, in shape [..., 2], int or float.
            ... could be [n_point, ], [n_frame, n_point, ]
            [n_frame, n_object, n_point, ], etc.

    Raises:
        NotImplementedError: Camera convention not supported.

    Returns:
        Tuple[PinholeCameraParameter, np.ndarray]:
            PinholeCameraParameter:
                Undistorted camera parameter.
            np.ndarray:
                Corrected points location in the same shape as input,
                dtype is np.float64.
    """
    # prepare input of cv2.undistortPoints
    if distorted_cam.convention != 'opencv':
        distorted_cam = convert_camera_parameter(
            cam_param=distorted_cam, dst='opencv')
    distorted_intrinsic33 = np.array(distorted_cam.get_intrinsic(k_dim=3))
    dist_coeff_list = distorted_cam.get_dist_coeff()
    dist_coeff_np = np.array(dist_coeff_list)
    corrected_cam_param = undistort_camera(distorted_cam=distorted_cam)
    corrected_intrinsic33 = np.array(
        corrected_cam_param.get_intrinsic(k_dim=3))
    shape_backup = points.shape
    # opencv expects (n, 1, 2)
    points = points.reshape(-1, 1, 2)
    corrected_points = cv2.undistortPoints(
        points.astype(np.float64),
        cameraMatrix=distorted_intrinsic33,
        distCoeffs=dist_coeff_np,
        P=corrected_intrinsic33)
    corrected_points = corrected_points.reshape(*shape_backup)
    return corrected_cam_param, corrected_points


def get_undistort_maps(
        fisheye_param: FisheyeCameraParameter
) -> Tuple[np.ndarray, np.ndarray]:
    """Get Undistortion and rectification maps defined in opencv.

    Args:
        fisheye_param (FisheyeCameraParameter):
            FisheyeCameraParameter for the distorted image.

    Returns:
        Tuple[np.ndarray, np.ndarray]:
            Undistortion and rectification transformation map.
    """
    pinhole_param = undistort_camera(fisheye_param)
    dist_coeff_np = np.array(fisheye_param.get_dist_coeff())
    map1, map2 = cv2.initUndistortRectifyMap(
        cameraMatrix=np.array(fisheye_param.get_intrinsic(3)),
        distCoeffs=dist_coeff_np,
        R=np.eye(3),
        newCameraMatrix=np.array(pinhole_param.get_intrinsic(3)),
        size=np.array((
            pinhole_param.width,
            pinhole_param.height,
        )),
        m1type=cv2.CV_32FC1)
    return map1, map2


class FastImageUndistortor:
    """A class for fast image undistortion."""

    def __init__(self,
                 fisheye_param: FisheyeCameraParameter,
                 logger: Union[None, str, logging.Logger] = None) -> None:
        """
        Args:
            fisheye_param (FisheyeCameraParameter):
                FisheyeCameraParameter for the distorted image.
            logger (Union[None, str, logging.Logger], optional):
                Logger for logging. If None, root logger will be selected.
                Defaults to None.
        """
        self.logger = get_logger(logger)
        self.fisheye_param = fisheye_param
        self.pinhole_param = undistort_camera(fisheye_param)
        map1, map2 = get_undistort_maps(fisheye_param)
        self.map1 = map1
        self.map2 = map2

    def undistort_image(self, img_arr: np.ndarray) -> np.ndarray:
        """Undistort an image captured by self.fisheye_param.

        Args:
            img_arr (np.ndarray):
                Image array in shape [h, w, c].

        Returns:
            np.ndarray: Undistorted image.
        """
        img_arr = cv2.remap(
            img_arr, self.map1, self.map2, interpolation=cv2.INTER_NEAREST)
        return img_arr
