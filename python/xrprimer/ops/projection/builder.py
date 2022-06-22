from mmcv.utils import Registry

from .base_projector import BaseProjector
from .opencv_projector import OpencvProjector

PROJECTORS = Registry('projector')
PROJECTORS.register_module(name='OpencvProjector', module=OpencvProjector)


def build_projector(cfg) -> BaseProjector:
    """Build projector."""
    return PROJECTORS.build(cfg)
