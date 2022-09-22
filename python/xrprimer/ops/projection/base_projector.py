# yapf: disable
import logging
from operator import itemgetter
from typing import List, Union

import numpy as np

from xrprimer.data_structure.camera import (
    FisheyeCameraParameter,
    PinholeCameraParameter,
)
from xrprimer.transform.convention.camera import convert_camera_parameter
from xrprimer.utils.log_utils import get_logger

# yapf: enable


# Super class of all projectors, cannot be built
class BaseProjector:
    """BaseProjector for points projection."""

    CAMERA_CONVENTION = 'opencv'
    CAMERA_WORLD2CAM = False

    def __init__(self,
                 camera_parameters: List[Union[PinholeCameraParameter, str]],
                 logger: Union[None, str, logging.Logger] = None) -> None:
        """Initialization for BaseProjector.

        Args:
            camera_parameters (List[Union[PinholeCameraParameter, str]]):
                A list of PinholeCameraParameter, or a list
                of paths to dumped PinholeCameraParameters.
            logger (Union[None, str, logging.Logger], optional):
                Logger for logging. If None, root logger will be selected.
                Defaults to None.
        """
        self.camera_parameters = []
        self.set_cameras(camera_parameters)
        self.logger = get_logger(logger)

    def set_cameras(
        self, camera_parameters: List[Union[PinholeCameraParameter,
                                            FisheyeCameraParameter]]
    ) -> None:
        """Set cameras for this projector.

        Args:
            camera_parameters (List[Union[PinholeCameraParameter, str]]):
                A list of PinholeCameraParameter or FisheyeCameraParameter.
        """
        self.camera_parameters = []
        for input_cam_param in camera_parameters:
            cam_param = input_cam_param.clone()
            if cam_param.world2cam != self.__class__.CAMERA_WORLD2CAM:
                cam_param.inverse_extrinsic()
            if cam_param.convention != self.__class__.CAMERA_CONVENTION:
                cam_param = convert_camera_parameter(
                    cam_param=cam_param, dst=self.__class__.CAMERA_CONVENTION)
            self.camera_parameters.append(cam_param)

    def project(
            self,
            points: Union[np.ndarray, list, tuple],
            points_mask: Union[np.ndarray, list, tuple] = None) -> np.ndarray:
        """Project points with self.camera_parameters.

        Args:
            points (Union[np.ndarray, list, tuple]):
                An ndarray or a nested list of points3d, in shape
                [n_point, 3].
            points_mask (Union[np.ndarray, list, tuple], optional):
                An ndarray or a nested list of mask, in shape
                [n_point, 1].
                If points_mask[index] == 1, points[index] is valid
                for projection, else it is ignored.
                Defaults to None.

        Returns:
            np.ndarray:
                An ndarray of points2d, in shape
                [n_view, n_point, 2].
        """
        raise NotImplementedError

    def project_single_point(
            self, points: Union[np.ndarray, list, tuple]) -> np.ndarray:
        """Project a single point with self.camera_parameters.

        Args:
            points (Union[np.ndarray, list, tuple]):
                An ndarray or a list of points3d, in shape
                [3].

        Returns:
            np.ndarray:
                An ndarray of points2d, in shape
                [n_view, 2].
        """
        raise NotImplementedError

    def __get_camera_parameters_slice__(
            self, index: Union[slice, int, list, tuple]) -> list:
        """Slice self.camera_parameters, return a sub-list.

        Args:
            index (Union[slice, int, list, tuple]):
                The index for slicing.

        Returns:
            list:
                A sliced list of self.camera_parameters,
                with selected cameras.
        """
        if isinstance(index, int):
            index = [index]
        if isinstance(index, list) or isinstance(index, tuple):
            new_cam_param_list = itemgetter(*index)(self.camera_parameters)
            if len(index) == 1:
                new_cam_param_list = [
                    new_cam_param_list,
                ]
        else:
            new_cam_param_list = self.camera_parameters[index]
        new_cam_param_list = list(new_cam_param_list)
        return new_cam_param_list

    def __getitem__(self, index: Union[slice, int, list,
                                       tuple]) -> 'BaseProjector':
        """Slice the projector by batch dim.

        Args:
            index (Union[slice, int, list, tuple]):
                The index for slicing.

        Returns:
            BaseProjector:
                A sliced Projector of origin class,
                with selected cameras.
        """
        new_cam_param_list = self.__get_camera_parameters_slice__(index)
        new_projector = self.__class__(camera_parameters=new_cam_param_list)
        return new_projector
