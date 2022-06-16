from xrprimer.data_structure.camera.camera import BaseCameraParameter
from .from_opencv import convert_camera_from_opencv
from .intrinsic import downgrade_k_4x4, upgrade_k_3x3
from .to_opencv import convert_camera_to_opencv

__all__ = ['upgrade_k_3x3', 'downgrade_k_4x4', 'convert_camera_parameter']


def convert_camera_parameter(
    cam_param: BaseCameraParameter,
    dst: str,
) -> BaseCameraParameter:
    """Convert a camera parameter instance into opencv convention.

    Args:
        cam_param (BaseCameraParameter):
            The input camera parameter, which is an instance of
            BaseCameraParameter subclass.
        dst (str):
            The name of destination convention.

    Returns:
        BaseCameraParameter:
            A camera in the same type as input, whose
            direction is same as cam_param, and convention
            equals to dst.
    """
    if cam_param.convention == dst:
        return cam_param
    else:
        opencv_cam = convert_camera_to_opencv(cam_param)
        dst_cam = convert_camera_from_opencv(opencv_cam, dst)
        if dst_cam.world2cam != cam_param.world2cam:
            dst_cam.inverse_extrinsic()
        return dst_cam
