import copy
import logging
import os
from typing import Union

import numpy as np

from xrprimer.utils.log_utils import get_logger
from xrprimer_cpp.camera import BaseCameraParameter as BaseCameraParameter_cpp


class BaseCameraParameter(BaseCameraParameter_cpp):
    ATTR_NAMES = [
        'name', 'intrinsic', 'extrinsic_r', 'extrinsic_t', 'height', 'width',
        'world2cam', 'convention'
    ]

    def __init__(self,
                 K: Union[list, np.ndarray, None] = None,
                 R: Union[list, np.ndarray, None] = None,
                 T: Union[list, np.ndarray, None] = None,
                 name: str = 'default',
                 height: int = 1080,
                 width: int = 1920,
                 world2cam: bool = True,
                 convention: str = 'opencv',
                 logger: Union[None, str, logging.Logger] = None) -> None:
        """Base class for all python camera parameter classes. Common methods
        are defined in this class.

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
            logger (Union[None, str, logging.Logger], optional):
                Logger for logging. If None, root logger will be selected.
                Defaults to None.
        """
        super().__init__(
            intrinsic=np.zeros((4, 4)),
            extrinsic_r=np.zeros((3, 3)),
            extrinsic_t=np.ones((3, )))
        self.name = name
        self.set_KRT(K, R, T)
        self.set_resolution(height=height, width=width)
        self.world2cam = world2cam
        self.convention = convention
        self.logger = get_logger(logger)

    def set_intrinsic(self,
                      mat3x3: Union[list, np.ndarray, None] = None,
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
            self.logger.error(
                'Either mat3x3 or (h, w, fx/y, cx/y) should be offered.')
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

    def set_KRT(self,
                K: Union[list, np.ndarray, None] = None,
                R: Union[list, np.ndarray, None] = None,
                T: Union[list, np.ndarray, None] = None,
                world2cam: Union[bool, None] = None) -> None:
        """Set K, R to matrix and T to vector.

        Args:
            K (Union[list, np.ndarray, None]):
                Nested list of float32, 4x4 or 3x3 K mat.
                Defaults to None, intrisic will not be changed.
            R (Union[list, np.ndarray, None]):
                Nested list of float32, 3x3 R mat.
                Defaults to None, extrisic_r will not be changed.
            T (Union[list, np.ndarray, None]):
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

    def inverse_extrinsic(self) -> None:
        """Inverse the direction of extrinsics, between world to camera and
        camera to world."""
        r_mat = np.asarray(self.extrinsic_r)
        t_vec = np.asarray(self.extrinsic_t)
        r_mat = np.linalg.inv(r_mat).reshape(3, 3)
        t_vec = -np.dot(r_mat, t_vec).reshape(3)
        self.extrinsic_r = r_mat
        self.extrinsic_t = t_vec
        self.world2cam = not self.world2cam

    def intrinsic33(self) -> np.ndarray:
        """Get an intrinsic matrix in shape (3, 3).

        Returns:
            ndarray: An ndarray of intrinsic matrix.
        """
        return super().intrinsic33()

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
            self.logger.error('k_dim is neither 3 nor 4.')
            raise ValueError

    def get_extrinsic_r(self) -> list:
        """Get extrinsic rotation matrix.

        Returns:
            list: Nested list of float32, 3x3 R mat.
        """
        return self.extrinsic_r.tolist()

    def get_extrinsic_t(self) -> list:
        """Get extrinsic translation vector.

        Returns:
            list: Nested list of float32, T vec of length 3.
        """
        return self.extrinsic_t.reshape(3).tolist()

    def SaveFile(self, filename: str) -> int:
        """Dump camera name and parameters to a json file.

        Args:
            filename (str):
                Path to the dumped json file.

        Returns:
            int: returns 0.
        """
        return BaseCameraParameter_cpp.SaveFile(self, filename)

    def dump(self, filename: str) -> None:
        """Dump camera name and parameters to a json file.

        Args:
            filename (str):
                Path to the dumped json file.

        Raises:
            RuntimeError: Fail to dump a json file.
        """
        if not self.SaveFile(filename):
            self.logger.error('Fail to dump a json file.')
            raise RuntimeError

    def LoadFile(self, filename: str) -> bool:
        """Load camera name and parameters from a dumped json file.

        Args:
            filename (str):
                Path to the dumped json file.

        Returns:
            bool: True if load succeed.
        """
        return BaseCameraParameter_cpp.LoadFile(self, filename)

    def load(self, filename: str) -> None:
        """Load camera name and parameters from a dumped json file.

        Args:
            filename (str):
                Path to the dumped json file.

        Raises:
            FileNotFoundError: File not found at filename.
            ValueError: Content in filename is not correct.
        """
        if not os.path.exists(filename):
            self.logger.error(f'File not found at {filename}.')
            raise FileNotFoundError
        test_cam = self.__class__()
        load_test = test_cam.LoadFile(filename)
        if load_test:
            self.LoadFile(filename)
        else:
            self.logger.error('File content is not correct.')
            raise ValueError

    def clone(self) -> 'BaseCameraParameter':
        """Clone a new CameraPrameter instance like self.

        Returns:
            BaseCameraParameter
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
        return new_cam_param

    @classmethod
    def fromfile(cls, filename: str) -> 'BaseCameraParameter':
        """Construct a camera parameter data structure from a json file.

        Args:
            filename (str):
                Path to the dumped json file.

        Returns:
            CameraParameter:
                An instance of CameraParameter class.
        """
        ret_cam = cls()
        ret_cam.load(filename)
        return ret_cam
