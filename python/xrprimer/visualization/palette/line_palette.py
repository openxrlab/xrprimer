# yapf: disable
import logging
from typing import Any, List, Union

import numpy as np
import torch

from xrprimer.utils.log_utils import get_logger
from xrprimer.utils.visualization_utils import fix_arr_shape, fix_arr_type
from .point_palette import PointPalette

# yapf: enable


class LinePalette(PointPalette):

    def __init__(self,
                 conn_array: Union[list, np.ndarray, torch.Tensor],
                 point_array: Union[list, np.ndarray, torch.Tensor],
                 name: str = 'default_line_palette',
                 conn_mask: Union[list, np.ndarray, torch.Tensor, None] = None,
                 color_array: Union[list, np.ndarray, torch.Tensor,
                                    None] = None,
                 logger: Union[None, str, logging.Logger] = None) -> None:
        self.logger = get_logger(logger)
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
        ret_len = 0 if self.conn_array is None \
            else len(self.conn_array)
        return ret_len

    def set_conn_array(self, conn_array: Union[list, np.ndarray,
                                               torch.Tensor]):
        conn_array = fix_arr_type(conn_array)
        target_len = None if self.conn_array is None \
            else len(self.conn_array)
        conn_array = fix_arr_shape(
            array=conn_array,
            array_name=f'{self.name}\'s conn_array',
            target_len=target_len,
            logger=self.logger)
        self.conn_array = conn_array

    def set_conn_mask(self, conn_mask: Union[list, np.ndarray, torch.Tensor]):
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
        raise NotImplementedError

    def set_color_array(self, color_array: Union[list, np.ndarray,
                                                 torch.Tensor]):
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
