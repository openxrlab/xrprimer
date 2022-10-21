# yapf: disable
import logging
from typing import List, Union

import numpy as np
import torch

from xrprimer.utils.log_utils import get_logger
from xrprimer.utils.visualization_utils import fix_arr_shape, fix_arr_type

# yapf: enable


class PointPalette:

    def __init__(self,
                 point_array: Union[list, np.ndarray, torch.Tensor],
                 name: str = 'default_point_palette',
                 point_mask: Union[list, np.ndarray, torch.Tensor,
                                   None] = None,
                 color_array: Union[list, np.ndarray, torch.Tensor,
                                    None] = None,
                 logger: Union[None, str, logging.Logger] = None) -> None:
        self.logger = get_logger(logger)
        self.name = name
        self.point_array = None
        self.color_array = None
        self.point_mask = None

        self.set_point_array(point_array)
        point_mask = point_mask if point_mask is not None \
            else np.ones_like(self.point_array[:, 0:1])
        self.set_point_mask(point_mask)

        color_array = color_array if color_array is not None \
            else [255, 0, 0]
        self.set_color_array(color_array)

    def __len__(self) -> int:
        ret_len = 0 if self.point_array is None \
            else len(self.point_array)
        return ret_len

    def set_point_array(self, point_array: Union[list, np.ndarray,
                                                 torch.Tensor]):
        point_array = fix_arr_type(point_array)
        target_len = None if self.point_array is None \
            else len(self.point_array)
        point_array = fix_arr_shape(
            array=point_array,
            array_name=f'{self.name}\'s point_array',
            target_len=target_len,
            logger=self.logger)
        self.point_array = point_array

    def set_point_mask(self, point_mask: Union[list, np.ndarray,
                                               torch.Tensor]):
        point_mask = fix_arr_type(point_mask)
        target_len = None if self.point_array is None \
            else len(self.point_array)
        if len(point_mask.shape) == 1:
            point_mask = np.expand_dims(point_mask, axis=-1)
        point_mask = fix_arr_shape(
            array=point_mask,
            array_name=f'{self.name}\'s point_mask',
            target_len=target_len,
            logger=self.logger)
        self.point_mask = point_mask.squeeze(axis=-1).astype(np.uint8)

    def set_color_array(self, color_array: Union[list, np.ndarray,
                                                 torch.Tensor]):
        color_array = fix_arr_type(color_array)
        target_len = None if self.point_array is None \
            else len(self.point_array)
        color_array = fix_arr_shape(
            array=color_array,
            array_name=f'{self.name}\'s color_array',
            target_len=target_len,
            logger=self.logger)
        self.color_array = color_array.astype(np.uint8)

    @classmethod
    def concatenate(
            cls,
            point_palette_list: List['PointPalette'],
            logger: Union[None, str, logging.Logger] = None) -> 'PointPalette':
        if len(point_palette_list) == 0:
            logger = get_logger(logger)
            logger.error('Cannot concatenate an empty list.')
            raise ValueError
        elif len(point_palette_list) == 1:
            logger = point_palette_list[0].logger
            logger.warning('Only one point palette to concatenate.')
        # init attributes to concatenate
        attr_names = ['point_array', 'color_array']
        concat_dict = dict()
        for attr_name in attr_names:
            concat_dict[attr_name] = []
        # record attributes
        for point_palette in point_palette_list:
            for attr_name in attr_names:
                concat_dict[attr_name].append(
                    getattr(point_palette, attr_name))
        # concatenate np array
        kwargs = dict(
            name='concatenated_point_palette',
            logger=point_palette_list[0].logger)
        for attr_name in attr_names:
            kwargs[attr_name] = np.concatenate(concat_dict[attr_name], axis=0)
        ret_point_palette = cls(**kwargs)
        return ret_point_palette
