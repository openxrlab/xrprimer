# Camera convention

## Intrinsic convention

In OpenCV, shape of the intrinsic matrix is 3x3, while in some other system it's 4x4. In XRPrimer data structures, we store intrinsic in 4x4 manner, but you can get 3x3 intrinsic matrix by argument of get method. Here are the differences between intrinsic33 and intrinsic44.

Intrinsic33, only for perspective camera:

```python
[[fx,   0,   px],
 [0,   fy,   py],
 [0,    0,   1]]
```

Intrinsic44, perspective camera:

```python
[[fx,   0,    px,   0],
 [0,   fy,    py,   0],
 [0,    0,    0,    1],
 [0,    0,    1,    0]]
```

Intrinsic44, orthographic camera:

```python
[[fx,   0,    0,   px],
 [0,   fy,    0,   py],
 [0,    0,    1,    0],
 [0,    0,    0,    1]]
```

We can convert between intrinsic33 and intrinsic44 by `upgrade_k_3x3()`, `downgrade_k_4x4()`:

```python
from xrprimer.transform.convention.camera import downgrade_k_4x4, upgrade_k_3x3

intrinsic44 = upgrade_k_3x3(intrinsic33, is_perspective=True) # intrinsic33 in shape [3, 3] or [batch_size, 3, 3]
intrinsic33 = downgrade_k_4x4(intrinsic44) # intrinsic44 in shape [4, 4] or [batch_size, 4, 4]
```

## Extrinsic convention

In OpenCV camera space, a camera looks at Z+ of , screen right is X+ and screen up is Y-. However, not all the cameras are defined this way. We offer you a conversion method, converting a camera from one system to another.

For example, in order to convert an OpenCV camera into a Blender camera, call `convert_camera_parameter()`, and the direction of extrinsic (world2cam or cam2world) will not be changed.

```python
from xrprimer.transform.convention.camera import convert_camera_parameter

blender_pinhole_param = convert_camera_parameter(pinhole_param, dst'blender')
```

Here is a sheet of supported camera conventions:

| Convention name | Forward | Up   | Right |
| --------------- | ------ | ---- | ----- |
| opencv          | Z+     | Y-   | X+    |
| blender         | Z-     | Y+   | X+    |
| unreal          | X+     | Z+   | Y+    |
