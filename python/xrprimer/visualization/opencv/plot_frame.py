from typing import Union, overload

import cv2
import numpy as np

from xrprimer.transform.image.color import bgr2rgb
from xrprimer.utils.log_utils import get_logger, logging
from xrprimer.visualization.palette.line_palette import LinePalette
from xrprimer.visualization.palette.point_palette import PointPalette


@overload
def plot_frame(point_palette: Union[PointPalette, None],
               backgroud_arr: Union[np.ndarray, None] = None,
               height: Union[int, None] = None,
               width: Union[int, None] = None,
               line_thickness: Union[str, int] = 'auto',
               point_radius: Union[str, int] = 'auto',
               logger: Union[None, str, logging.Logger] = None) -> np.ndarray:
    ...


@overload
def plot_frame(line_palette: Union[PointPalette, None],
               backgroud_arr: Union[np.ndarray, None] = None,
               height: Union[int, None] = None,
               width: Union[int, None] = None,
               line_thickness: Union[str, int] = 'auto',
               point_radius: Union[str, int] = 'auto',
               logger: Union[None, str, logging.Logger] = None) -> np.ndarray:
    ...


@overload
def plot_frame(point_palette: Union[PointPalette, None],
               line_palette: Union[PointPalette, None],
               backgroud_arr: Union[np.ndarray, None] = None,
               height: Union[int, None] = None,
               width: Union[int, None] = None,
               line_thickness: Union[str, int] = 'auto',
               point_radius: Union[str, int] = 'auto',
               logger: Union[None, str, logging.Logger] = None) -> np.ndarray:
    ...


def plot_frame(point_palette: Union[PointPalette, None] = None,
               line_palette: Union[LinePalette, None] = None,
               backgroud_arr: Union[np.ndarray, None] = None,
               height: Union[int, None] = None,
               width: Union[int, None] = None,
               line_thickness: Union[str, int] = 'auto',
               point_radius: Union[str, int] = 'auto',
               logger: Union[None, str, logging.Logger] = None) -> np.ndarray:
    logger = get_logger(logger)
    # check if input is valid
    if point_palette is None and \
            line_palette is None:
        logger.error('To plot a frame, please offer either point_palette' +
                     ' or line_palette, or both.')
        raise RuntimeError
    # decide canvas
    if backgroud_arr is not None and (height is not None or width is not None):
        logger.error('To plot a frame, please offer either backgroud_arr' +
                     ' or [height, width], not both.')
        raise RuntimeError
    if backgroud_arr is not None:
        canvas = backgroud_arr
        # gray to rgb
        if len(canvas.shape) == 2:
            canvas = np.expand_dims(canvas, axis=-1)
            canvas = np.repeat(canvas, 3, axis=2)
    else:
        if height is not None and width is not None:
            canvas = np.ones(
                shape=(int(height), int(width), 3), dtype=np.uint8)
        else:
            logger.error('To plot a frame without background,' +
                         ' please offer height and width.')
            raise ValueError
    # draw lines on canvas
    if line_palette is not None:
        if line_thickness == 'auto':
            line_thickness = max(int(min(canvas.shape[:2]) / 300), 1)
        else:
            line_thickness = int(line_thickness)
        color_array = bgr2rgb(line_palette.color_array.copy())
        for line_idx in range(len(line_palette)):
            conn_mask = line_palette.conn_mask[line_idx]
            if conn_mask == 0:
                continue
            conn = line_palette.conn_array[line_idx]
            points = np.around(
                line_palette.point_array[conn, :], decimals=0).astype(np.int32)
            color = color_array[line_idx]
            cv2.line(
                img=canvas,
                pt1=points[0],
                pt2=points[1],
                color=color.tolist(),
                thickness=line_thickness)
    # draw points on canvas
    if point_palette is not None:
        if point_radius == 'auto':
            point_radius = max(int(min(canvas.shape[:2]) / 70), 1)
        else:
            point_radius = int(point_radius)
        color_array = bgr2rgb(point_palette.color_array.copy())
        for point_idx in range(len(point_palette)):
            point_mask = point_palette.point_mask[point_idx]
            if point_mask == 0:
                continue
            point_loc = np.around(
                point_palette.point_array[point_idx, :],
                decimals=0).astype(np.int32)
            color = color_array[point_idx]
            cv2.circle(
                img=canvas,
                center=point_loc[:2],
                radius=point_radius,
                color=color.tolist(),
                thickness=-1)
    return canvas
