import numpy as np


def upgrade_k_3x3(k: np.ndarray, is_perspective: bool = True) -> np.ndarray:
    """Convert opencv 3x3 intrinsic matrix to 4x4.

    Args:
        K (np.ndarray): Input 3x3 intrinsic matrix, left mm defined.

            [[fx,   0,   px],
             [0,   fy,   py],
             [0,    0,   1]]

        is_perspective (bool, optional): whether is perspective projection.
            Defaults to True.

    Returns:
        np.ndarray: Output intrinsic matrix.

            for perspective:
                [[fx,   0,    px,   0],
                [0,   fy,    py,   0],
                [0,    0,    0,    1],
                [0,    0,    1,    0]]

            for orthographics:
                [[fx,   0,    0,   px],
                [0,   fy,    0,   py],
                [0,    0,    1,    0],
                [0,    0,    0,    1]]
    """
    k_batch = k.reshape(-1, 3, 3)
    if is_perspective:
        k_ret = np.zeros((k_batch.shape[0], 4, 4), dtype=k_batch.dtype)
        k_ret[:, :2, :3] = k_batch[:, :2, :3]
        k_ret[:, 3, 2] = 1
        k_ret[:, 2, 3] = 1
    else:
        k_ret = np.zeros((k_batch.shape[0], 4, 4), dtype=k_batch.dtype)
        k_ret[:, :2, :2] = k_batch[:, :2, :2]
        k_ret[:, :2, 3:] = k_batch[:, :2, 2:]
        k_ret[:, 2, 2] = 1
        k_ret[:, 3, 3] = 1
    ret_shape = [4, 4]
    for dim_index in range(k.ndim - 3, -1, -1):
        ret_shape.insert(0, k.shape[dim_index])
    return k_ret.reshape(*ret_shape)


def downgrade_k_4x4(k: np.ndarray) -> np.ndarray:
    """Convert opencv 4x4 intrinsic matrix to 3x3.

    Args:
        K (np.ndarray):
            Input 4x4 intrinsic matrix, left mm defined.

    Returns:
        np.ndarray: Output 3x3 intrinsic matrix, left mm defined.

            [[fx,   0,   px],
             [0,   fy,   py],
             [0,    0,   1]]
    """
    k_batch = k.reshape(-1, 4, 4)
    is_perspective = (k_batch[0, 2, 3] == k_batch[0, 3, 2])
    if is_perspective:
        k_ret = np.zeros((k_batch.shape[0], 3, 3), dtype=k_batch.dtype)
        k_ret[:, :2, :3] = k_batch[:, :2, :3]
        k_ret[:, 2, 2] = 1
    else:
        k_ret = np.zeros((k_batch.shape[0], 3, 3), dtype=k_batch.dtype)
        k_ret[:, :2, :2] = k_batch[:, :2, :2]
        k_ret[:, :2, 2:3] = k_batch[:, :2, 3:4]
        k_ret[:, 2, 2] = 1
    ret_shape = [3, 3]
    for dim_index in range(k.ndim - 3, -1, -1):
        ret_shape.insert(0, k.shape[dim_index])
    return k_ret.reshape(*ret_shape)
