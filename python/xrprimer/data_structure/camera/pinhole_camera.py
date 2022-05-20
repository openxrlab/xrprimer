import copy
from typing import Union

from xrprimer_cpp.camera import \
    PinholeCameraParameter as PinholeCameraParameter_cpp
from .camera import BaseCameraParameter


class PinholeCameraParameter(PinholeCameraParameter_cpp, BaseCameraParameter):
    ATTR_NAMES = BaseCameraParameter.ATTR_NAMES.copy()

    def __init__(self,
                 K: Union[list, None] = None,
                 R: Union[list, None] = None,
                 T: Union[list, None] = None,
                 name: str = 'default',
                 height: int = 1080,
                 width: int = 1920,
                 world2cam: bool = True,
                 convention: str = 'opencv') -> None:
        PinholeCameraParameter_cpp.__init__(self)
        BaseCameraParameter.__init__(
            self,
            K=K,
            R=R,
            T=T,
            name=name,
            height=height,
            width=width,
            world2cam=world2cam,
            convention=convention)

    def clone(self) -> 'PinholeCameraParameter':
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
        return new_cam_param

    def SaveFile(self, filename: str) -> int:
        """Dump camera name and parameters to a json file.

        Args:
            filename (str):
                Path to the dumped json file.

        Returns:
            int: returns 0.
        """
        return super(PinholeCameraParameter_cpp, self).SaveFile(filename)

    def LoadFile(self, filename: str) -> int:
        """Load camera name and parameters from a dumped json file.

        Args:
            filename (str):
                Path to the dumped json file.

        Returns:
            int: returns 0.
        """
        return super(PinholeCameraParameter_cpp, self).LoadFile(filename)
