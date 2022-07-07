import logging
from typing import List, Union

import cv2
import numpy as np

from xrprimer.data_structure.camera import (
    FisheyeCameraParameter,
    PinholeCameraParameter,
)
from xrprimer.transform.camera.distortion import undistort_points
from ..projection.opencv_projector import OpencvProjector
from .base_triangulator import BaseTriangulator

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


class OpencvTriangulator(BaseTriangulator):
    CAMERA_CONVENTION = 'opencv'
    CAMERA_WORLD2CAM = True

    def __init__(self,
                 camera_parameters: List[FisheyeCameraParameter],
                 multiview_reduction: Literal['mean', 'median'] = 'mean',
                 logger: Union[None, str, logging.Logger] = None) -> None:
        """Triangulator for points triangulation, powered by OpenCV.

        Args:
            camera_parameters (List[FisheyeCameraParameter]):
                A list of FisheyeCameraParameter, or a list
                of PinholeCameraParameter.
            multiview_reduction (Literal['mean', 'median']):
                When more than 2 views are provided, how to
                reduce among view pairs.
                Defaults to mean.
            logger (Union[None, str, logging.Logger], optional):
                Logger for logging. If None, root logger will be selected.
                Defaults to None.

        Raises:
            TypeError:
                Some element of camera_parameters is neither
                PinholeCameraParameter nor str.
            NotImplementedError:
                Some camera_parameter from camera_parameters
                has a different camera convention from expectation.
        """
        super().__init__(camera_parameters=camera_parameters, logger=logger)
        self.multiview_reduction = multiview_reduction

    def set_cameras(self,
                    camera_parameters: List[FisheyeCameraParameter]) -> None:
        """Set cameras for this triangulator.

        Args:
            camera_parameters (List[FisheyeCameraParameter]):
                A list of FisheyeCameraParameter, or a list
                of paths to dumped FisheyeCameraParameter.
        """
        super().set_cameras(camera_parameters=camera_parameters)

    def triangulate(
            self,
            points: Union[np.ndarray, list, tuple],
            points_mask: Union[np.ndarray, list, tuple] = None) -> np.ndarray:
        """Triangulate points with self.camera_parameters.

        Args:
            points (Union[np.ndarray, list, tuple]):
                An ndarray or a nested list of points2d, in shape
                [n_view, n_point 2].
            points_mask (Union[np.ndarray, list, tuple], optional):
                An ndarray or a nested list of mask, in shape
                [n_view, n_point 1].
                If points_mask[index] == 1, points[index] is valid
                for triangulation, else it is ignored.
                If points_mask[index] == np.nan, the whole pair will
                be ignored and not counted by any method.
                Defaults to None.

        Returns:
            np.ndarray:
                An ndarray of points3d, in shape
                [n_point, 3].
        """
        assert len(points) == len(self.camera_parameters)
        points = np.array(points)
        undistorted_cam_list = []
        for view_idx, view_cam in enumerate(self.camera_parameters):
            if isinstance(view_cam, FisheyeCameraParameter):
                undistorted_cam, points[view_idx, ...] = undistort_points(
                    distorted_cam=view_cam, points=points[view_idx, ...])
                undistorted_cam_list.append(undistorted_cam)
            else:
                undistorted_cam_list.append(view_cam)
        triangulation_mat = self.__class__.prepare_triangulation_mat(
            undistorted_cam_list)
        if points_mask is not None:
            points_mask = np.array(points_mask)
        else:
            points_mask = np.ones_like(points[:, :, :1])
        n_view = len(self.camera_parameters)
        n_point = points.shape[1]
        n_pair = int(n_view * (n_view - 1) / 2)
        triangulation_results = np.zeros(shape=(n_pair, n_point, 3))
        triangulation_result_mask = np.zeros(shape=(n_pair, n_point, 1))
        pair_count = 0
        for view_index_0 in range(n_view):
            for view_index_1 in range(view_index_0 + 1, n_view, 1):
                # if mask of one point is 0 or nan,
                # the pair fails(masked by nan)
                pair_mask = points_mask[view_index_0, ...] * \
                    points_mask[view_index_1, ...]
                pair_mask[pair_mask == 0] = np.nan
                point4d_hom = cv2.triangulatePoints(
                    projMatr1=triangulation_mat[view_index_0],
                    projMatr2=triangulation_mat[view_index_1],
                    projPoints1=points[view_index_0, :, :2].transpose(1, 0),
                    projPoints2=points[view_index_1, :, :2].transpose(1, 0))
                # if 0, invalid, else divide it
                dividend = point4d_hom[3, :]
                pair_mask[dividend == 0, :] = np.nan
                # avoid zero-division
                dividend[dividend == 0] = 1
                point3d = point4d_hom[:3] / dividend
                triangulation_results[pair_count, :, :] = point3d.transpose(
                    1, 0)
                triangulation_result_mask[pair_count, :, :] = pair_mask
                pair_count += 1
        triangulation_result_mask = np.repeat(
            triangulation_result_mask, 3, axis=2)
        triangulation_results = triangulation_results * \
            triangulation_result_mask
        # get mean location among pairs ignoring nan
        if self.multiview_reduction == 'mean':
            points3d = np.nanmean(
                triangulation_results, axis=0, keepdims=False)
        elif self.multiview_reduction == 'median':
            points3d = np.nanmedian(
                triangulation_results, axis=0, keepdims=False)
        else:
            self.logger.error(
                f'Wrong reduction_method: {self.multiview_reduction}')
            raise ValueError
        points3d[np.isnan(points3d)] = 0.0
        return points3d

    def triangulate_single_point(
            self,
            points: Union[np.ndarray, list, tuple],
            points_mask: Union[np.ndarray, list, tuple] = None) -> np.ndarray:
        """Triangulate a single point with self.camera_parameters.

        Args:
            points (Union[np.ndarray, list, tuple]):
                An ndarray or a nested list of points2d, in shape
                [n_view, 2].
            points_mask (Union[np.ndarray, list, tuple], optional):
                An ndarray or a nested list of mask, in shape
                [n_view, 1].
                If points_mask[index] == 1, points[index] is valid
                for triangulation, else it is ignored.
                Defaults to None.

        Returns:
            np.ndarray:
                An ndarray of points3d, in shape
                [3, ].
        """
        assert len(points) == len(self.camera_parameters)
        points = np.array(points)
        undistorted_cam_list = []
        for view_idx, view_cam in enumerate(self.camera_parameters):
            if isinstance(view_cam, FisheyeCameraParameter):
                undistorted_cam, points[view_idx, ...] = undistort_points(
                    distorted_cam=view_cam, points=points[view_idx, ...])
                undistorted_cam_list.append(undistorted_cam)
            else:
                undistorted_cam_list.append(view_cam)
        triangulation_mat = self.__class__.prepare_triangulation_mat(
            undistorted_cam_list)
        if points_mask is not None:
            points_mask = np.array(points_mask)
        else:
            points_mask = np.ones_like(points[:, :1])
        n_view = len(self.camera_parameters)
        triangulation_results = []
        for view_index_0 in range(n_view):
            if points_mask[view_index_0, 0] != 1:
                continue
            for view_index_1 in range(view_index_0 + 1, n_view, 1):
                if points_mask[view_index_1, 0] != 1:
                    continue
                point4d_hom = cv2.triangulatePoints(
                    projMatr1=triangulation_mat[view_index_0],
                    projMatr2=triangulation_mat[view_index_1],
                    projPoints1=points[view_index_0],
                    projPoints2=points[view_index_1])
                # if 0, invalid, else divide it
                dividend = point4d_hom[3, :]
                if dividend == 0:
                    continue
                point3d = point4d_hom[:3] / dividend
                triangulation_results.append(np.squeeze(point3d, axis=1))
        point3d = np.zeros(shape=[
            3,
        ])
        if len(triangulation_results) > 0:
            if self.multiview_reduction == 'mean':
                point3d = np.mean(
                    np.array(triangulation_results), axis=0, keepdims=False)
            elif self.multiview_reduction == 'median':
                point3d = np.median(
                    np.array(triangulation_results), axis=0, keepdims=False)
            else:
                self.logger.error(
                    f'Wrong reduction_method: {self.multiview_reduction}')
                raise ValueError
        return point3d

    def get_reprojection_error(
            self,
            points2d: Union[np.ndarray, list, tuple],
            points3d: Union[np.ndarray, list, tuple],
            points_mask: Union[np.ndarray, list, tuple] = None) -> np.ndarray:
        """Get reprojection error between reprojected points2d and input
        points2d.

        Args:
            points2d (Union[np.ndarray, list, tuple]):
                An ndarray or a nested list of points2d, in shape
                [n_view, n_point, 2].
            points3d (Union[np.ndarray, list, tuple]):
                An ndarray or a nested list of points3d, in shape
                [n_point, 3].
            points_mask (Union[np.ndarray, list, tuple], optional):
                An ndarray or a nested list of mask, in shape
                [n_view, n_point, 1].
                If points_mask[index] == 1, points[index] is valid
                for triangulation, else it is ignored.
                If points_mask[index] == np.nan, the whole pair will
                be ignored and not counted by any method.
                Defaults to None.

        Returns:
            np.ndarray:
                An ndarray in shape [n_view, n_point, 2],
                record offset alone x, y axis of each point2d.
        """
        projector = self.get_projector()
        points3d = np.array(points3d).reshape(-1, 3)
        points2d_shape_backup = points2d.shape
        n_view = points2d_shape_backup[0]
        points2d = np.array(points2d).reshape(n_view, -1, 2)
        if points_mask is None:
            points_mask = np.ones_like(points2d[..., :1])
        points_mask = np.array(points_mask).reshape(n_view, -1, 1)
        projected_points = projector.project(points3d)
        projected_error = projected_points - points2d
        points_mask = np.repeat(points_mask, 2, axis=2)
        projected_error = projected_error * points_mask
        return projected_error

    def get_projector(self) -> OpencvProjector:
        projector = OpencvProjector(camera_parameters=self.camera_parameters)
        return projector

    def __getitem__(self, index: Union[slice, int, list, tuple]):
        """Slice the triangulator by batch dim.

        Args:
            index (Union[slice, int, list, tuple]):
                The index for slicing.

        Returns:
            Triangulator:
                A sliced Triangulator of origin class,
                with selected cameras.
        """
        new_cam_param_list = self.__get_camera_parameters_slice__(index)
        new_triangulator = self.__class__(
            camera_parameters=new_cam_param_list,
            multiview_reduction=self.multiview_reduction)
        return new_triangulator

    @classmethod
    def prepare_triangulation_mat(
            cls,
            camera_parameters: List[PinholeCameraParameter]) -> np.ndarray:
        """Prepare projection matrix for triangulation. According to opencv,

        ProjectionMatrix = [intrinsic33] * [extrinsic_r|extrinsic_t]

        Args:
            camera_parameters (List[PinholeCameraParameter]):
                A list of pinhole camera parameters.

        Returns:
            np.ndarray:
                The projection matrix in shape
                [n_camera, 3, 4].
        """
        triangulation_mat = np.zeros(shape=(len(camera_parameters), 3, 4))
        for camera_index in range(len(camera_parameters)):
            triangulation_mat[camera_index, :, :3] = np.array(
                camera_parameters[camera_index].get_extrinsic_r()).reshape(
                    3, 3)
            triangulation_mat[camera_index, :, 3:] = np.array(
                camera_parameters[camera_index].get_extrinsic_t()).reshape(
                    3, 1)
            triangulation_mat[camera_index] = np.matmul(
                np.array(
                    camera_parameters[camera_index].get_intrinsic(k_dim=3)),
                triangulation_mat[camera_index])
        return triangulation_mat
