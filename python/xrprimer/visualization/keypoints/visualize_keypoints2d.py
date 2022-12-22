# yapf: disable
from typing import Union

import numpy as np

from xrprimer.data_structure.keypoints import Keypoints
from xrprimer.transform.limbs import get_limbs_from_keypoints
from xrprimer.utils.log_utils import get_logger, logging
from ..opencv.plot_video import plot_video
from ..palette import LinePalette, PointPalette, get_different_colors

# yapf: enable


def visualize_keypoints2d(
    # input args
    keypoints: Keypoints,
    # output args
    output_path: str,
    overwrite: bool = True,
    return_array: bool = False,
    plot_points: bool = True,
    plot_lines: bool = True,
    # background args
    backgroud_arr: Union[np.ndarray, None] = None,
    backgroud_dir: Union[np.ndarray, None] = None,
    backgroud_video: Union[np.ndarray, None] = None,
    height: Union[int, None] = None,
    width: Union[int, None] = None,
    # verbose args
    disable_tqdm: bool = True,
    logger: Union[None, str,
                  logging.Logger] = None) -> Union[None, np.ndarray]:
    """Visualize multi-frame keypoints2d by OpenCV. For plot args, please
    either plot_points or plot_lines, or both. For background args, please
    offer only one of them.

    Args:
        keypoints (Keypoints):
            An instance of class Keypoints. If n_person > 1,
            each person has its own color, else each point
            and line has different color.
        output_path (str):
            Path to the output mp4 video file or image directory.
        overwrite (bool, optional):
            Whether to overwrite the file at output_path.
            Defaults to True.
        return_array (bool, optional):
            Whether to return the video array. If True,
            please make sure your RAM is enough for the video.
            Defaults to False, return None.
        plot_points (bool, optional):
            Whether to plot points according to keypoints'
            location.
            Defaults to True.
        plot_lines (bool, optional):
            Whether to plot lines according to keypoints'
            limbs. Defaults to True.
        backgroud_arr (Union[np.ndarray, None], optional):
            Background image array. Defaults to None.
        backgroud_dir (Union[np.ndarray, None], optional):
            Path to the image directory for background.
            Defaults to None.
        backgroud_video (Union[np.ndarray, None], optional):
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

    Raises:
        ValueError: Neither plot_points nor plot_lines is True.

    Returns:
        Union[np.ndarray, None]:
            Plotted multi-frame image array or None.
            If it's an array, its shape shall be
            [n_frame, height, width, 3].
    """
    logger = get_logger(logger)
    if not plot_points and not plot_lines:
        logger.error('plot_points or plot_lines must be True.')
        raise ValueError
    n_frame = keypoints.get_frame_number()
    n_person = keypoints.get_person_number()
    n_kps = keypoints.get_keypoints_number()
    mperson_colors = get_different_colors(
        number_of_colors=n_person,
        enable_random=False,
        mode='rgb',
        logger=logger)
    if plot_points:
        point_template = keypoints.get_keypoints()[0, 0, ...]
        point_palette_list = []
        # construct palette for each person
        for person_idx in range(n_person):
            point_palette = PointPalette(
                point_array=point_template,
                name=f'point_palette_{person_idx}',
                color_array=mperson_colors[person_idx],
                logger=logger)
            point_palette_list.append(point_palette)
        # concat mperson's palette into one
        point_palette = PointPalette.concatenate(point_palette_list, logger)
        mframe_point_data = keypoints.get_keypoints()[..., :2].reshape(
            n_frame, n_person * n_kps, 2)
        mframe_point_mask = keypoints.get_mask().reshape(
            n_frame, n_person * n_kps)
        # if only one person,
        # use different colors for different points
        if n_person == 1:
            point_colors = get_different_colors(
                number_of_colors=n_kps, mode='rgb', logger=logger)
            point_palette.set_color_array(point_colors)
    else:
        point_palette = None
        mframe_point_data = None
        mframe_point_mask = None
    if plot_lines:
        limbs = get_limbs_from_keypoints(keypoints=keypoints, )
        point_template = keypoints.get_keypoints()[0, 0, ...]
        conn = limbs.get_connections()
        conn_array = np.asarray(conn)
        n_line = len(conn)
        line_palette_list = []
        # construct palette for each person
        for person_idx in range(n_person):
            line_palette = LinePalette(
                conn_array=conn_array,
                point_array=point_template,
                name=f'line_palette_{person_idx}',
                color_array=mperson_colors[person_idx],
                logger=logger)
            line_palette_list.append(line_palette)
        # concat mperson's palette into one
        line_palette = LinePalette.concatenate(line_palette_list, logger)
        mframe_line_data = keypoints.get_keypoints()[..., :2].reshape(
            n_frame, n_person * n_kps, 2)
        mframe_line_mask = np.ones(shape=(n_frame, n_person * n_line))
        point_mask = keypoints.get_mask()
        # if both two points of a line has mask 1
        # the line gets mask 1
        for frame_idx in range(n_frame):
            for person_idx in range(n_person):
                for conn_idx, point_idxs in enumerate(conn):
                    valid_flag = 1
                    for point_idx in point_idxs:
                        valid_flag *= point_mask[frame_idx, person_idx,
                                                 point_idx]
                    if valid_flag > 0:
                        mframe_line_mask[frame_idx,
                                         person_idx * n_line + conn_idx] = 1
                    else:
                        mframe_line_mask[frame_idx,
                                         person_idx * n_line + conn_idx] = 0
        # if only one person,
        # use different colors for different parts
        if n_person == 1:
            conn_colors = get_different_colors(
                number_of_colors=n_line, mode='rgb', logger=logger)
            line_palette.set_color_array(conn_colors)
    else:
        line_palette = None
        mframe_line_data = None
        mframe_line_mask = None
    ret_value = plot_video(
        output_path=output_path,
        overwrite=overwrite,
        return_array=return_array,
        mframe_point_data=mframe_point_data,
        mframe_line_data=mframe_line_data,
        mframe_point_mask=mframe_point_mask,
        mframe_line_mask=mframe_line_mask,
        point_palette=point_palette,
        line_palette=line_palette,
        backgroud_arr=backgroud_arr,
        backgroud_dir=backgroud_dir,
        backgroud_video=backgroud_video,
        height=height,
        width=width,
        disable_tqdm=disable_tqdm,
        logger=logger)
    return ret_value
