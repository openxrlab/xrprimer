from xrprimer.data_structure.camera.fisheye_camera import FisheyeCameraParameter
from xrprimer.transform.camera.distortion import undistort_images
import numpy as np

images = np.ones((10, 1080, 1920, 3), dtype=np.uint8)
fishe_param_0 = FisheyeCameraParameter()

# if Pinhole is returned
images, new_cam_param = undistort_images(
    distorted_cam=fishe_param_0,
    image_array=images)
print(new_cam_param.k1)  # Error, no such attr
new_cam_param.k1 = 1.0  # Error, no such attr
fishe_param_1 = FisheyeCameraParameter(
    K=new_cam_param.get_intrinsic(),
    R=new_cam_param.get_extrinsic_r(),
    T=new_cam_param.get_extrinsic_t(),
    name='cam_1',
    height=new_cam_param.height, width=new_cam_param.width,
    world2cam=new_cam_param.world2cam, convention=new_cam_param.convention
)

# if Fisheye is returned
images, new_cam_param = undistort_images(
    distorted_cam=fishe_param_0,
    image_array=images)
print(new_cam_param.k1)  # stdout: 0.0
new_cam_param.k1 = 1.0  # set k1 to 1.0
fishe_param_1 = new_cam_param.clone()

