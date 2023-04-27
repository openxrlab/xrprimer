# yapf: disable
import logging
import os
from typing import Union

import numpy as np

from .ffmpeg_utils import VideoInfoReader
from .log_utils import get_logger
from .path_utils import Existence, check_path_existence, check_path_suffix

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

# yapf: enable


def fix_arr_type(array: Union[list, np.ndarray, 'torch.Tensor']) -> np.ndarray:
    """Convert array-like data into ndarray.

    Args:
        array (Union[list, np.ndarray, torch.Tensor]):
            The input array.

    Returns:
        np.ndarray
    """
    if not has_torch:
        raise ImportError(import_exception)
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


def check_mframe_data_src(mframe_point_data: Union[np.ndarray, None],
                          mframe_line_data: Union[np.ndarray, None],
                          logger: logging.Logger) -> int:
    """Check length of data. Return the length if all data match.

    Args:
        mframe_point_data (Union[np.ndarray, None]):
            Mulit-frame point data.
        mframe_line_data (Union[np.ndarray, None]):
            Mulit-frame line data.
        logger (logging.Logger):
            Logger for logging.

    Raises:
        ValueError:
            Length of point_data,
            line_data and background do not match.

    Returns:
        int: 0 for success.
    """
    empty_data = True
    len_list = []
    if mframe_point_data is not None:
        empty_data = False
        len_list.append(mframe_point_data.shape[0])
    if mframe_line_data is not None:
        empty_data = False
        len_list.append(mframe_line_data.shape[0])
    if empty_data:
        logger.error('Please pass point_data or line_data or both.')
        raise ValueError
    return 0


def check_data_len(data_list: list,
                   logger: Union[None, str, logging.Logger] = None) -> int:
    """Check length of data. Return the length if all data match.

    Args:
        data_list (list):
            List of data. Each one is an array-like data,
            or list, or path to a video.

    Raises:
        ValueError:
            Please pass at list one data in data_list.
        ValueError:
            Length of data in data_list do not match.

    Returns:
        int: Length of data.
    """
    len_list = []
    for data in data_list:
        if data is not None:
            # path data
            if isinstance(data, str):
                # path to a video
                if check_path_suffix(data, '.mp4'):
                    reader = VideoInfoReader(data, logger)
                    tmp_len = int(reader['nb_frames'])
                # path to a folder
                else:
                    tmp_len = len(os.listdir(data))
            # array data or list data
            else:
                tmp_len = len(data)
            len_list.append(tmp_len)
    if len(len_list) == 0:
        logger.error('Please pass at list one data in data_list.')
        raise ValueError
    ref_len = len_list[0]
    len_correct = True
    for tmp_len in len_list:
        if tmp_len != ref_len:
            len_correct = False
            break
    if not len_correct:
        logger.error('Length of data in data_list do not match.\n' +
                     'Length list: ' + str(len_list) + '\n' +
                     'Reference length: ' + str(ref_len))
        raise ValueError
    return ref_len


def check_output_path(output_path: str, overwrite: bool,
                      logger: logging.Logger) -> None:
    """Check output path.

    Args:
        output_path (str):
            Path to output.
        overwrite (bool):
            Whether to overwrite existing files.
        logger (logging.Logger):
            Logger for logging.

    Raises:
        FileNotFoundError: Parent of output_path doesn't exist.
        FileExistsError: output_path exists and overwrite not enabled.
    """
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
