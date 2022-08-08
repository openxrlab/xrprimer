from typing import Union

import numpy as np

from xrprimer.data_structure.camera import (
    FisheyeCameraParameter,
    PinholeCameraParameter,
)


def rotate_camera(
    cam_param: Union[PinholeCameraParameter,
                     FisheyeCameraParameter], rotation_mat: np.ndarray
) -> Union[PinholeCameraParameter, FisheyeCameraParameter]:
    """Apply rotation to a camera parameter.

    Args:
        cam_param (Union[
                PinholeCameraParameter,
                FisheyeCameraParameter]):
            The camera to rotate.
        rotation_mat (np.ndarray):
            Rotation matrix defined in world space,
            shape [3, 3].

    Returns:
        Union[PinholeCameraParameter, FisheyeCameraParameter]:
            Rotated camera in same type and extrinsic direction
            like the input camera.
    """
    input_w2c = cam_param.world2cam
    ret_cam_param = cam_param.clone()
    if input_w2c:
        ret_cam_param.inverse_extrinsic()
    cam_loc = np.asarray(ret_cam_param.get_extrinsic_t())
    cam_loc = np.matmul(rotation_mat, cam_loc)
    c2w_rot = np.asarray(ret_cam_param.get_extrinsic_r())
    c2w_rot = np.matmul(rotation_mat, c2w_rot)
    ret_cam_param.set_KRT(R=c2w_rot, T=cam_loc, world2cam=False)
    if ret_cam_param.world2cam != input_w2c:
        ret_cam_param.inverse_extrinsic()
    return ret_cam_param


def translate_camera(
    cam_param: Union[PinholeCameraParameter,
                     FisheyeCameraParameter], translation: np.ndarray
) -> Union[PinholeCameraParameter, FisheyeCameraParameter]:
    """Apply the translation to a camera parameter.

    Args:
        cam_param (Union[
                PinholeCameraParameter,
                FisheyeCameraParameter]):
            The camera to rotate.
        translation (np.ndarray):
            Translation vector defined in world space,
            shape [3,].

    Returns:
        Union[PinholeCameraParameter, FisheyeCameraParameter]:
            Translated camera in same type and extrinsic direction
            like the input camera.
    """
    input_w2c = cam_param.world2cam
    ret_cam_param = cam_param.clone()
    if input_w2c:
        ret_cam_param.inverse_extrinsic()
    cam_loc = np.asarray(ret_cam_param.get_extrinsic_t())
    cam_loc += translation
    ret_cam_param.set_KRT(T=cam_loc, world2cam=False)
    if ret_cam_param.world2cam != input_w2c:
        ret_cam_param.inverse_extrinsic()
    return ret_cam_param
