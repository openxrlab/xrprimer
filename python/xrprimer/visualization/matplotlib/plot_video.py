import os
import shutil
from typing import Union

import cv2
import numpy as np
from tqdm import tqdm

from xrprimer.utils.ffmpeg_utils import array_to_video, images_to_video
from xrprimer.utils.log_utils import get_logger, logging
from xrprimer.utils.path_utils import (
    Existence,
    check_path_existence,
    check_path_suffix,
)
from ..palette.line_palette import LinePalette
from ..palette.point_palette import PointPalette
from .plot_frame import _get_visual_range
from .plot_frame import plot_frame as plot_frame_matplotlib


def plot_video(
    # output args
    output_path: str,
    overwrite: bool = True,
    return_array: bool = False,
    # plot args
    batch_size: int = 1000,
    visual_range: Union[None, np.ndarray] = None,
    mframe_point_data: Union[np.ndarray, None] = None,
    mframe_line_data: Union[np.ndarray, None] = None,
    mframe_point_mask: Union[np.ndarray, None] = None,
    mframe_line_mask: Union[np.ndarray, None] = None,
    point_palette: Union[PointPalette, None] = None,
    line_palette: Union[LinePalette, None] = None,
    # verbose args
    disable_tqdm: bool = True,
    logger: Union[None, str,
                  logging.Logger] = None) -> Union[np.ndarray, None]:
    logger = get_logger(logger)
    # check parent and whether to overwrite
    _check_output_path(
        output_path=output_path, overwrite=overwrite, logger=logger)
    # check if data matches background
    data_len = _check_data_len(
        mframe_point_data=mframe_point_data,
        mframe_line_data=mframe_line_data,
        logger=logger)
    # check whether to write video directly or write images first
    if check_path_suffix(output_path, '.mp4'):
        write_video = True
        if batch_size < data_len:
            output_dir = f'{output_path}_temp'
            os.makedirs(output_dir, exist_ok=True)
            write_img = True
            remove_output_dir = True
        else:
            write_img = False
            remove_output_dir = False
    else:
        write_video = False
        output_dir = output_path
        write_img = True
        remove_output_dir = False
    # auto visual_range if None
    if visual_range is None:
        points3d = None
        if point_palette is not None:
            n_frame, n_point = mframe_point_mask.shape
            valid_idxs = np.where(mframe_point_mask.reshape(-1) == 1)
            points3d = mframe_point_data.reshape(n_frame * n_point,
                                                 -1)[valid_idxs[0], :]
        if line_palette is not None:
            n_frame, n_line = mframe_line_mask.shape
            valid_idxs = np.where(mframe_line_mask == 1)
            # TODO: check valid_idxs when
            # 0, 1
            # 1, 0
            valid_conn = line_palette.conn_array[valid_idxs[0], :]
            point_idxs = np.unique(valid_conn.reshape(-1))
            valid_points = line_palette.point_array[point_idxs, :]
            if points3d is None:
                points3d = valid_points
            else:
                points3d = np.concatenate((points3d, valid_points), axis=0)
        visual_range = _get_visual_range(
            points_array=points3d, scale=1.1, logger=logger)
    # to prevent OOM
    batch_size = min(batch_size, data_len)
    if return_array or write_video:
        img_list = []
    # to save time for list file and sort
    for start_idx in tqdm(
            range(0, data_len, batch_size), disable=disable_tqdm):
        end_idx = min(start_idx + batch_size, data_len)
        # plot frames in batch one by one
        batch_results = []
        for abs_idx in range(start_idx, end_idx):
            if point_palette is not None:
                point_palette.set_point_array(mframe_point_data[abs_idx])
                if mframe_point_mask is not None:
                    point_palette.set_point_mask(
                        np.expand_dims(mframe_point_mask[abs_idx], -1))
            if line_palette is not None:
                line_palette.set_point_array(mframe_line_data[abs_idx])
                if mframe_line_mask is not None:
                    line_palette.set_conn_mask(
                        np.expand_dims(mframe_line_mask[abs_idx], -1))
            result_sframe = plot_frame_matplotlib(
                point_palette=point_palette,
                line_palette=line_palette,
                visual_range=visual_range,
                logger=logger)
            batch_results.append(result_sframe)
            if write_img:
                cv2.imwrite(
                    filename=os.path.join(output_dir, f'{abs_idx:06d}.png'),
                    img=result_sframe)
        if return_array or write_video:
            img_list += batch_results
    if return_array or write_video:
        img_arr = np.asarray(img_list)
    if write_video:
        if write_img:
            images_to_video(
                input_folder=output_dir,
                output_path=output_path,
                img_format='%06d.png')
        else:
            array_to_video(image_array=img_arr, output_path=output_path)
        if remove_output_dir:
            shutil.rmtree(output_dir)
    return img_arr if return_array else None


def _check_output_path(output_path: str, overwrite: bool,
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


def _check_data_len(mframe_point_data: Union[np.ndarray, None],
                    mframe_line_data: Union[np.ndarray, None],
                    logger: logging.Logger) -> int:
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
    ref_len = len_list[0]
    if len(len_list) <= 1:
        return ref_len
    else:
        if len_list[1] != ref_len:
            len_correct = False
        else:
            len_correct = True
        if not len_correct:
            logger.error('Length of point_data and line_data' +
                         ' do not match.')
            raise ValueError
        else:
            return ref_len
