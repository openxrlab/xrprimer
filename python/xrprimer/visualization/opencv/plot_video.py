import os
from typing import Union

import cv2
import numpy as np
from tqdm import tqdm

from xrprimer.utils.ffmpeg_utils import (
    VideoInfoReader,
    VideoReader,
    VideoWriter,
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
    # conditional output args
    fps: Union[float, None] = None,
    img_format: Union[str, None] = None,
    # plot args
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
        fps (Union[float, None], optional):
            Frames per second for the output video.
            Defaults to None, 30 fps when writing a video.
        img_format (Union[str, None], optional):
            Name format for the output image file.
            Defaults to None, `%06d.png` when writing images.
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
    # init some var
    video_writer = None
    video_reader = None
    arr_to_return = None
    # to save time for list file and sort
    file_names_cache = None
    # check whether to write video or write images
    if check_path_suffix(output_path, '.mp4'):
        write_video = True
        write_img = not write_video
        fps = fps if fps is not None else 30.0
        if img_format is not None:
            logger.warning('Argument img_format is useless when' +
                           ' writing a video. To suppress this warning,' +
                           ' do not pass it.')
    else:
        write_video = False
        write_img = not write_video
        img_format = img_format \
            if img_format is not None \
            else '%06d.png'
        if fps is not None:
            logger.warning('Argument fps is useless when' +
                           ' writing image files. To suppress this warning,' +
                           ' do not pass it.')
    for frame_idx in tqdm(range(0, data_len), disable=disable_tqdm):
        # prepare background array for this batch
        if background_arr is not None:
            background_sframe = background_arr[frame_idx, ...].copy()
        elif background_dir is not None:
            file_names_cache = file_names_cache \
                if file_names_cache is not None \
                else sorted(os.listdir(background_dir))
            file_name = file_names_cache[frame_idx]
            background_sframe = cv2.imread(
                os.path.join(background_dir, file_name))
        elif background_video is not None:
            video_reader = video_reader \
                if video_reader is not None \
                else VideoReader(
                    input_path=background_video,
                    disable_log=True,
                    logger=logger
                )
            background_sframe = video_reader.get_next_frame()
        else:
            background_sframe = np.zeros(
                shape=(height, width, 3), dtype=np.uint8)
        if point_palette is not None:
            point_palette.set_point_array(mframe_point_data[frame_idx])
            if mframe_point_mask is not None:
                point_palette.set_point_mask(
                    np.expand_dims(mframe_point_mask[frame_idx], -1))
        if line_palette is not None:
            line_palette.set_point_array(mframe_line_data[frame_idx])
            if mframe_line_mask is not None:
                line_palette.set_conn_mask(
                    np.expand_dims(mframe_line_mask[frame_idx], -1))
        result_sframe = plot_frame_opencv(
            point_palette=point_palette,
            line_palette=line_palette,
            background_arr=background_sframe,
            logger=logger)
        if write_img:
            cv2.imwrite(
                filename=os.path.join(output_path,
                                      f'{img_format}' % frame_idx),
                img=result_sframe)
        if write_video:
            video_writer = video_writer \
                if video_writer is not None \
                else VideoWriter(
                    output_path=output_path,
                    resolution=result_sframe.shape[:2],
                    fps=fps,
                    n_frames=data_len,
                    disable_log=False,
                    logger=logger
                )
            video_writer.write(result_sframe)
        if return_array:
            unsqueezed_sframe = np.expand_dims(result_sframe, axis=0)
            arr_to_return = unsqueezed_sframe \
                if arr_to_return is None \
                else np.concatenate((arr_to_return, unsqueezed_sframe), axis=0)
    if video_writer is not None:
        video_writer.close()
    if video_reader is not None:
        video_reader.close()
    return arr_to_return if return_array else None


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
