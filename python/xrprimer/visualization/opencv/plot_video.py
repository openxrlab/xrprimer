import os
import shutil
from typing import Union

import cv2
import numpy as np
from tqdm import tqdm

from xrprimer.utils.ffmpeg_utils import (
    VideoInfoReader,
    array_to_video,
    images_to_video,
    video_to_array,
)
from xrprimer.utils.log_utils import get_logger, logging
from xrprimer.utils.path_utils import (
    Existence,
    check_path_existence,
    check_path_suffix,
)
from ..palette.line_palette import LinePalette
from ..palette.point_palette import PointPalette
from .plot_frame import plot_frame as plot_frame_opencv


def plot_video(
    # output args
    output_path: str,
    overwrite: bool = True,
    return_array: bool = False,
    # plot args
    batch_size: int = 1000,
    mframe_point_data: Union[np.ndarray, None] = None,
    mframe_line_data: Union[np.ndarray, None] = None,
    mframe_point_mask: Union[np.ndarray, None] = None,
    mframe_line_mask: Union[np.ndarray, None] = None,
    point_palette: Union[PointPalette, None] = None,
    line_palette: Union[LinePalette, None] = None,
    # background args
    background_arr: Union[np.ndarray, None] = None,
    background_dir: Union[np.ndarray, None] = None,
    background_video: Union[np.ndarray, None] = None,
    height: Union[int, None] = None,
    width: Union[int, None] = None,
    # verbose args
    disable_tqdm: bool = True,
    logger: Union[None, str,
                  logging.Logger] = None) -> Union[np.ndarray, None]:
    """Plot a video(or a number of images) with opencv. For plot args, please
    offer either points or lines, or both. For background args, please offer
    only one of them.

    Args:
        output_path (str):
            Path to the output mp4 video file or image directory.
        overwrite (bool, optional):
            Whether to overwrite the file at output_path.
            Defaults to True.
        return_array (bool, optional):
            Whether to return the video array. If True,
            please make sure your RAM is enough for the video.
            Defaults to False, return None.
        batch_size (int, optional):
            How many frames will be in RAM at the same
            time when plotting.
            Defaults to 1000.
        mframe_point_data (Union[np.ndarray, None], optional):
            Multi-frame point data,
            in shape [n_frame, n_point, 2].
            Defaults to None.
        mframe_line_data (Union[np.ndarray, None], optional):
            Multi-frame line data, locations for line ends,
            in shape [n_frame, n_line, 2].
            Defaults to None. Defaults to None.
        mframe_point_mask (Union[np.ndarray, None], optional):
            Visibility mask of multi-frame point data,
            in shape [n_frame, n_point].
            Defaults to None.
        mframe_line_mask (Union[np.ndarray, None], optional):
            Visibility mask of multi-frame line data,
            in shape [n_frame, n_line].
            Defaults to None. Defaults to None.
        point_palette (Union[PointPalette, None], optional):
            An instance of PointPalette. Color and
            visibility are kept by point_palette.
            Defaults to None, do not plot points.
        line_palette (Union[LinePalette, None], optional):
            An instance of LinePalette. Connection,
            color and
            visibility are kept by point_palette.
            Defaults to None, do not plot lines.
        background_arr (Union[np.ndarray, None], optional):
            Background image array. Defaults to None.
        background_dir (Union[np.ndarray, None], optional):
            Path to the image directory for background.
            Defaults to None.
        background_video (Union[np.ndarray, None], optional):
            Path to the video for background.
            Defaults to None.
        height (Union[int, None], optional):
            Height of background. Defaults to None.
        width (Union[int, None], optional):
            Width of background. Defaults to None.
        disable_tqdm (bool, optional):
            Whether to disable tqdm progress bar.
            Defaults to True.
        logger (Union[None, str, logging.Logger], optional):
            Logger for logging. If None, root logger will be selected.
            Defaults to None.

    Returns:
        Union[np.ndarray, None]:
            Plotted multi-frame image array or None.
            If it's an array, its shape shall be
            [n_frame, height, width, 3].
    """
    logger = get_logger(logger)
    # check parent and whether to overwrite
    _check_output_path(
        output_path=output_path, overwrite=overwrite, logger=logger)
    # check if only one background source
    background_len = _check_background(
        background_arr=background_arr,
        background_dir=background_dir,
        background_video=background_video,
        height=height,
        width=width,
        logger=logger)
    # check if data matches background
    data_len = _check_data_len(
        mframe_point_data=mframe_point_data,
        mframe_line_data=mframe_line_data,
        background_len=background_len,
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
    # to prevent OOM
    batch_size = min(batch_size, data_len)
    if return_array or write_video:
        img_list = []
    # to save time for list file and sort
    file_names_cache = None
    for start_idx in tqdm(
            range(0, data_len, batch_size), disable=disable_tqdm):
        end_idx = min(start_idx + batch_size, data_len)
        # prepare background array for this batch
        if background_arr is not None:
            background_arr_batch = background_arr[start_idx:end_idx,
                                                  ...].copy()
        elif background_dir is not None:
            file_names_cache = file_names_cache \
                if file_names_cache is not None \
                else sorted(os.listdir(background_dir))
            file_names_batch = file_names_cache[start_idx:end_idx]
            background_list_batch = []
            for file_name in file_names_batch:
                background_list_batch.append(
                    np.expand_dims(
                        cv2.imread(os.path.join(background_dir, file_name)),
                        axis=0))
            background_arr_batch = np.concatenate(
                background_list_batch, axis=0)
        elif background_video is not None:
            background_arr_batch = video_to_array(
                background_video, start=start_idx, end=end_idx)
        else:
            background_arr_batch = np.zeros(
                shape=(end_idx - start_idx, height, width, 3), dtype=np.uint8)
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
            background_sframe = background_arr_batch[abs_idx - start_idx]
            result_sframe = plot_frame_opencv(
                point_palette=point_palette,
                line_palette=line_palette,
                background_arr=background_sframe,
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


def _check_background(background_arr: Union[np.ndarray, None],
                      background_dir: Union[np.ndarray, None],
                      background_video: Union[np.ndarray,
                                              None], height: Union[int, None],
                      width: Union[int, None], logger: logging.Logger) -> int:
    candidates = [background_arr, background_dir, background_video]
    not_none_count = 0
    for candidate in candidates:
        if candidate is not None:
            not_none_count += 1
    if height is not None and width is not None:
        not_none_count += 1
    if not_none_count != 1:
        logger.error('Please pass only one background source' +
                     ' among background_arr, background_dir,' +
                     ' background_video and height+width.')
        raise ValueError
    if background_arr is not None:
        return background_arr.shape[0]
    elif background_dir is not None:
        return len(os.listdir(background_dir))
    elif background_video is not None:
        reader = VideoInfoReader(background_video, logger)
        return int(reader['nb_frames'])
    else:
        return -1


def _check_data_len(mframe_point_data: Union[np.ndarray, None],
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
