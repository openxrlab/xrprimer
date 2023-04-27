import numpy as np

from .base_world import BaseWorld


class MatplotlibWorld(BaseWorld):
    """A world class for Matplotlib coordinate convention.

    A human subject in this word faces to z- and his head is up towards y-. By
    using the rotation rotation matrix of this world(left multiplication), 3D
    data can be transformed from base world space to the current space.
    """
    # rotation mat of euler_zxy(0, 270, 0)
    ROTATION = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], dtype=np.float32)
