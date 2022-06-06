from typing import Union

import cv2
import numpy as np

from .base_triangulator import BaseTriangulator

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


class OpencvTriangulator(BaseTriangulator):

    def __init__(
            self,
            camera_parameters: list,
            multiview_reduction: Literal['mean', 'median'] = 'mean') -> None:
        """BaseTriangulator for points triangulation.

        Args:
            camera_parameters (list):
                A list of FisheyeCameraParameter, or a list
                of PinholeCameraParameter.
            multiview_reduction (Literal['mean', 'median']):
                When more than 2 views are provided, how to
                reduce among view pairs.
                Defaults to mean.

        Raises:
            TypeError:
                Some element of camera_parameters is neither
                PinholeCameraParameter nor str.
            NotImplementedError:
                Some camera_parameter from camera_parameters
                has a different camera convention from expectation.
        """
        super().__init__(camera_parameters=camera_parameters)
        self.multiview_reduction = multiview_reduction

    def triangulate(
            self,
            points: Union[np.ndarray, list, tuple],
            points_mask: Union[np.ndarray, list, tuple] = None) -> np.ndarray:
        """Triangulate points with self.camera_parameters.

        Args:
            points (Union[np.ndarray, list, tuple]):
                An ndarray or a nested list of points2d, in shape
                [view_number, point_number 2].
            points_mask (Union[np.ndarray, list, tuple], optional):
                An ndarray or a nested list of mask, in shape
                [view_number, point_number 1].
                If points_mask[index] == 1, points[index] is valid
                for triangulation, else it is ignored.
                If points_mask[index] == np.nan, the whole pair will
                be ignored and not counted by any method.
                Defaults to None.

        Returns:
            np.ndarray:
                An ndarray of points3d, in shape
                [point_number, 3].
        """
        assert len(points) == len(self.camera_parameters)
        points = np.array(points)
        # TODO: undistort
        if points_mask is not None:
            points_mask = np.array(points_mask)
        else:
            points_mask = np.ones_like(points[:, :, :1])
        triangulation_mat = self.__prepare_triangulation_mat__()
        view_number = len(self.camera_parameters)
        point_number = points.shape[1]
        pair_number = int(view_number * (view_number - 1) / 2)
        triangulation_results = np.zeros(shape=(pair_number, point_number, 3))
        triangulation_result_mask = np.zeros(
            shape=(pair_number, point_number, 1))
        pair_count = 0
        for view_index_0 in range(view_number):
            for view_index_1 in range(view_index_0 + 1, view_number, 1):
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
            raise ValueError(
                f'Wrong reduction_method: {self.multiview_reduction}')
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
                [view_number, 2].
            points_mask (Union[np.ndarray, list, tuple], optional):
                An ndarray or a nested list of mask, in shape
                [view_number, 1].
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
        if points_mask is not None:
            points_mask = np.array(points_mask)
        else:
            points_mask = np.ones_like(points[:, :1])
        triangulation_mat = self.__prepare_triangulation_mat__()
        view_number = len(self.camera_parameters)
        triangulation_results = []
        for view_index_0 in range(view_number):
            if points_mask[view_index_0, 0] != 1:
                continue
            for view_index_1 in range(view_index_0 + 1, view_number, 1):
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
                raise ValueError(
                    f'Wrong reduction_method: {self.multiview_reduction}')
        return point3d

    def __prepare_triangulation_mat__(self) -> np.ndarray:
        """Prepare projection matrix for triangulation. According to opencv,

        ProjectionMatrix = [intrinsic33] * [extrinsic_r|extrinsic_t]

        Returns:
            np.ndarray:
                The projection matrix in shape
                [cam_num, 3, 4].
        """
        triangulation_mat = np.zeros(shape=(len(self.camera_parameters), 3, 4))
        for camera_index in range(len(self.camera_parameters)):
            triangulation_mat[camera_index, :, :3] = np.array(
                self.camera_parameters[camera_index].get_extrinsic_r(
                )).reshape(3, 3)
            triangulation_mat[camera_index, :, 3:] = np.array(
                self.camera_parameters[camera_index].get_extrinsic_t(
                )).reshape(3, 1)
            triangulation_mat[camera_index] = np.matmul(
                np.array(self.camera_parameters[camera_index].get_intrinsic(
                    k_dim=3)), triangulation_mat[camera_index])
        return triangulation_mat

    def __prepare_distortion__(self) -> list:
        """Prepare distortion argument for opencv.

        Returns:
            list: list of distCoeffs, len(list) == cam_num.
        """
        distortion_list = []
        for cam_param in self.camera_parameters:
            if hasattr(cam_param, 'k1'):
                dist_coeffs = np.array([
                    cam_param.k1, cam_param.k2, cam_param.p1, cam_param.p2,
                    cam_param.k3, cam_param.k4, cam_param.k5, cam_param.k6
                ])
            else:
                dist_coeffs = 0.0
            distortion_list.append(dist_coeffs)
        return distortion_list

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
                [view_number, point_number, 2].
            points3d (Union[np.ndarray, list, tuple]):
                An ndarray or a nested list of points3d, in shape
                [point_number, 3].
            points_mask (Union[np.ndarray, list, tuple], optional):
                An ndarray or a nested list of mask, in shape
                [view_number, point_number, 1].
                If points_mask[index] == 1, points[index] is valid
                for triangulation, else it is ignored.
                If points_mask[index] == np.nan, the whole pair will
                be ignored and not counted by any method.
                Defaults to None.

        Returns:
            np.ndarray:
                An ndarray in shape [view_number, point_number, 2],
                record offset alone x, y axis of each point2d.
        """
        distortion_list = self.__prepare_distortion__()
        points3d = points3d.copy().reshape(-1, 3)
        points2d_shape_backup = points2d.shape
        view_number = points2d_shape_backup[0]
        points2d = points2d.copy().reshape(view_number, -1, 2)
        if points_mask is None:
            points_mask = np.ones_like(points2d[..., :1])
        points_mask = points_mask.copy().reshape(view_number, -1, 1)
        projected_error = np.zeros_like(points2d)
        for camera_index in range(len(self.camera_parameters)):
            cam_param = self.camera_parameters[camera_index]
            r_mat = np.array(cam_param.get_extrinsic_r()).astype(
                points3d.dtype)
            t_vec = np.array(cam_param.get_extrinsic_t()).astype(
                points3d.dtype)
            k_mat = np.array(cam_param.get_intrinsic(3)).astype(points3d.dtype)
            projected_points, _ = cv2.projectPoints(
                objectPoints=points3d,
                rvec=r_mat,
                tvec=t_vec,
                cameraMatrix=k_mat,
                distCoeffs=distortion_list[camera_index])
            projected_points = projected_points.reshape(-1, 2)
            projected_error[camera_index, :, :] = \
                projected_points - points2d[camera_index, :, :]
        points_mask = np.repeat(points_mask, 2, axis=2)
        projected_error = projected_error * points_mask
        return projected_error

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
