# Projector

- [Prepare camera parameters](#prepare-camera-parameters)
- [Build a triangulator](#build-a-triangulator)
- [Triangulate points from 2D to 3D](#triangulate-points-from-2d-to-3d)
- [Get reprojection error](#get-reprojection-error)
- [Camera selection](#camera-selection)

## Prepare camera parameters

A multi-view projector requires a list of camera parameters, just like the triangulator. Each camera parameter should be an instance of `PinholeCameraParameter` or it's sub-class. For details, please refer to [triangulator doc](./triangulator.md#prepare-camera-parameters) .

## Build a projector

In XRprimer, we use registry and builder to build a certain projector among multiple alternative classes.

```python
import mmcv

from xrprimer.ops.projection.builder import build_projector

projector_config = dict(
        mmcv.Config.fromfile(
            'config/ops/triangulation/opencv_projector.py'))
projector_config['camera_parameters'] = cam_param_list
projector_config = build_projector(projector_config)
```

## Set cameras of a projector

Camera parameters can also be set after building.

```python
projector.set_cameras(cam_param_list)
```

## Project points from 3D to 2D

If there's only one point in 3D space, we could use `project_single_point()`.

```python
# points3d in shape [3, ], in type numpy.ndarray, or list/tuple
mview_point2d = projector.project_single_point(point3d)
# mview_point2d in shape [n_view, 2], in type numpy.ndarray
```

For more than one point, `project()` is recommended.

```python
# points3d in shape [n_point, 3], in type numpy.ndarray, or nested list/tuple
points2d = triangulator.triangulate(points3d)
# points2d in shape [n_view, n_point, 2], in type numpy.ndarray
```

In multi-view scenario, if we set the value at `points_mask[p_idx]` to zero, the point will not be projected.

```python
points2d = triangulator.project(points3d, points_mask)
```

## Camera selection

To select a sub-set of all the cameras, we provide a selection method. For details, please refer to [triangulator doc](./triangulator.md#camera-selection) .
