# yapf: disable
import os
import shutil

import numpy as np
import pytest

from xrprimer.data_structure.camera import (
    FisheyeCameraParameter,
    PinholeCameraParameter,
)
from xrprimer.data_structure.keypoints import Keypoints
from xrprimer.visualization.keypoints.visualize_keypoints3d import (
    visualize_keypoints3d_cv2,
    visualize_keypoints3d_mpl,
)

# yapf: enable

input_dir = 'tests/data/visualization/' + \
    'keypoints/test_visualize_keypoints3d'
output_dir = 'tests/data/output/visualization' + \
    '/keypoints/test_visualize_keypoints3d'
# lower dpi to speed up tests
_DPI = 50


@pytest.fixture(scope='module', autouse=True)
def fixture():
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=False)
    keypoints3d_path = os.path.join(input_dir, 'keypoints_3d.npz')
    keypoints3d_1f_1p = Keypoints.fromfile(keypoints3d_path)
    # repeat sperson keypoints for 90 frames
    keypoints3d_90f_1p = keypoints3d_1f_1p.clone()
    kps3d_90f_1p = keypoints3d_1f_1p.get_keypoints().repeat(90, axis=0)
    mask_90f_1p = keypoints3d_1f_1p.get_mask().repeat(90, axis=0)
    keypoints3d_90f_1p.set_keypoints(kps3d_90f_1p)
    keypoints3d_90f_1p.set_mask(mask_90f_1p)
    keypoints3d_90f_1p.dump(
        os.path.join(output_dir, 'keypoints_3d_90f_1p.npz'))
    # translate 2 person keypoints for 90 frames
    keypoints3d_90f_2p = keypoints3d_90f_1p.clone()
    kps3d_90f_1st = keypoints3d_90f_1p.get_keypoints().copy()
    kps3d_90f_2nd = keypoints3d_90f_1p.get_keypoints().copy()
    kps3d_90f_2nd[..., 0] += 2
    kps3d_90f_2p = np.concatenate([kps3d_90f_1st, kps3d_90f_2nd], axis=1)
    mask_90f_2p = np.repeat(keypoints3d_90f_1p.get_mask(), 2, axis=1)
    keypoints3d_90f_2p.set_keypoints(kps3d_90f_2p)
    keypoints3d_90f_2p.set_mask(mask_90f_2p)
    keypoints3d_90f_2p.dump(
        os.path.join(output_dir, 'keypoints_3d_90f_2p.npz'))


def test_visualize_keypoints3d_cv2():
    keypoints3d_path = os.path.join(input_dir, 'Shelf_unittest',
                                    'xrmocap_meta_perception2d', 'scene_0',
                                    'keypoints3d_GT.npz')
    keypoints3d = Keypoints.fromfile(keypoints3d_path)
    fisheye_param_path = os.path.join(input_dir, 'Shelf_unittest',
                                      'xrmocap_meta_perception2d', 'scene_0',
                                      'camera_parameters',
                                      'fisheye_param_00.json')
    fisheye_param = FisheyeCameraParameter.fromfile(fisheye_param_path)
    background_dir = os.path.join(input_dir, 'Shelf_unittest', 'Camera0')
    # test plot from a fish eye camera
    output_path = os.path.join(output_dir, 'test_cv2_fisheye.mp4')
    visualize_keypoints3d_cv2(
        keypoints=keypoints3d,
        camera=fisheye_param,
        output_path=output_path,
        plot_points=True,
        plot_lines=True,
        background_dir=background_dir)
    # test plot from a fish eye camera
    pinhole_param = PinholeCameraParameter(
        K=fisheye_param.get_intrinsic(),
        R=fisheye_param.get_extrinsic_r(),
        T=fisheye_param.get_extrinsic_t(),
        height=fisheye_param.height,
        width=fisheye_param.width,
        world2cam=fisheye_param.world2cam,
        convention=fisheye_param.convention,
    )
    output_path = os.path.join(output_dir, 'test_cv2_pinhole.mp4')
    visualize_keypoints3d_cv2(
        keypoints=keypoints3d,
        camera=pinhole_param,
        output_path=output_path,
        plot_points=True,
        plot_lines=True,
        background_dir=background_dir)
    # Plot neither points nor lines
    with pytest.raises(ValueError):
        visualize_keypoints3d_cv2(
            keypoints=keypoints3d,
            camera=pinhole_param,
            output_path=output_path,
            plot_points=False,
            plot_lines=False,
            background_dir=background_dir)


def test_visualize_keypoints3d_mpl_sperson():
    keypoints3d_path = os.path.join(output_dir, 'keypoints_3d_90f_1p.npz')
    keypoints3d = Keypoints.fromfile(keypoints3d_path)
    # test plot only points
    output_path = os.path.join(output_dir, 'test_mpl_plot_points_sperson.mp4')
    visualize_keypoints3d_mpl(
        keypoints=keypoints3d,
        output_path=output_path,
        plot_points=True,
        plot_lines=False,
        dpi=_DPI)
    # test plot only lines
    output_path = os.path.join(output_dir, 'test_mpl_plot_lines_sperson.mp4')
    visualize_keypoints3d_mpl(
        keypoints=keypoints3d,
        output_path=output_path,
        plot_points=False,
        plot_lines=True,
        dpi=_DPI)
    # test plot both points and lines
    output_path = os.path.join(output_dir, 'test_mpl_plot_both_sperson.mp4')
    visualize_keypoints3d_mpl(
        keypoints=keypoints3d,
        output_path=output_path,
        plot_points=True,
        plot_lines=True,
        dpi=_DPI)


def test_visualize_keypoints3d_mpl_mperson():
    keypoints3d_path = os.path.join(output_dir, 'keypoints_3d_90f_2p.npz')
    keypoints3d = Keypoints.fromfile(keypoints3d_path)
    # test plot only points
    output_path = os.path.join(output_dir, 'test_mpl_plot_points_mperson.mp4')
    visualize_keypoints3d_mpl(
        keypoints=keypoints3d,
        output_path=output_path,
        plot_points=True,
        plot_lines=False,
        dpi=_DPI)
    # test plot only lines
    output_path = os.path.join(output_dir, 'test_mpl_plot_lines_mperson.mp4')
    visualize_keypoints3d_mpl(
        keypoints=keypoints3d,
        output_path=output_path,
        plot_points=False,
        plot_lines=True,
        dpi=_DPI)
    # test plot both points and lines
    output_path = os.path.join(output_dir, 'test_mpl_plot_both_mperson.mp4')
    visualize_keypoints3d_mpl(
        keypoints=keypoints3d,
        output_path=output_path,
        plot_points=True,
        plot_lines=True,
        dpi=_DPI)


def test_visualize_keypoints3d_mpl_mperson_mask():
    keypoints3d_path = os.path.join(output_dir, 'keypoints_3d_90f_2p.npz')
    keypoints3d = Keypoints.fromfile(keypoints3d_path)
    keypoints3d['mask'][20:30, 0:1, 0:10, ...] = 0
    output_path = os.path.join(output_dir, 'test_mpl_plot_point_mask.mp4')
    visualize_keypoints3d_mpl(
        keypoints=keypoints3d,
        output_path=output_path,
        plot_points=True,
        plot_lines=True,
        dpi=_DPI)
    keypoints3d['mask'][20:30, 0:2, ...] = 0
    output_path = os.path.join(output_dir, 'test_mpl_plot_person_mask.mp4')
    visualize_keypoints3d_mpl(
        keypoints=keypoints3d,
        output_path=output_path,
        plot_points=True,
        plot_lines=True,
        dpi=_DPI)
