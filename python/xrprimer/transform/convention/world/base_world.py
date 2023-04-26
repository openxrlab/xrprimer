import numpy as np


class BaseWorld:
    """A world class for world coordinate convention.

    By using the rotation rotation matrix of this world(left multiplication),
    3D data can be transformed from base world space to the current space.
    """
    ROTATION = np.eye(3)
