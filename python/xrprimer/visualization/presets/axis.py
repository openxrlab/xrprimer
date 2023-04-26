from typing import Union

import numpy as np

from xrprimer.utils.log_utils import get_logger, logging
from ..palette import LinePalette


def create_coordinate_axis(
        axis_length: float = 1.0,
        location: Union[np.ndarray, None] = None,
        logger: Union[None, str, logging.Logger] = None) -> LinePalette:
    """Create a coordinate axis at the given location, scaled to the given
    size, and return an instance of LinePalette. Colors of each axis are
    (red-x, green-y, blue-z) respectively.

    Args:
        axis_length (float, optional):
            Length of each axis. Defaults to 1.0.
        location (Union[np.ndarray, None], optional):
            Location of the coordinate axis. Defaults to None,
            the axis will be placed at the origin.
        logger (Union[None, str, logging.Logger], optional):
            Logger for logging. If None, root logger will be selected.
            Defaults to None.

    Returns:
        LinePalette:
            A LinePalette instance of the coordinate axis.
    """
    logger = get_logger(logger)
    point_array = np.array(((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)),
                           dtype=np.float32)
    # scale the axis
    point_array *= axis_length
    # translate the axis according to location
    if location is not None:
        location = location.reshape(-1)
        if location.shape[0] != 3:
            logger.error(
                f'location should be in shape[3], but got {location.shape}')
            raise ValueError
        point_array += location
    axis_palette = LinePalette(
        conn_array=np.array(((0, 1), (0, 2), (0, 3))),
        point_array=point_array,
        name='coordinate_axis_line_palette',
        color_array=np.array(((255, 0, 0), (0, 255, 0), (0, 0, 255))),
        logger=logger)
    return axis_palette
