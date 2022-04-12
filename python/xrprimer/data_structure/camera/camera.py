import json
from typing import Union

import numpy as np

from xrprimer.transform.camera.convention import downgrade_k_4x4, upgrade_k_3x3


class BaseCameraParameter():
    ATTR_NAMES = [
        'name', 'intrinsic', 'extrinsic_r', 'extrinsic_t', 'height', 'width',
        'world2cam', 'convention'
    ]

    def __init__(self,
                 K: Union[list, None] = None,
                 R: Union[list, None] = None,
                 T: Union[list, None] = None,
                 name: str = 'default',
                 height: int = 1080,
                 width: int = 1920,
                 world2cam: bool = True,
                 convention: str = 'opencv') -> None:
        for attr_name in self.__class__.ATTR_NAMES:
            setattr(self, attr_name, None)

        self.name = name
        self.set_KRT(K, R, T)
        self.set_resolution(height=height, width=width)
        self.world2cam = world2cam
        self.convention = convention

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
                self.intrinsic = K
            else:
                self.intrinsic = upgrade_k_3x3(np.asarray(K)).reshape(
                    4, 4).tolist()
        if R is not None:
            self.extrinsic_r = R
        if T is not None:
            self.extrinsic_t = T
        if world2cam is not None:
            assert isinstance(world2cam, bool)
            self.world2cam = world2cam

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
            return self.intrinsic
        elif k_dim == 3:
            return downgrade_k_4x4(np.asarray(self.intrinsic)).reshape(
                3, 3).tolist()
        else:
            raise ValueError

    def set_resolution(self, height: int, width: int) -> None:
        self.height = height
        self.width = width

    def inverse_extrinsic(self) -> None:
        r_mat = np.asarray(self.extrinsic_r)
        t_vec = np.asarray(self.extrinsic_t)
        r_mat = np.linalg.inv(r_mat).reshape(3, 3)
        t_vec = -np.dot(r_mat, t_vec).reshape(3)
        self.extrinsic_r = r_mat.tolist()
        self.extrinsic_t = t_vec.tolist()
        self.world2cam = not self.world2cam

    def to_dict(self) -> dict:
        """Dump camera name and parameters to dict.

        Returns:
            dict:
                A dict with all attributes.
        """
        dump_dict = {}
        for attr_name in self.__class__.ATTR_NAMES:
            attr_value = getattr(self, attr_name)
            dump_dict[attr_name] = attr_value
        return dump_dict

    def load_from_dict(self, attr_dict: dict) -> None:
        """Load camera name and parameters from dict.

        Args:
            attr_dict (dict): dict of attributes
        """
        not_matched_keys = []
        for key, value in attr_dict.items():
            if key in self.__class__.ATTR_NAMES:
                setattr(self, key, value)
            else:
                not_matched_keys.append(key)
        if len(not_matched_keys) > 0:
            # cast a warning in the future
            print('The following keys do not match definition:\n',
                  not_matched_keys)

    def dump(self, json_path: str) -> None:
        """Dump camera name and parameters to a json file.

        Returns:
            dict:
                Put self.name and self.parameters_dict
                in one dict, and dump them to a json file.
        """
        dump_dict = self.to_dict()
        with open(json_path, 'w') as f_write:
            json.dump(dump_dict, f_write)

    def load(self, json_path: str) -> None:
        """Load camera name and parameters from a dumped json file.

        Args:
            json_path (str):
                Path to the dumped json file.
        """
        with open(json_path, 'r') as f_read:
            dumped_dict = json.load(f_read)
        self.load_from_dict(dumped_dict)
