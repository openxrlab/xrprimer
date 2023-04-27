from typing import TypeVar

import numpy as np

from .base_world import BaseWorld
from .plt_world import MatplotlibWorld
from .smc_world import SenseMoCapWorld

__all__ = ['BaseWorld', 'MatplotlibWorld', 'SenseMoCapWorld']

WorldClass = TypeVar('WorldClass')


def convert_world(src_world: WorldClass, dst_world: WorldClass) -> np.ndarray:
    """Get a rotation matrix converting vectors from src_world to dst_world.

    Args:
        src_world (WorldClass):
            The source world.
        dst_world (WorldClass):
            The destination world.
    Returns:
        np.ndarray:
            The rotation matrix from src_world to dst_world.
    """
    return dst_world.ROTATION @ src_world.ROTATION.T
