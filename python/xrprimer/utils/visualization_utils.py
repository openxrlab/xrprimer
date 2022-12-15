# yapf: disable
import logging
from typing import Union

import numpy as np
import torch

from xrprimer.utils.log_utils import get_logger

# yapf: enable


def fix_arr_type(array: Union[list, np.ndarray, torch.Tensor]) -> np.ndarray:
    """Convert array-like data into ndarray.

    Args:
        array (Union[list, np.ndarray, torch.Tensor]):
            The input array.

    Returns:
        np.ndarray
    """
    if isinstance(array, torch.Tensor):
        array = array.detach().cpu().numpy()
    else:
        array = np.array(array)
    return array


def fix_arr_shape(
        array: np.ndarray,
        array_name: str,
        target_len: Union[int, None] = None,
        logger: Union[None, str, logging.Logger] = None) -> np.ndarray:
    """Fix shape of arrays in palette.

    Args:
        array (np.ndarray):
            The input array, in shape [d], [1, d] or [n, d].
        array_name (str):
            Name of this array. Useful for log.
        target_len (Union[int, None], optional):
            Target length of this array.
            Defaults to None, no specific length.
        logger (Union[None, str, logging.Logger], optional):
            Logger for logging. If None, root logger will be selected.
            Defaults to None.

    Raises:
        ValueError: len(array.shape) > 2.
        ValueError: len(array) != target_len and len(array) != 1.

    Returns:
        np.ndarray: resized array in shape [n, d].
    """
    logger = get_logger(logger)
    # check and fix ndim
    if len(array.shape) == 1:
        array = np.expand_dims(array, axis=0)
    elif len(array.shape) > 2:
        logger.error(f'{array_name} has a wrong shape!' +
                     ' Expecting (d, ) or (n, d),' +
                     f' getting {array.shape}.')
        raise ValueError
    # check and fix len
    if target_len is not None:
        if len(array) == 1:
            array = np.repeat(array, target_len, axis=0)
        elif len(array) != target_len:
            logger.error(f'{array_name} has a wrong shape!' +
                         f' Expecting (1, d) or ({target_len}, d),' +
                         f' getting {array.shape}.')
            raise ValueError
    return array
