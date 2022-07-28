from mmcv.utils import Registry

from .base_calibrator import BaseCalibrator
from .mview_fisheye_calibrator import MviewFisheyeCalibrator
from .mview_pinhole_calibrator import MviewPinholeCalibrator
from .sview_fisheye_calibrator import SviewFisheyeDistortionCalibrator

CALIBRATORS = Registry('calibrator')
CALIBRATORS.register_module(
    name='MviewPinholeCalibrator', module=MviewPinholeCalibrator)
CALIBRATORS.register_module(
    name='MviewFisheyeCalibrator', module=MviewFisheyeCalibrator)
CALIBRATORS.register_module(
    name='SviewFisheyeDistortionCalibrator',
    module=SviewFisheyeDistortionCalibrator)


def build_calibrator(cfg) -> BaseCalibrator:
    """Build calibrator."""
    return CALIBRATORS.build(cfg)
