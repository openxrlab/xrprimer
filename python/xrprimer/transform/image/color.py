from typing import Union

import numpy as np
import torch


def switch_channel(input_array: Union[np.ndarray, torch.Tensor],
                   color_dim: int = -1,
                   inplace: bool = False) -> Union[np.ndarray, torch.Tensor]:
    """Switch the 1st channel and 3rd channel at color_dim.

    Args:
        input_array (Union[np.ndarray, torch.Tensor]):
            An array of images. The shape could be:
            [h, w, n_ch], [n_frame, h, w, n_ch],
            [n_view, n_frame, h, w, n_ch], etc.
            And n_ch shall be 3.
        color_dim (int, optional):
            Which dim is the color channel.
            Defaults to -1, the last dim.
        inplace (bool, optional):
            Whether it is an in-place operation.
            Defaults to False.

    Returns:
        Union[np.ndarray, torch.Tensor]:
            Same type as the input.
    """
    r_slice_list = [
        slice(None),
    ] * len(input_array.shape)
    b_slice_list = [
        slice(None),
    ] * len(input_array.shape)
    r_slice_list[color_dim] = slice(0, 1, 1)
    b_slice_list[color_dim] = slice(2, 3, 1)
    b_idxs = tuple(b_slice_list)
    r_idxs = tuple(r_slice_list)
    if isinstance(input_array, torch.Tensor):
        b_backup = input_array[b_idxs].clone()
        if not inplace:
            ret_array = input_array.clone()
        else:
            ret_array = input_array
    else:
        b_backup = input_array[b_idxs].copy()
        if not inplace:
            ret_array = input_array.copy()
        else:
            ret_array = input_array
    ret_array[b_idxs] = input_array[r_idxs]
    ret_array[r_idxs] = b_backup
    return ret_array


def rgb2bgr(input_array: Union[np.ndarray, torch.Tensor],
            color_dim: int = -1,
            inplace: bool = False) -> Union[np.ndarray, torch.Tensor]:
    """Convert RGB image array of any shape to BGR.

    Args:
        input_array (Union[np.ndarray, torch.Tensor]):
            An array of images. The shape could be:
            [h, w, n_ch], [n_frame, h, w, n_ch],
            [n_view, n_frame, h, w, n_ch], etc.
        color_dim (int, optional):
            Which dim is the color channel. Defaults to -1.
        inplace (bool, optional):
            Whether it is an in-place operation.
            Defaults to False.

    Returns:
        Union[np.ndarray, torch.Tensor]:
            Same type as the input.
    """
    return switch_channel(
        input_array=input_array, color_dim=color_dim, inplace=inplace)


def bgr2rgb(input_array: Union[np.ndarray, torch.Tensor],
            color_dim: int = -1,
            inplace: bool = False) -> Union[np.ndarray, torch.Tensor]:
    """Convert BGR image array of any shape to RGB.

    Args:
        input_array (Union[np.ndarray, torch.Tensor]):
            An array of images. The shape could be:
            [h, w, n_ch], [n_frame, h, w, n_ch],
            [n_view, n_frame, h, w, n_ch], etc.
        color_dim (int, optional):
            Which dim is the color channel. Defaults to -1.
        inplace (bool, optional):
            Whether it is an in-place operation.
            Defaults to False.

    Returns:
        Union[np.ndarray, torch.Tensor]:
            Same type as the input.
    """
    return switch_channel(
        input_array=input_array, color_dim=color_dim, inplace=inplace)
