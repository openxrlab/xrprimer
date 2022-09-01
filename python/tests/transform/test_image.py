import numpy as np

from xrprimer.transform.image.color import bgr2rgb


def test_bgr2rgb():
    # test numpy
    # one img
    rgb_image = np.zeros(shape=(3, 640, 480))
    rgb_image[2, ...] = 2
    assert rgb_image[2, 0, 0] == 2
    bgr_image = bgr2rgb(rgb_image, color_dim=0)
    assert bgr_image[0, 0, 0] == 2
    assert bgr_image[2, 0, 0] == 0
    # pytorch batch like
    rgb_image = np.zeros(shape=(2, 3, 640, 480))
    rgb_image[:, 2, ...] = 2
    assert rgb_image[0, 2, 0, 0] == 2
    bgr_image = bgr2rgb(rgb_image, color_dim=1)
    assert bgr_image[0, 0, 0, 0] == 2
    assert bgr_image[0, 2, 0, 0] == 0
    # opencv video like
    rgb_image = np.zeros(shape=(2, 640, 480, 3))
    rgb_image[..., 2] = 2
    assert rgb_image[0, 0, 0, 2] == 2
    bgr_image = bgr2rgb(rgb_image, color_dim=-1)
    assert bgr_image[0, 0, 0, 0] == 2
    assert bgr_image[0, 0, 0, 2] == 0
