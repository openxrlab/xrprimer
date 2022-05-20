import copy
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
                 dist_coeff_p: list = []) -> None:
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
            convention=convention)
        self.set_distortion_coefficients(
            dist_coeff_k=dist_coeff_k, dist_coeff_p=dist_coeff_p)

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
            convention=self.convention)
        for k_index in range(1, 7, 1):
            attr_name = f'k{k_index}'
            attr_value = getattr(self, attr_name)
            setattr(new_cam_param, attr_name, attr_value)
        for p_index in range(1, 3, 1):
            attr_name = f'p{p_index}'
            attr_value = getattr(self, attr_name)
            setattr(new_cam_param, attr_name, attr_value)
        return new_cam_param

    def SaveFile(self, filename: str) -> int:
        """Dump camera name and parameters to a json file.

        Args:
            filename (str):
                Path to the dumped json file.

        Returns:
            int: returns 0.
        """
        return super(FisheyeCameraParameter_cpp, self).SaveFile(filename)

    def LoadFile(self, filename: str) -> int:
        """Load camera name and parameters from a dumped json file.

        Args:
            filename (str):
                Path to the dumped json file.

        Returns:
            int: returns 0.
        """
        return super(FisheyeCameraParameter_cpp, self).LoadFile(filename)
