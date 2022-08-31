# Triangulator

- [Prepare camera parameters](#prepare-camera-parameters)
- [Build a triangulator](#build-a-triangulator)
- [Triangulate points from 2D to 3D](#triangulate-points-from-2d-to-3d)
- [Get reprojection error](#get-reprojection-error)
- [Camera selection](#camera-selection)

## Prepare camera parameters

A triangulator requires a list of camera parameters to triangulate points. Each camera parameter should be an instance of `PinholeCameraParameter` or it's sub-class. There are several ways to create the camera parameter list.

a. Assign camera  parameters manually.

```python
from xrprimer.data_structure.camera import PinholeCameraParameter

cam_param_list = []
for kinect_index in range(n_view):
    cam_param = PinholeCameraParameter(
    	name=f'cam_{kinect_index:02d}',
    	world2cam=True)
    cam_param.set_KRT(
    	K=intrinsics[kinect_index],
    	R=rotations[kinect_index],
    	T=translations[kinect_index])
    cam_param_list.append(cam_param)
```

b. Load dumped camera parameter files.

```python
from xrprimer.data_structure.camera import PinholeCameraParameter

cam_param_list = []
for kinect_index in range(n_view):
    cam_param_path = os.path.join(input_dir,
                                  f'cam_{kinect_index:02d}.json')
    cam_param = PinholeCameraParameter()
    cam_param.load(cam_param_path)
    cam_param_list.append(cam_param)
```

Note that `convention` and `world2cam` shall be set correctly. It is essential for the triangulator to know how to deal with input parameters.

## Build a triangulator

In XRprimer, we use registry and builder to build a certain triangulator among multiple alternative classes.

```python
import mmcv

from xrprimer.ops.triangulation.builder import build_triangulator

triangulator_config = dict(
        mmcv.Config.fromfile(
            'config/ops/triangulation/opencv_triangulator.py'))
triangulator_config['camera_parameters'] = cam_param_list
triangulator = build_triangulator(triangulator_config)
```

## Set cameras of a triangulator

Camera parameters can also be set after building.

```python
triangulator.set_cameras(cam_param_list)
```

## Triangulate points from 2D to 3D

If there's only one point in 3D space, we could use `triangulate_single_point()`.

```python
# points2d in shape [n_view, 2], in type numpy.ndarray, or nested list/tuple
point3d = triangulator.triangulate_single_point(points2d)
# points3d in shape [3, ], in type numpy.ndarray
```

For more than one point, `triangulate()` is recommended.

```python
# points2d in shape [n_view, n_point, 2], in type numpy.ndarray, or nested list/tuple
point3d = triangulator.triangulate(points2d)
# points3d in shape [n_point, 3], in type numpy.ndarray
```

In multi-view scenario, not every view is helpful. To filter the good sources in 2D space, `points_mask` is introduced.

```python
# points_mask in shape [n_view, n_point 1]
# 			point0			point1		point2
# view0		0				nan			1
# view1		1				nan			1
# view2		1				nan			1
# result	combine 1,2		nan			combine 0,1,2
point3d = triangulator.triangulate_single_point(points2d, points_mask)
```

## Get reprojection error

To evaluate the triangulation quality, we also provide a point-wise reprojection error, between input points2d and reprojected points2d. `points_mask` is also functional here.

```python
point3d = triangulator.triangulate(points2d, points_mask)
error2d = triangulator.get_reprojection_error(points2d, points3d, points_mask)
# error2d has the same shape as points2d
```

## Camera selection

To select a sub-set of all the cameras, we provide a selection method.

```python
# select two cameras by index list
sub_triangulator = triangulator[[0, 1]]
# a tuple argument is same as list
sub_triangulator = triangulator[(0, 1)]
# select the first 3 cameras by slice
sub_triangulator = triangulator[:3]
# select cameras whose index is divisible by 2
sub_triangulator = triangulator[::2]
```

## Get a conjugated projector

The returned multi-view projector will have the same cameras as triangulator.

```python
projector = triangulator.get_projector()
```
