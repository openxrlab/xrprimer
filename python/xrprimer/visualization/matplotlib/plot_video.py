# yapf: disable
import os
from typing import List, Tuple, Union

import cv2
import numpy as np
from tqdm import tqdm

from xrprimer.utils.ffmpeg_utils import VideoWriter
from xrprimer.utils.log_utils import get_logger, logging
from xrprimer.utils.path_utils import check_path_suffix
from xrprimer.utils.visualization_utils import (
    check_data_len,
    check_mframe_data_src,
    check_output_path,
)
from ..palette.line_palette import LinePalette
from ..palette.point_palette import PointPalette
from .plot_frame import _get_visual_range
from .plot_frame import plot_frame as plot_frame_matplotlib

# yapf: enable


def plot_video(
    # output args
    output_path: str,
    overwrite: bool = True,
    return_array: bool = False,
    # conditional output args
    fps: Union[float, None] = None,
    img_format: Union[str, None] = None,
    # plot args
    visual_range: Union[None, np.ndarray] = None,
    mframe_point_data: Union[np.ndarray, None] = None,
    mframe_line_data: Union[np.ndarray, None] = None,
    mframe_point_mask: Union[np.ndarray, None] = None,
    mframe_line_mask: Union[np.ndarray, None] = None,
    point_palette: Union[PointPalette, None] = None,
    line_palette: Union[LinePalette, None] = None,
    dpi: float = 180.0,
    # verbose args
    disable_tqdm: bool = False,
    logger: Union[None, str,
                  logging.Logger] = None) -> Union[np.ndarray, None]:
    """Plot a video(or a number of images) with matplotlib. For plot args,
    please offer either points or lines, or both.

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
        visual_range (Union[None, np.ndarray], optional):
            Visible range array whose shape is [3, 2],
            ((x_min, x_max), (y_min, y_max), (z_min, z_max))
            Defaults to None, calculated from data whose mask==1.
        mframe_point_data (Union[np.ndarray, None], optional):
            Multi-frame point data,
            in shape [n_frame, n_point, 3].
            Defaults to None.
        mframe_line_data (Union[np.ndarray, None], optional):
            Multi-frame line data, locations for line ends,
            in shape [n_frame, n_point, 3].
            Defaults to None.
        mframe_point_mask (Union[np.ndarray, None], optional):
            Visibility mask of multi-frame point data,
            in shape [n_frame, n_point].
            Defaults to None.
        mframe_line_mask (Union[np.ndarray, None], optional):
            Visibility mask of multi-frame line data,
            in shape [n_frame, n_line].
            Defaults to None.
        point_palette (Union[PointPalette, None], optional):
            An instance of PointPalette. Color and
            visibility are kept by point_palette.
            Defaults to None, do not plot points.
        line_palette (Union[LinePalette, None], optional):
            An instance of LinePalette. Connection,
            color and
            visibility are kept by point_palette.
            Defaults to None, do not plot lines.
        dpi (float, optional):
            Resolution of the figure in dots-per-inch as a float.
            Defaults to 180.0.
        disable_tqdm (bool, optional):
            Whether to disable tqdm progress bar.
            Defaults to False.
        logger (Union[None, str, logging.Logger], optional):
            Logger for logging. If None, root logger will be selected.
            Defaults to None.

    Returns:
        Union[np.ndarray, None]: _description_
    """
    logger = get_logger(logger)
    # check parent and whether to overwrite
    check_output_path(
        output_path=output_path, overwrite=overwrite, logger=logger)
    # check if no fewer than one mframe data source
    check_mframe_data_src(
        mframe_point_data=mframe_point_data,
        mframe_line_data=mframe_line_data,
        logger=logger)
    # check if data matches background
    data_to_check = [
        mframe_point_data,
        mframe_line_data,
    ]
    data_len = check_data_len(data_list=data_to_check, logger=logger)
    # init some var
    video_writer = None
    arr_to_return = None
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
    # auto visual_range if None
    if visual_range is None:
        points3d = None
        if point_palette is not None:
            if mframe_point_mask is not None:
                n_frame, n_point = mframe_point_mask.shape
                valid_idxs = np.where(mframe_point_mask.reshape(-1) == 1)
                points3d = mframe_point_data.reshape(n_frame * n_point,
                                                     -1)[valid_idxs[0], :]
            else:
                n_frame, n_point, _ = mframe_point_data.shape
                points3d = mframe_point_data.reshape(n_frame * n_point, -1)
        if line_palette is not None:
            if mframe_line_mask is not None:
                valid_idxs = np.where(mframe_line_mask == 1)
            else:
                n_line = len(line_palette.conn_mask)
                n_frame = mframe_line_data.shape[0]
                valid_idxs = (
                    np.arange(n_frame).reshape(1,
                                               -1).repeat(n_line,
                                                          axis=0).reshape(-1),
                    np.arange(n_line).reshape(-1,
                                              1).repeat(n_frame,
                                                        axis=1).reshape(-1),
                )
            for frame_idx, line_idx in zip(valid_idxs[0], valid_idxs[1]):
                valid_point_idxs = line_palette.conn_array[line_idx, :]
                valid_points = mframe_line_data[frame_idx, valid_point_idxs, :]
                if points3d is None:
                    points3d = valid_points
                else:
                    points3d = np.concatenate((points3d, valid_points), axis=0)
        visual_range = _get_visual_range(
            points_array=points3d, scale=1.1, logger=logger)
    lat_long_list = _get_camera_positions(n_frames=data_len)
    # to save time for list file and sort
    for frame_idx in tqdm(range(0, data_len), disable=disable_tqdm):
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
        result_sframe = plot_frame_matplotlib(
            point_palette=point_palette,
            line_palette=line_palette,
            visual_range=visual_range,
            cam_latitude=lat_long_list[frame_idx][0],
            cam_longtitude=lat_long_list[frame_idx][1],
            dpi=dpi,
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
    return arr_to_return if return_array else None


def _get_camera_positions(
        n_frames: int,
        latitude_speed: float = 0.0,
        longtitude_speed: float = 0.5) -> List[Tuple[float, float]]:
    cam_polar_positions = [
        (10.0, 45.0),
    ]
    latitude_sign = 1
    longtitude_sign = 1
    for _ in range(n_frames - 1):
        last_latitude = cam_polar_positions[-1][0]
        # try to go forward with the current sign
        new_latitude = latitude_sign * latitude_speed + last_latitude
        if new_latitude >= 90 - 2 * latitude_speed or \
                new_latitude <= 2 * latitude_speed:
            # reaching border, go backward
            latitude_sign *= -1
            new_latitude = latitude_sign * latitude_speed + last_latitude
        last_longtitude = cam_polar_positions[-1][1]
        # try to go forward with the current sign
        new_longtitude = longtitude_sign * longtitude_speed + last_longtitude
        if new_longtitude >= 90 - 2 * longtitude_speed or \
                new_longtitude <= 2 * longtitude_speed:
            # reaching border, go backward
            longtitude_sign *= -1
            new_longtitude = longtitude_sign * \
                longtitude_speed + last_longtitude
        cam_polar_positions.append([new_latitude, new_longtitude])
    return cam_polar_positions
