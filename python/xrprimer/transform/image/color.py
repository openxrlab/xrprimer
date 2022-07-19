import numpy as np


def bgr2rgb(input_array: np.ndarray, color_dim: int = -1) -> np.ndarray:
    """Convert image array of any shape between BGR and RGB.

    Args:
        input_array (np.ndarray):
            An array of images. The shape could be:
            [h, w, n_ch], [n_frame, h, w, n_ch],
            [n_view, n_frame, h, w, n_ch], etc.
        color_dim (int, optional):
            Which dim is the color channel. Defaults to -1.

    Returns:
        np.ndarray
    """
    r_slice_list = [
        slice(None),
    ] * len(input_array.shape)
    b_slice_list = [
        slice(None),
    ] * len(input_array.shape)
    r_slice_list[color_dim] = slice(0, 1, 1)
    b_slice_list[color_dim] = slice(2, 3, 1)
    b_backup = input_array[tuple(b_slice_list)].copy()
    input_array[tuple(b_slice_list)] = input_array[tuple(r_slice_list)]
    input_array[tuple(r_slice_list)] = b_backup
    return input_array
