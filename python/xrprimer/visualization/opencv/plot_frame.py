from typing import Union, overload

import cv2
import numpy as np

from xrprimer.transform.image.color import rgb2bgr
from xrprimer.utils.log_utils import get_logger, logging
from xrprimer.visualization.palette.line_palette import LinePalette
from xrprimer.visualization.palette.point_palette import PointPalette


@overload
def plot_frame(point_palette: Union[PointPalette, None],
               background_arr: Union[np.ndarray, None] = None,
               height: Union[int, None] = None,
               width: Union[int, None] = None,
               line_thickness: Union[str, int] = 'auto',
               point_radius: Union[str, int] = 'auto',
               logger: Union[None, str, logging.Logger] = None) -> np.ndarray:
    ...


@overload
def plot_frame(line_palette: Union[PointPalette, None],
               background_arr: Union[np.ndarray, None] = None,
               height: Union[int, None] = None,
               width: Union[int, None] = None,
               line_thickness: Union[str, int] = 'auto',
               point_radius: Union[str, int] = 'auto',
               logger: Union[None, str, logging.Logger] = None) -> np.ndarray:
    ...


@overload
def plot_frame(point_palette: Union[PointPalette, None],
               line_palette: Union[PointPalette, None],
               background_arr: Union[np.ndarray, None] = None,
               height: Union[int, None] = None,
               width: Union[int, None] = None,
               line_thickness: Union[str, int] = 'auto',
               point_radius: Union[str, int] = 'auto',
               logger: Union[None, str, logging.Logger] = None) -> np.ndarray:
    ...


def plot_frame(point_palette: Union[PointPalette, None] = None,
               line_palette: Union[LinePalette, None] = None,
               background_arr: Union[np.ndarray, None] = None,
               height: Union[int, None] = None,
               width: Union[int, None] = None,
               line_thickness: Union[str, int] = 'auto',
               point_radius: Union[str, int] = 'auto',
               logger: Union[None, str, logging.Logger] = None) -> np.ndarray:
    """Plot points and/or lines on a single frame, with opencv.

    Args:
        point_palette (Union[PointPalette, None], optional):
            An instance of PointPalette. Location, color and
            visibility are kept by point_palette.
            Defaults to None, do not plot points.
        line_palette (Union[LinePalette, None], optional):
            An instance of LinePalette. Location, connection,
            color and
            visibility are kept by point_palette.
            Defaults to None, do not plot lines.
        background_arr (Union[np.ndarray, None], optional):
            A background image array, in shape [h, w, c].
            If background_arr is not None, do not pass height
            and width.
            Defaults to None, use white background.
        height (Union[int, None], optional):
            Height of the canvas. When background_arr is None,
            size of canvas is decided by height and width.
            Defaults to None.
        width (Union[int, None], optional):
            Width of the canvas. When background_arr is None,
            size of canvas is decided by height and width.
            Defaults to None.
        line_thickness (Union[str, int], optional):
            Thickness of lines in pixel.
            Defaults to 'auto'.
        point_radius (Union[str, int], optional):
            Radius of point circles in pixel.
            Defaults to 'auto'.
        logger (Union[None, str, logging.Logger], optional):
            Logger for logging. If None, root logger will be selected.
            Defaults to None.

    Raises:
        RuntimeError:
            Both point_palette and line_palette are passed.
        RuntimeError:
            Both background_arr and [height, width] are passed.
        ValueError:
            Either height or width is None when background_arr is None.

    Returns:
        np.ndarray: The plotted image array.
    """
    logger = get_logger(logger)
    # check if input is valid
    if point_palette is None and \
            line_palette is None:
        logger.error('To plot a frame, please offer either point_palette' +
                     ' or line_palette, or both.')
        raise RuntimeError
    # decide canvas
    if background_arr is not None and (height is not None
                                       or width is not None):
        logger.error('To plot a frame, please offer either background_arr' +
                     ' or [height, width], not both.')
        raise RuntimeError
    if background_arr is not None:
        canvas = background_arr
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
        color_array = rgb2bgr(line_palette.color_array.copy())
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
        color_array = rgb2bgr(point_palette.color_array.copy())
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
