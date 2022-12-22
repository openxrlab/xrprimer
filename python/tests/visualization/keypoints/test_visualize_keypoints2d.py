# yapf: disable
import os
import shutil

import pytest

from xrprimer.data_structure.keypoints import Keypoints
from xrprimer.visualization.keypoints.visualize_keypoints2d import (
    visualize_keypoints2d,
)

# yapf: enable

input_dir = 'tests/data/visualization/' + \
    'keypoints/test_visualize_keypoints2d'
output_dir = 'tests/data/output/visualization' + \
    '/keypoints/test_visualize_keypoints2d'


@pytest.fixture(scope='module', autouse=True)
def fixture():
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=False)


def test_visualize_keypoints2d_mperson():
    keypoints2d_path = os.path.join(input_dir, 'shelf_keypoints2d.npz')
    keypoints2d = Keypoints.fromfile(keypoints2d_path)
    # test plot only points
    output_path = os.path.join(output_dir, 'test_plot_points_mperson.mp4')
    visualize_keypoints2d(
        keypoints=keypoints2d,
        output_path=output_path,
        plot_points=True,
        plot_lines=False,
        width=1920,
        height=1080)
    # test plot only lines
    output_path = os.path.join(output_dir, 'test_plot_lines_mperson.mp4')
    visualize_keypoints2d(
        keypoints=keypoints2d,
        output_path=output_path,
        plot_points=False,
        plot_lines=True,
        width=1920,
        height=1080)
    # test plot both points and lines
    output_path = os.path.join(output_dir, 'test_plot_both_mperson.mp4')
    visualize_keypoints2d(
        keypoints=keypoints2d,
        output_path=output_path,
        plot_points=True,
        plot_lines=True,
        width=1920,
        height=1080)


def test_visualize_keypoints2d_sperson():
    keypoints2d_path = os.path.join(input_dir, 'shelf_keypoints2d.npz')
    keypoints2d = Keypoints.fromfile(keypoints2d_path)
    keypoints2d.set_keypoints(keypoints2d.get_keypoints()[:, 0:1, ...])
    keypoints2d.set_mask(keypoints2d.get_mask()[:, 0:1, ...])
    # test plot only points
    output_path = os.path.join(output_dir, 'test_plot_points_sperson.mp4')
    visualize_keypoints2d(
        keypoints=keypoints2d,
        output_path=output_path,
        plot_points=True,
        plot_lines=False,
        width=1920,
        height=1080)
    # test plot only lines
    output_path = os.path.join(output_dir, 'test_plot_lines_sperson.mp4')
    visualize_keypoints2d(
        keypoints=keypoints2d,
        output_path=output_path,
        plot_points=False,
        plot_lines=True,
        width=1920,
        height=1080)
    # test plot both points and lines
    output_path = os.path.join(output_dir, 'test_plot_both_sperson.mp4')
    visualize_keypoints2d(
        keypoints=keypoints2d,
        output_path=output_path,
        plot_points=True,
        plot_lines=True,
        width=1920,
        height=1080)


def test_visualize_keypoints2d_mask():
    keypoints2d_path = os.path.join(input_dir, 'shelf_keypoints2d.npz')
    keypoints2d = Keypoints.fromfile(keypoints2d_path)
    keypoints2d['mask'][20:30, 0:2, 0:10, ...] = 0
    output_path = os.path.join(output_dir, 'test_plot_point_mask.mp4')
    visualize_keypoints2d(
        keypoints=keypoints2d,
        output_path=output_path,
        plot_points=True,
        plot_lines=True,
        width=1920,
        height=1080)
    keypoints2d['mask'][20:30, 0:2, ...] = 0
    output_path = os.path.join(output_dir, 'test_plot_person_mask.mp4')
    visualize_keypoints2d(
        keypoints=keypoints2d,
        output_path=output_path,
        plot_points=True,
        plot_lines=True,
        width=1920,
        height=1080)
