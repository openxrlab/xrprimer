import numpy as np

from xrprimer_cpp import VectorDouble
from xrprimer_cpp.ops import prior_guided_pnp


def pose_estimation():
    m, n = 5, 100
    correspondences = np.random.random([m, n]).astype('float32')
    point2ds = correspondences[0:2, :].copy()
    point3ds = correspondences[2:5, :].copy()
    priors = np.ones([1, n], dtype='float32')
    params = VectorDouble([1465., 1465., 955., 689.])
    camera_config = {'model_name': 'PINHOLE', 'params': params}
    ransac_config = {
        'error_thres': 12,
        'inlier_ratio': 0.01,
        'confidence': 0.9999,
        'max_iter': 100000,
        'local_optimal': True
    }
    return prior_guided_pnp(point2ds, point3ds, priors, camera_config,
                            ransac_config)


if __name__ == '__main__':
    print(pose_estimation())
