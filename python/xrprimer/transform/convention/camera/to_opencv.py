import numpy as np

from xrprimer.data_structure.camera.camera import BaseCameraParameter


def convert_camera_to_opencv(
        cam_param: BaseCameraParameter) -> BaseCameraParameter:
    """Convert a camera parameter instance into opencv convention.

    Args:
        cam_param (BaseCameraParameter):
            The input camera parameter, which is an instance of
            BaseCameraParameter subclass.

    Raises:
        NotImplementedError:
            cam_param.convention has not been supported.

    Returns:
        BaseCameraParameter:
            A camera in the same type as input, whose
            direction is cam2world and convention
            is 'opencv'.
    """
    # do not modify cam_param, modify the cloned cam
    cam_param_backup = cam_param
    cam_param = cam_param_backup.clone()
    if cam_param.world2cam is True:
        cam_param.inverse_extrinsic()
    if cam_param.convention == 'opencv':
        return cam_param
    elif cam_param.convention == 'blender':
        # rotation of euler zxy, (0, 180, 0)
        rot_mat = np.array([[1.0, 0.0, 0.0], [0.0, -1.0, 0.0],
                            [0.0, 0.0, -1.0]])
        extrinsic_r = np.asarray(cam_param.get_extrinsic_r())
        extrinsic_r = np.matmul(rot_mat, extrinsic_r)
        cam_param.set_KRT(R=extrinsic_r)
        cam_param.convention = 'blender'
        return cam_param
    elif cam_param.convention == 'unreal':
        cam_location = np.asarray(cam_param.get_extrinsic_t())
        # left hand to right hand
        cam_location *= np.asarray((-1, 1, 1))
        # rotation of euler zxy, (90, 270, 0)
        rot_mat = np.array([[0.0, -1.0, 0.0], [0.0, 0.0, 1.0],
                            [-1.0, 0.0, 0.0]])
        extrinsic_r = np.asarray(cam_param.get_extrinsic_r())
        extrinsic_r = np.matmul(rot_mat, extrinsic_r)
        cam_param.set_KRT(R=extrinsic_r, T=cam_location)
        cam_param.convention = 'unreal'
        return cam_param
    else:
        cam_param.logger.error(
            f'Converting a camera from {cam_param.convention} to opencv' +
            ' has not been supported yet.')
        raise NotImplementedError
