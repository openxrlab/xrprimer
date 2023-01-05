import logging
from typing import Union

import numpy as np

from xrprimer.utils.log_utils import get_logger
from .line_palette import LinePalette
from .point_palette import PointPalette

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal
try:
    import colorsys
    has_colorsys = True
    import_exception = ''
except (ImportError, ModuleNotFoundError):
    has_colorsys = False
    import traceback
    stack_str = ''
    for line in traceback.format_stack():
        if 'frozen' not in line:
            stack_str += line + '\n'
    import_exception = traceback.format_exc() + '\n'
    import_exception = stack_str + import_exception

__all__ = ['PointPalette', 'LinePalette', 'get_different_colors']


def get_different_colors(
        number_of_colors: int,
        enable_random: bool = False,
        alpha: float = 1.0,
        mode: Literal['rgb', 'rgba', 'bgr', 'bgra'] = 'rgb',
        logger: Union[None, str, logging.Logger] = None) -> np.ndarray:
    """Get n different colors in one array. The distance between any two colors
    will not be too close.

    Args:
        number_of_colors (int):
            How many colors to get.
        enable_random (bool, optional):
            Whether to enable random adjustment for base colors.
            Defaults to False.
        alpha (float, optional):
            Value of the alpha.
            Defaults to 1.0.
        mode (Literal['rgb', 'rgba', 'bgr', 'bgra'], optional):
            Color mode in str.
            Defaults to 'rgb'.

    Returns:
        np.ndarray:
            An array of colors in [n_color, 3] or [n_color, 4].
    """
    if not has_colorsys:
        logger = get_logger(logger)
        logger.error(import_exception)
        raise ImportError
    mode = mode.lower()
    assert set(mode).issubset({'r', 'g', 'b', 'a'})
    colors = []
    for i in np.arange(0.0, 360.0, 360.0 / number_of_colors):
        hue = i / 360.0
        lightness_offset = np.random.rand() if enable_random else 0
        saturation_offset = np.random.rand() if enable_random else 0
        lightness = (50 + lightness_offset * 10) / 100.
        saturation = (90 + saturation_offset * 10) / 100.
        colors.append(colorsys.hls_to_rgb(hue, lightness, saturation))
    colors_bgr = (np.asarray(colors) * 255).astype(np.uint8)
    color_dict = {}
    if 'a' in mode:
        color_dict['a'] = np.ones((number_of_colors, 1)) * alpha
    color_dict['b'] = colors_bgr[:, 0:1]
    color_dict['g'] = colors_bgr[:, 1:2]
    color_dict['r'] = colors_bgr[:, 2:3]
    colors_final = []
    for channel in mode:
        colors_final.append(color_dict[channel])
    colors_final = np.concatenate(colors_final, -1)
    return colors_final
