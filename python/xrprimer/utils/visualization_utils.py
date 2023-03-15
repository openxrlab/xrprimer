# yapf: disable
import logging
import os
from typing import Union

import numpy as np
import torch

from xrprimer.utils.log_utils import get_logger
from .path_utils import Existence, check_path_existence, check_path_suffix

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


def check_data_len(mframe_point_data: Union[np.ndarray, None],
                   mframe_line_data: Union[np.ndarray, None],
                   background_len: int, logger: logging.Logger) -> int:
    empty_data = True
    len_list = []
    if background_len > 0:
        len_list.append(background_len)
    if mframe_point_data is not None:
        empty_data = False
        len_list.append(mframe_point_data.shape[0])
    if mframe_line_data is not None:
        empty_data = False
        len_list.append(mframe_line_data.shape[0])
    if empty_data:
        logger.error('Please pass point_data or line_data or both.')
        raise ValueError
    ref_len = len_list[0]
    len_correct = True
    for tmp_len in len_list:
        if tmp_len != ref_len:
            len_correct = False
            break
    if not len_correct:
        logger.error('Length of point_data, line_data' +
                     ' and background do not match.')
        raise ValueError
    else:
        return ref_len


def check_output_path(output_path: str, overwrite: bool,
                      logger: logging.Logger) -> None:
    existence = check_path_existence(output_path)
    if existence == Existence.MissingParent:
        logger.error(f'Parent of {output_path} doesn\'t exist.')
        raise FileNotFoundError
    elif (existence == Existence.DirectoryExistNotEmpty
          or existence == Existence.FileExist) and not overwrite:
        logger.error(f'{output_path} exists and overwrite not enabled.')
        raise FileExistsError
    if not check_path_suffix(output_path, '.mp4'):
        os.makedirs(output_path, exist_ok=True)
