import copy
import logging
from typing import Union

from xrprimer_cpp.camera import \
    FisheyeCameraParameter as FisheyeCameraParameter_cpp
from .pinhole_camera import PinholeCameraParameter


class FisheyeCameraParameter(FisheyeCameraParameter_cpp,
                             PinholeCameraParameter):
    ATTR_NAMES = PinholeCameraParameter.ATTR_NAMES.copy() + \
        ['k1', 'k2', 'k3', 'k4', 'k5', 'k6', 'p1', 'p2']

    def __init__(self,
                 K: Union[list, None] = None,
                 R: Union[list, None] = None,
                 T: Union[list, None] = None,
                 name: str = 'default',
                 height: int = 1080,
                 width: int = 1920,
                 world2cam: bool = True,
                 convention: str = 'opencv',
                 dist_coeff_k: list = [],
                 dist_coeff_p: list = [],
                 logger: Union[None, str, logging.Logger] = None) -> None:
        """A camera parameter class for fisheye camera model. Distortion
        coefficients are k1, k2, ..., k6, p1, p2.

        Args:
            K (Union[list, np.ndarray, None], optional):
                Nested list of float32, 4x4 or 3x3 K mat.
                Defaults to None, 4x4 zeros.
            R (Union[list, np.ndarray, None], optional):
                Nested list of float32, 3x3 rotation mat.
                Defaults to None, 3x3 identity.
            T (Union[list, np.ndarray, None], optional):
                List of float32, T vector.
                Defaults to None, zero vector.
            name (str, optional):
                Name of this camera. Defaults to 'default'.
            height (int, optional):
                Height of the image shot by this camera.
                Defaults to 1080.
            width (int, optional):
                Width of the image shot by this camera.
                Defaults to 1920.
            world2cam (bool, optional):
                Whether the R, T transform points from world space
                to camera space. Defaults to True.
            convention (str, optional):
                Convention name of this camera.
                Defaults to 'opencv'.
            dist_coeff_k (list, optional):
                List of float. [k1, k2, k3, k4, k5, k6].
                When length of list is n and n<6,
                only the first n coefficients will be set. Defaults to [].
            dist_coeff_p (list, optional):
                List of float. [p1, p2].
                To set only p1, pass [p1]. Defaults to [].
            logger (Union[None, str, logging.Logger], optional):
                Logger for logging. If None, root logger will be selected.
                Defaults to None.
        """
        FisheyeCameraParameter_cpp.__init__(self)
        PinholeCameraParameter.__init__(
            self,
            K=K,
            R=R,
            T=T,
            name=name,
            height=height,
            width=width,
            world2cam=world2cam,
            convention=convention,
            logger=logger)
        self.set_dist_coeff(
            dist_coeff_k=dist_coeff_k, dist_coeff_p=dist_coeff_p)

    def set_dist_coeff(self, dist_coeff_k: list, dist_coeff_p: list) -> None:
        """Set distortion coefficients from list.

        Args:
            dist_coeff_k (list):
                List of float. [k1, k2, k3, k4, k5, k6].
                When length of list is n and n<6,
                only the first n coefficients will be set.
            dist_coeff_p (list):
                List of float. [p1, p2].
                To set only p1, pass [p1].
        """
        assert len(dist_coeff_k) <= 6
        assert len(dist_coeff_p) <= 2
        for k_index, k_value in enumerate(dist_coeff_k):
            setattr(self, f'k{k_index+1}', k_value)
        for p_index, p_value in enumerate(dist_coeff_p):
            setattr(self, f'p{p_index+1}', p_value)

    def get_dist_coeff(self) -> list:
        """Get distortion coefficients in self.convention.

        Raises:
            NotImplementedError: convention not supported.

        Returns:
            list: A list of distortion coefficients, in a
            turn defined by self.convention.
        """
        dist_coeff_list = []
        if self.convention == 'opencv':
            dist_coeff_names = ['k1', 'k2', 'p1', 'p2', 'k3', 'k4', 'k5', 'k6']
            for coeff_name in dist_coeff_names:
                dist_coeff_list.append(getattr(self, coeff_name, 0.0))
        else:
            self.logger.error(f'Distortion for camera in {self.convention}' +
                              ' has not been supported .')
            raise NotImplementedError
        return dist_coeff_list

    def clone(self) -> 'FisheyeCameraParameter':
        """Clone a new CameraPrameter instance like self.

        Returns:
            FisheyeCameraParameter
        """
        new_cam_param = self.__class__(
            K=copy.deepcopy(self.get_intrinsic(k_dim=4)),
            R=copy.deepcopy(self.extrinsic_r),
            T=copy.deepcopy(self.extrinsic_t),
            name=self.name,
            height=self.height,
            width=self.width,
            world2cam=self.world2cam,
            convention=self.convention,
            logger=self.logger)
        attr_name_list = [f'k{k_index}' for k_index in range(1, 7, 1)]
        attr_name_list += [f'p{p_index}' for p_index in range(1, 3, 1)]
        for attr_name in attr_name_list:
            attr_value = getattr(self, attr_name)
            setattr(new_cam_param, attr_name, attr_value)
        return new_cam_param

    def SaveFile(self, filename: str) -> bool:
        """Dump camera name and parameters to a json file.

        Args:
            filename (str):
                Path to the dumped json file.

        Returns:
            bool: True if save succeed.
        """
        return FisheyeCameraParameter_cpp.SaveFile(self, filename)

    def LoadFile(self, filename: str) -> bool:
        """Load camera name and parameters from a dumped json file.

        Args:
            filename (str):
                Path to the dumped json file.

        Returns:
            bool: True if load succeed.
        """
        return FisheyeCameraParameter_cpp.LoadFile(self, filename)
