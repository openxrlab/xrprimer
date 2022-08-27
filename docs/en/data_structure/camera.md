# Camera

This file introduces the supported camera and distortion models.

## Pinhole

A pinhole camera is a simple camera without a lens but with a tiny aperture(from [Wikipedia](https://en.wikipedia.org/wiki/Pinhole_camera)).

##### Attributes

Here are attributes of a PinholeCameraParameter below:

| Attribute name | Type     | Description                                                  |
| -------------- | -------- | ------------------------------------------------------------ |
| name           | string   | Name of the camera.                                          |
| intrinsic      | Matrix4f | Intrinsic matrix.                                            |
| extrinsic_r    | Matrix3f | Extrinsic rotation matrix.                                   |
| extrinsic_t    | Vector3f | Extrinsic translation vector.                                |
| height         | int      | Height of screen.                                            |
| width          | int      | Width of screen.                                             |
| world2cam      | bool     | Whether the R, T transform points from world space to camera space. |
| convention     | string   | Convention name of this camera.                              |

For details of convention, please refer to [camera convention doc](../transform/camera_convention.md).

##### File IO

A camera parameter defined in XRPrimer can dump its parameters to a json file or load a dumped json file easily.

```python
# load method 1
pinhole_param = PinholeCameraParameter.fromfile('./pinhole_param.npz')
# load method 2
pinhole_param = PinholeCameraParameter()
pinhole_param.load('./pinhole_param.npz')
# dump method
pinhole_param.dump('./pinhole_param.npz')
```

##### Set intrinsic

There are three ways of setting intrinsic.

a. Set with a 4x4 K matrix.

```python
pinhole_param.set_KRT(K=mat_4x4)
pinhole_param.set_resolution(h, w)
```

b. Set with a 3x3 K matrix.

```python
# method 1, only for perspective camera
pinhole_param.set_KRT(K=mat_3x3)
pinhole_param.set_resolution(h, w)
# method 2
pinhole_param.set_intrinsic(
  mat3x3=mat_3x3,
  width=w, height=h,
	perspective=True)
```

c. Set with focal length and principal point.

```python
pinhole_param.set_intrinsic(
  fx=focal[0], fy=focal[1],
  cx=principal[0], cy=principal[1],
  width=w, height=h,
	perspective=True)
```

##### Set extrinsics

To set extrinsic_r or extrinsic_t, call `set_KRT()`. Remember that `world2cam` argument is important, always check the direction before setting.

```python
# set RT that transform points from camera space to world space
pinhole_param.set_KRT(R=mat_3x3, T=vec_3, world2cam=False)
# set RT but do not modify extrinsic direction stored in pinhole_param
pinhole_param.set_KRT(R=mat_3x3, T=vec_3)
```

##### Inverse extrinsics

Sometimes the extrinsic parameters are not what you desire. Call `inverse_extrinsic()` to inverse the direction, `world2cam` will be inversed synchronously.

```python
assert pinhole_param.world2cam
world2cam_r = pinhole_param.get_extrinsic_r()
pinhole_param.inverse_extrinsic()
cam2world_r = pinhole_param.get_extrinsic_r()
```

##### Clone

In order to get a new camera parameter instance which can be modified arbitrarily, call `clone()`.

```python
another_pinhole_param = pinhole_param.clone()
```

##### Get attributes

```python
# intrinsic
intrinsic33 = pinhole_param.intrinsic33() # an ndarray in shape [3, 3]
intrinsic33 = pinhole_param.get_intrinsic() # a nested list in shape [3, 3]
intrinsic44 = pinhole_param.get_intrinsic(4) # a nested list in shape [4, 4]
# extrinsic
rotation_mat = pinhole_param.get_extrinsic_r() # a nested list in shape [3, 3]
translation_vec = pinhole_param.get_extrinsic_t() # a list whose length is 3
```

## Fisheye

A fisheye lens is an ultra wide-angle lens that produces strong visual distortion intended to create a wide panoramic or hemispherical image(from [Wikipedia](https://en.wikipedia.org/wiki/Fisheye_lens)). In XRPrimer, it's a sub-class of `class PinholeCameraParameter`.

##### Attributes

Here are additional attributes of a FisheyeCameraParameter below:

| Attribute name | Type  | Description |
| -------------- | ----- | ----------- |
| k1             | float |             |
| k2             | float |             |
| k3             | float |             |
| k4             | float |             |
| k5             | float |             |
| k6             | float |             |
| p1             | float |             |
| p2             | float |             |

##### Set distortion coefficients

a. Set all the coefficients.

```python
fisheye_param.set_dist_coeff(dist_coeff_k=[k1, k2, k3, k4, k5, k6], dist_coeff_p=[p1, p2])
```

b. Set all the first four ks, k5 and k6 will keep their value.

```python
fisheye_param.set_dist_coeff(dist_coeff_k=[k1, k2, k3, k4], dist_coeff_p=[p1, p2])
```

##### Get attributes

```python
# distortion coefficients in opencv sequence
dist_coeff_list = fisheye_param.get_dist_coeff() # a list of float, k1, k2, p1, p2, k3, k4, k5, k6
```
