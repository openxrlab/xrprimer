import io
from typing import Union

import cv2
import numpy as np

from xrprimer.utils.log_utils import get_logger, logging
from xrprimer.visualization.palette.line_palette import LinePalette
from xrprimer.visualization.palette.point_palette import PointPalette

try:
    from matplotlib import pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    has_matplotlib = True
    import_exception = ''
except (ImportError, ModuleNotFoundError):
    has_matplotlib = False
    import traceback
    stack_str = ''
    for line in traceback.format_stack():
        if 'frozen' not in line:
            stack_str += line + '\n'
    import_exception = traceback.format_exc() + '\n'
    import_exception = stack_str + import_exception


def plot_frame(point_palette: Union[PointPalette, None] = None,
               line_palette: Union[LinePalette, None] = None,
               visual_range: Union[None, np.ndarray] = None,
               cam_latitude: float = 10.0,
               cam_longitude: float = 45.0,
               linewidth: float = 2.0,
               markersize: float = 5.0,
               logger: Union[None, str, logging.Logger] = None) -> np.ndarray:
    logger = get_logger(logger)
    if not has_matplotlib:
        logger.error(import_exception)
        raise ImportError
    # check if input is valid
    if point_palette is None and \
            line_palette is None:
        logger.error('To plot a frame, please offer either point_palette' +
                     ' or line_palette, or both.')
        raise RuntimeError
    # confirm visual range
    if visual_range is None:
        points3d = None
        if point_palette is not None:
            points_mask = point_palette.point_mask
            valid_idxs = np.where(points_mask == 1)
            points3d = point_palette.point_array[valid_idxs[0], :]
        if line_palette is not None:
            conn_mask = line_palette.conn_mask
            valid_idxs = np.where(conn_mask == 1)
            valid_conn = line_palette.conn_array[valid_idxs[0], :]
            point_idxs = np.unique(valid_conn.reshape(-1))
            valid_points = line_palette.point_array[point_idxs, :]
            if points3d is None:
                points3d = valid_points
            else:
                points3d = np.concatenate((points3d, valid_points), axis=0)
        visual_range = _get_visual_range(
            points_array=points3d, scale=1.0, logger=logger)
    # create fig
    fig = plt.figure()
    ax = Axes3D(fig, auto_add_to_figure=False)
    fig.add_axes(ax)
    ax.set_xlim(*visual_range[0])
    ax.set_ylim(*visual_range[1])
    ax.set_zlim(*visual_range[2])
    ax.view_init(cam_latitude, cam_longitude)
    # draw lines on canvas
    if line_palette is not None:
        color_array = line_palette.color_array.astype(np.float32) / 255.0
        for line_idx in range(len(line_palette)):
            conn_mask = line_palette.conn_mask[line_idx]
            if conn_mask == 0:
                continue
            conn = line_palette.conn_array[line_idx]
            two_points = line_palette.point_array[conn, :]
            color = color_array[line_idx]
            ax.plot([two_points[0, 0], two_points[1, 0]],
                    [two_points[0, 1], two_points[1, 1]],
                    [two_points[0, 2], two_points[1, 2]],
                    color=color,
                    linewidth=linewidth)
    # draw points on canvas
    if point_palette is not None:
        color_array = point_palette.color_array.astype(np.float32) / 255.0
        for point_idx in range(len(point_palette)):
            point_mask = point_palette.point_mask[point_idx]
            if point_mask == 0:
                continue
            point_loc = point_palette.point_array[point_idx, :]
            color = color_array[point_idx]
            ax.plot([
                point_loc[0],
            ], [
                point_loc[1],
            ], [
                point_loc[2],
            ],
                    marker='o',
                    markersize=markersize,
                    color=color)
    img_arr = _get_cv2mat_from_matplotlib(fig=fig, dpi=180)
    # img_arr = cv2.resize(img_arr, (width, height))
    return img_arr


def _get_visual_range(
        points_array: np.ndarray,
        scale: float,
        logger: Union[None, str, logging.Logger] = None) -> np.ndarray:
    logger = get_logger(logger)
    if scale < 1:
        logger.warning(
            'visual_range smaller than bbox will make some data unvisible.')
    n_dim = points_array.shape[-1]
    flat_array = points_array.reshape(-1, n_dim)
    axis_stat = np.zeros(shape=[n_dim, 4])
    for axis_idx in range(n_dim):
        axis_data = flat_array[:, axis_idx]
        axis_min = np.min(axis_data)
        axis_max = np.max(axis_data)
        axis_mid = (axis_min + axis_max) / 2.0
        axis_span = axis_max - axis_min
        axis_stat[axis_idx] = np.asarray(
            (axis_min, axis_max, axis_mid, axis_span))
    max_span = np.max(axis_stat[:, 3]) * scale
    visual_range = np.zeros_like(axis_stat[:, :2])
    for axis_idx in range(n_dim):
        visual_range[axis_idx, 0] =\
            axis_stat[axis_idx, 2] - max_span/2.0
        visual_range[axis_idx, 1] =\
            axis_stat[axis_idx, 2] + max_span/2.0
    return visual_range


def _get_cv2mat_from_matplotlib(fig, dpi=180) -> np.ndarray:
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=dpi)
    buf.seek(0)
    png_bytes = np.frombuffer(buf.getvalue(), dtype=np.uint8)
    buf.close()
    img_arr = cv2.imdecode(png_bytes, 1)
    return img_arr
