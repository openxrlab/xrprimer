# yapf: disable
import logging
from typing import Union

import numpy as np
import torch

from xrprimer.utils.log_utils import get_logger

# yapf: enable


def fix_arr_type(array: Union[list, np.ndarray, torch.Tensor]):
    if isinstance(array, torch.Tensor):
        array = array.detach().cpu().numpy()
    else:
        array = np.array(array)
    return array


def fix_arr_shape(array: np.ndarray,
                  array_name: str,
                  target_len: Union[int, None] = None,
                  logger: Union[None, str, logging.Logger] = None):
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
