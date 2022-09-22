import logging
from typing import Union

from xrprimer.data_structure.camera import PinholeCameraParameter
from xrprimer.utils.log_utils import get_logger


class BaseCalibrator():
    """Base class of camera calibrator."""

    def __init__(self,
                 work_dir: str = './temp',
                 logger: Union[None, str, logging.Logger] = None) -> None:
        """Initialization for camera calibrator.

        Args:
            work_dir (str, optional):
                Path to the working dir for this instance.
                Defaults to './temp'.
            logger (Union[None, str, logging.Logger], optional):
                Logger for logging. If None, root logger will be selected.
                Defaults to None.
        """
        self.logger = get_logger(logger)
        self.work_dir = work_dir

    def calibrate(self) -> PinholeCameraParameter:
        """Calibrate a camera or several cameras. Input args shall not be
        modified and the calibrated camera will be returned.

        Returns:
            PinholeCameraParameter:
                The calibrated camera.
        """
        raise NotImplementedError
