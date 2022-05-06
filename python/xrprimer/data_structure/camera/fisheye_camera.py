import copy
from typing import TypeVar, Union

import numpy as np
from xrprimer_cpp.camera import \
    FisheyeCameraParameter as FisheyeCameraParameter_cpp

_FisheyeCameraParameter = TypeVar('_FisheyeCameraParameter')


class FisheyeCameraParameter(FisheyeCameraParameter_cpp):
    ATTR_NAMES = [
        'name', 'intrinsic', 'extrinsic_r', 'extrinsic_t', 'height', 'width',
        'world2cam', 'convention', 'k1', 'k2', 'k3', 'k4', 'k5', 'k6', 'p1',
        'p2'
    ]

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
        super().__init__()
        self.name = name
        self.set_KRT(K, R, T)
        self.set_resolution(height=height, width=width)
        self.world2cam = world2cam
        self.convention = convention
        self.set_distortion_coefficients(
            dist_coeff_k=dist_coeff_k, dist_coeff_p=dist_coeff_p)

    def clone(self) -> _FisheyeCameraParameter:
        """Clone a new CameraPrameter instance like self.

        Returns:
            PinholeCameraParameter
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

    def set_KRT(self,
                K: Union[list, None] = None,
                R: Union[list, None] = None,
                T: Union[list, None] = None,
                world2cam: Union[bool, None] = None) -> None:
        """Set K, R to matrix and T to vector.

        Args:
            K (Union[list, None]):
                Nested list of float32, 4x4 or 3x3 K mat.
                Defaults to None, intrisic will not be changed.
            R (Union[list, None]):
                Nested list of float32, 3x3 R mat.
                Defaults to None, extrisic_r will not be changed.
            T (Union[list, None]):
                List of float32, T vector.
                Defaults to None, extrisic_t will not be changed.
            world2cam (Union[bool, None], optional):
                Whether the R, T transform points from world space
                to camera space.
                Defaults to None, self.world2cam will not be changed.
        """
        if K is not None:
            if len(K) == 4:
                self.intrinsic = np.asarray(K)
            else:
                self.set_intrinsic(mat3x3=K, perspective=True)
        if R is not None:
            self.extrinsic_r = np.asarray(R)
        if T is not None:
            self.extrinsic_t = np.asarray(T)
        if world2cam is not None:
            assert isinstance(world2cam, bool)
            self.world2cam = world2cam

    def set_intrinsic(self,
                      mat3x3: Union[list, None] = None,
                      width: int = None,
                      height: int = None,
                      fx: float = None,
                      fy: float = None,
                      cx: float = None,
                      cy: float = None,
                      perspective: bool = True) -> None:
        """Set the intrinsic of a camera. Note that mat3x3 has a higher
        priority than fx, fy, cx, cy.

        Args:
            mat3x3 (list, optional):
                A nested list of intrinsic matrix,
                in shape (3, 3). If mat is given,
                fx, fy, cx, cy will be ignored.
                Defaults to None.
            width (int):
                Width of the screen.
            height (int):
                Height of the screen.
            fx (float, optional):
                Focal length. Defaults to None.
            fy (float, optional):
                Focal length. Defaults to None.
            cx (float, optional):
                Camera principal point. Defaults to None.
            cy (float, optional):
                Camera principal point. Defaults to None.
            perspective (bool, optional):
                Whether it is a perspective camera, if not,
                it's orthographics. Defaults to True.
        """
        if mat3x3 is not None:
            mat3x3 = np.asarray(mat3x3)
            super().set_intrinsic(mat3x3=mat3x3, perspective=perspective)
        elif width is not None and\
                height is not None and\
                fx is not None and\
                fy is not None and\
                cx is not None and\
                cy is not None:
            super().set_intrinsic(
                width=width, height=height, fx=fx, fy=fy, cx=cx, cy=cy)
        else:
            raise ValueError

    def get_intrinsic(self, k_dim: int = 3) -> list:
        """Get intrinsic K matrix.

        Args:
            k_dim (int, optional):
                If 3, returns a 3x3 mat.
                Else if 4, returns a 4x4 mat.
                Defaults to 3.

        Raises:
            ValueError: k_dim is neither 3 nor 4.

        Returns:
            list: Nested list of float32, 4x4 or 3x3 K mat.
        """
        if k_dim == 4:
            return self.intrinsic.tolist()
        elif k_dim == 3:
            return super().intrinsic33().tolist()
        else:
            raise ValueError

    def set_resolution(self, height: int, width: int) -> None:
        """Set resolution of the camera.

        Args:
            height (int):
                Height of the screen.
            width (int):
                Width of the screen.
        """
        self.height = height
        self.width = width

    def inverse_extrinsic(self) -> None:
        """Inverse the direction of extrinsics, between world to camera and
        camera to world."""
        r_mat = np.asarray(self.extrinsic_r)
        t_vec = np.asarray(self.extrinsic_t)
        r_mat = np.linalg.inv(r_mat).reshape(3, 3)
        t_vec = -np.dot(r_mat, t_vec).reshape(3)
        self.extrinsic_r = r_mat.tolist()
        self.extrinsic_t = t_vec.tolist()
        self.world2cam = not self.world2cam

    def SaveFile(self, filename: str) -> int:
        """Dump camera name and parameters to a json file.

        Args:
            filename (str):
                Path to the dumped json file.

        Returns:
            int: returns 0.
        """
        super().SaveFile(filename)

    def dump(self, filename: str) -> None:
        """Dump camera name and parameters to a json file.

        Args:
            filename (str):
                Path to the dumped json file.
        """
        self.SaveFile(filename)

    def LoadFile(self, filename: str) -> int:
        """Load camera name and parameters from a dumped json file.

        Args:
            filename (str):
                Path to the dumped json file.

        Returns:
            int: returns 0.
        """
        super().LoadFile(filename)

    def load(self, filename: str) -> None:
        """Load camera name and parameters from a dumped json file.

        Args:
            filename (str):
                Path to the dumped json file.
        """
        self.LoadFile(filename)

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
