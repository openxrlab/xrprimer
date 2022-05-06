from mmcv.utils import Registry

from .opencv_triangulator import OpencvTriangulator

TRIANGULATORS = Registry('triangulator')
TRIANGULATORS.register_module(
    name='OpencvTriangulator', module=OpencvTriangulator)


def build_triangulator(cfg):
    """Build detector."""
    return TRIANGULATORS.build(cfg)
