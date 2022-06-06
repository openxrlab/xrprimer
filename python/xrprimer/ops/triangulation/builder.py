from mmcv.utils import Registry

from .base_triangulator import BaseTriangulator
from .opencv_triangulator import OpencvTriangulator

TRIANGULATORS = Registry('triangulator')
TRIANGULATORS.register_module(
    name='OpencvTriangulator', module=OpencvTriangulator)


def build_triangulator(cfg) -> BaseTriangulator:
    """Build detector."""
    return TRIANGULATORS.build(cfg)
