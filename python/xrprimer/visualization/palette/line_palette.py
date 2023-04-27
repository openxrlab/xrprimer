# yapf: disable
import logging
from typing import Any, List, Union

import numpy as np

from xrprimer.utils.log_utils import get_logger
from xrprimer.utils.visualization_utils import fix_arr_shape, fix_arr_type
from .point_palette import PointPalette

try:
    import torch
    has_torch = True
    import_exception = ''
except (ImportError, ModuleNotFoundError):
    has_torch = False
    import traceback
    stack_str = ''
    for line in traceback.format_stack():
        if 'frozen' not in line:
            stack_str += line + '\n'
    import_exception = traceback.format_exc() + '\n'
    import_exception = stack_str + import_exception

# yapf: enable


class LinePalette(PointPalette):
    """A class for line visualization.

    Location, connection, color and visibility are kept by LinePalette.
    """

    def __init__(self,
                 conn_array: Union[list, np.ndarray, 'torch.Tensor'],
                 point_array: Union[list, np.ndarray, 'torch.Tensor'],
                 name: str = 'default_line_palette',
                 conn_mask: Union[list, np.ndarray, 'torch.Tensor',
                                  None] = None,
                 color_array: Union[list, np.ndarray, 'torch.Tensor',
                                    None] = None,
                 logger: Union[None, str, logging.Logger] = None) -> None:
        """
        Args:
            conn_array (Union[list, np.ndarray, torch.Tensor]):
                An array of point locations, in shape[n_lines, 2].
            point_array (Union[list, np.ndarray, torch.Tensor]):
                An array of point locations, in shape
                [n_points, location_dim].
            name (str, optional):
                Name of this line palette.
                Defaults to 'default_line_palette'.
            conn_mask (Union[list, np.ndarray, torch.Tensor, None], optional):
                An array of points' visibility mask, in shape[1]
                or [n_conn, 1].
                Defaults to None, all visible.
            color_array (Union[
                    list, np.ndarray,
                    torch.Tensor, None], optional):
                An uint8 array of lines' color, 0 <= value <= 255,
                in shape[3]
                or [n_lines, 3].
                Defaults to None, all red.
            logger (Union[None, str, logging.Logger], optional):
                Logger for logging. If None, root logger will be selected.
                Defaults to None.
        """
        self.logger = get_logger(logger)
        if not has_torch:
            self.logger.error(import_exception)
            raise ImportError
        self.name = name
        self.conn_array = None
        self.conn_mask = None
        self.point_array = None
        self.color_array = None

        self.set_conn_array(conn_array)
        self.set_point_array(point_array)

        conn_mask = conn_mask if conn_mask is not None \
            else np.ones_like(self.conn_array[:, 0:1])
        self.set_conn_mask(conn_mask)

        color_array = color_array if color_array is not None \
            else [255, 0, 0]
        self.set_color_array(color_array)

    def __len__(self) -> int:
        return 0 if self.conn_array is None \
            else len(self.conn_array)

    def set_conn_array(self, conn_array: Union[list, np.ndarray,
                                               'torch.Tensor']):
        """Set conn_array. Type and length will be aligned automatically.

        Args:
            conn_array (Union[list, np.ndarray, torch.Tensor]):
                An array of connection relationship between points,
                in shape [n_line, 2].
        """
        conn_array = fix_arr_type(conn_array)
        target_len = None if self.conn_array is None \
            else len(self.conn_array)
        conn_array = fix_arr_shape(
            array=conn_array,
            array_name=f'{self.name}\'s conn_array',
            target_len=target_len,
            logger=self.logger)
        self.conn_array = conn_array

    def set_conn_mask(self, conn_mask: Union[list, np.ndarray,
                                             'torch.Tensor']):
        """Set lines' visibility mask. Type and length will be aligned
        automatically.

        Args:
            conn_mask (Union[list, np.ndarray, torch.Tensor]):
                An array of lines' visibility mask, in shape[1] or [n_line, 1].
        """
        conn_mask = fix_arr_type(conn_mask)
        target_len = None if self.conn_array is None \
            else len(self.conn_array)
        if len(conn_mask.shape) == 1:
            conn_mask = np.expand_dims(conn_mask, axis=-1)
        conn_mask = fix_arr_shape(
            array=conn_mask,
            array_name=f'{self.name}\'s conn_mask',
            target_len=target_len,
            logger=self.logger)
        self.conn_mask = conn_mask.squeeze(axis=-1).astype(np.uint8)

    def set_point_mask(self, point_mask: Any):
        """Set points' visibility mask. Points' mask is useless in LinePalette.

        Args:
            point_mask (Any)

        Raises:
            NotImplementedError:
                This function is not implemented.
        """
        raise NotImplementedError

    def set_color_array(self, color_array: Union[list, np.ndarray,
                                                 torch.Tensor]):
        """Set lines' color in RGB, [0, 255]. Type and length will be aligned
        automatically.

        Args:
            color_array (Union[list, np.ndarray, torch.Tensor]):
                An array of points' color, in shape[3]
                or [n_line, 3].
        """
        color_array = fix_arr_type(color_array)
        target_len = None if self.conn_array is None \
            else len(self.conn_array)
        color_array = fix_arr_shape(
            array=color_array,
            array_name=f'{self.name}\'s color_array',
            target_len=target_len,
            logger=self.logger)
        self.color_array = color_array.astype(np.uint8)

    @classmethod
    def concatenate(
            cls,
            line_palette_list: List['LinePalette'],
            logger: Union[None, str, logging.Logger] = None) -> 'LinePalette':
        """Concatenate several line_palettes into one.

        Args:
            line_palette_list (List['LinePalette']):
                A list of line_palettes.
        logger (Union[None, str, logging.Logger], optional):
            Logger for logging. If None, root logger will be selected.
            Defaults to None.

        Raises:
            ValueError: line_palette_list is empty.

        Returns:
            LinePalette: Concatenated line_palette.
        """
        if len(line_palette_list) == 0:
            logger = get_logger(logger)
            logger.error('Cannot concatenate an empty list.')
            raise ValueError
        elif len(line_palette_list) == 1:
            logger = line_palette_list[0].logger
            logger.warning('Only one line palette to concatenate.')
        # init attributes to concatenate
        attr_names = ['conn_array', 'point_array', 'color_array']
        concat_dict = dict()
        for attr_name in attr_names:
            concat_dict[attr_name] = []
        # record attributes
        point_base_idx = 0
        for line_palette in line_palette_list:
            for attr_name in attr_names:
                array = getattr(line_palette, attr_name)
                # connection index starts from point_base_idx
                if attr_name == 'conn_array':
                    array = array.copy() + point_base_idx
                concat_dict[attr_name].append(array)
            point_base_idx = point_base_idx + len(line_palette.point_array)
        # concatenate np array
        kwargs = dict(
            name='concatenated_line_palette',
            logger=line_palette_list[0].logger)
        for attr_name in attr_names:
            kwargs[attr_name] = np.concatenate(concat_dict[attr_name], axis=0)
        ret_line_palette = cls(**kwargs)
        return ret_line_palette
