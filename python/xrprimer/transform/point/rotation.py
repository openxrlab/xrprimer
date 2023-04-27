from typing import Union

import numpy as np

from xrprimer.utils.log_utils import get_logger, logging

try:
    import torch
    has_torch = True
    import_exception = ''
except (ImportError, ModuleNotFoundError):
    has_torch = False
    import traceback
    stack_str = ''
    for line in traceback.format_stack():
        if 'frozen' not in line:
            stack_str += line + '\n'
    import_exception = traceback.format_exc() + '\n'
    import_exception = stack_str + import_exception


class Points3DRotation:
    """Rotation for 3D points or 3D vectors."""

    def __init__(self,
                 rotmat: Union[np.ndarray, 'torch.Tensor'],
                 left_mm: bool = True,
                 logger: Union[None, str, logging.Logger] = None) -> None:
        """
        Args:
            rotmat (Union[np.ndarray, torch.Tensor]):
                Rotation matrix in shape [3, 3].
            left_mm (bool, optional):
                Whether to do left multiplication.
                Defaults to True.
            logger (Union[None, str, logging.Logger], optional):
                Logger for logging. If None, root logger will be selected.
                Defaults to None.

        """
        self.rotmat = rotmat
        self.left_mm = left_mm
        self.logger = get_logger(logger)
        if not has_torch:
            self.logger.error(import_exception)
            raise ImportError

    def __call__(
        self, points3d: Union[np.ndarray, 'torch.Tensor']
    ) -> Union[np.ndarray, 'torch.Tensor']:
        """Rotate 3D points or 3D vectors.

        Args:
            points3d (Union[np.ndarray, torch.Tensor]):
                3D points or 3D vectors in shape [..., 3].
        """
        shape_backup = points3d.shape
        if shape_backup[-1] != 3:
            self.logger.error('The last dimension of 3D data should be 3.')
            raise ValueError
        flat_data = _copy_array_tensor(points3d).reshape(-1, 3)
        if self.left_mm:
            rotated_data = (self.rotmat @ flat_data.T).T
        else:
            self.logger.error('Right multiplication is not supported yet.')
            raise NotImplementedError
        rotated_data = rotated_data.reshape(*shape_backup)
        return rotated_data


def _copy_array_tensor(
    data: Union[np.ndarray,
                'torch.Tensor']) -> Union[np.ndarray, 'torch.Tensor']:
    if isinstance(data, np.ndarray):
        return data.copy()
    else:
        return data.clone()
