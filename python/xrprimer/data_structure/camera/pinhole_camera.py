from typing import Union

from xrprimer.data_structure.camera.camera import BaseCameraParameter


class PinholeCameraParameter(BaseCameraParameter):
    ATTR_NAMES = BaseCameraParameter.ATTR_NAMES +\
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
        super().__init__(
            K=K,
            R=R,
            T=T,
            name=name,
            height=height,
            width=width,
            world2cam=world2cam,
            convention=convention)
        for k_index in range(1, 7, 1):
            setattr(self, f'k{k_index}', 0.0)
        for p_index in range(1, 3, 1):
            setattr(self, f'p{p_index}', 0.0)
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
            setattr(self, f'k{k_index}', k_value)
        for p_index, p_value in enumerate(dist_coeff_p):
            setattr(self, f'p{p_index}', p_value)
