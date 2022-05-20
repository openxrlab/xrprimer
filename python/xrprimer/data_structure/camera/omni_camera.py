from typing import Union

import numpy as np

from xrprimer_cpp.camera import OmniCameraParameter as OmniCameraParameter_cpp
from .pinhole_camera import PinholeCameraParameter


class OmniCameraParameter(OmniCameraParameter_cpp, PinholeCameraParameter):
    ATTR_NAMES = PinholeCameraParameter.ATTR_NAMES.copy() + \
        ['k1', 'k2', 'k3', 'k4', 'k5', 'k6', 'p1', 'p2', 'xi', 'D']

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
                 xi: float = 0.0,
                 D: list = None) -> None:
        OmniCameraParameter_cpp.__init__(self)
        PinholeCameraParameter.__init__(
            self,
            K=K,
            R=R,
            T=T,
            name=name,
            height=height,
            width=width,
            world2cam=world2cam,
            convention=convention)
        self.set_distortion_coefficients(
            dist_coeff_k=dist_coeff_k, dist_coeff_p=dist_coeff_p)
        self.set_omni_param(xi=xi, D=D)

    def SaveFile(self, filename: str) -> int:
        """Dump camera name and parameters to a json file.

        Args:
            filename (str):
                Path to the dumped json file.

        Returns:
            int: returns 0.
        """
        return super(OmniCameraParameter_cpp, self).SaveFile(filename)

    def LoadFile(self, filename: str) -> int:
        """Load camera name and parameters from a dumped json file.

        Args:
            filename (str):
                Path to the dumped json file.

        Returns:
            int: returns 0.
        """
        return super(OmniCameraParameter_cpp, self).LoadFile(filename)

    def set_omni_param(self,
                       xi: Union[float, None] = None,
                       D: Union[list, None] = None) -> None:
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
        if xi is not None:
            setattr(self, 'xi', xi)
        if D is not None:
            assert len(D) <= 4
            D_attr = np.zeros(shape=(4))
            D_input = np.array(D)
            D_attr[:len(D)] = D_input
            setattr(self, 'D', D_attr)

    def set_distortion_coefficients(self, dist_coeff_k: list,
                                    dist_coeff_p: list) -> None:
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
