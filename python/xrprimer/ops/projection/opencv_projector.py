from typing import List, Union

import cv2
import numpy as np

from xrprimer.data_structure.camera import FisheyeCameraParameter
from .base_projector import BaseProjector


class OpencvProjector(BaseProjector):
    CAMERA_CONVENTION = 'opencv'

    def __init__(self,
                 camera_parameters: List[FisheyeCameraParameter]) -> None:
        """BaseProjector for points projection.

        Args:
            camera_parameters (List[FisheyeCameraParameter]):
                A list of FisheyeCameraParameter.
        """
        BaseProjector.__init__(self, camera_parameters)

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
        distortion_list = self.__prepare_dist_coeff__()
        points3d = np.array(points, dtype=np.float64).reshape(-1, 3)
        n_view = len(self.camera_parameters)
        n_point = points3d.shape[0]
        points2d = np.zeros(shape=[n_view, n_point, 2], dtype=points3d.dtype)
        points_mask = np.array(points_mask).reshape(-1) \
            if points_mask is not None \
            else np.ones(shape=[n_point, ], dtype=np.uint8)
        valid_idxs = np.where(points_mask == 1)
        for camera_index in range(len(self.camera_parameters)):
            cam_param = self.camera_parameters[camera_index]
            r_mat = np.array(cam_param.get_extrinsic_r(), dtype=points3d.dtype)
            t_vec = np.array(cam_param.get_extrinsic_t(), dtype=points3d.dtype)
            k_mat = np.array(cam_param.get_intrinsic(3), dtype=points3d.dtype)
            dist_coeffs = np.array(
                distortion_list[camera_index], dtype=points3d.dtype)
            projected_points, _ = cv2.projectPoints(
                objectPoints=points3d[valid_idxs[0], :],
                rvec=r_mat,
                tvec=t_vec,
                cameraMatrix=k_mat,
                distCoeffs=dist_coeffs)
            projected_points = projected_points.reshape(-1, 2)
            points2d[camera_index, valid_idxs[0], :] = projected_points
        return points2d

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
        points3d = np.array(points).reshape(1, 3)
        return np.squeeze(self.project(points3d), axis=1)

    def __prepare_dist_coeff__(self) -> list:
        """Prepare distortion argument for opencv.

        Returns:
            list: list of distCoeffs, len(list) == n_camera.
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
