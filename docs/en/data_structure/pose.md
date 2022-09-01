# Pose

This file introduces the supported pose data structure in C++.
Generally, pose consists of a rotation and position.

#### Attributes

Here are attributes of class `Pose`.

| Attribute name  | Type                       | Description                                     |
| --------------- | -------------------------- | ----------------------------------------------- |
| quaternion\_    | Eigen::Quaterniond         | Pose rotation                                   |
| position\_      | Eigen::Vector3d            | Pose position                                   |

#### Construct a Pose

Construct a pose with default value, where rotation is identity matrix and position is zero.

```C++
Pose pose;
```

Construct a pose with rotation and position. Rotation can be represented as quaternion, axis angle or rotation matrix.

```C++
Eigen::Vector3d vec3d;

Eigen::Quaterniond quaternion;
Pose pose1(quaternion.setIdentity(), vec3d.setZero());

Eigen::AngleAxisd angleAxis(30, Eigen::Vector3d::UnitY());
Pose pose2(angleAxis, vec3d.setZero());

Eigen::Matrix3d mat3d;
Pose pose3(mat3d.setIdentity(), vec3d.setZero());
```

#### Set Pose to identity

A identity pose denotes to identity rotation and zero position

```C++
pose.SetIdentity();
```

#### Scale a Pose

Scale a pose means multiplying scaling factor with the position.

```C++
auto p = pose3.Scale(1.2);
pose3.ScaleMutable(1.4);
```

#### Inverse a Pose

Inverse a pose is defined as (1) applying rotation inversion and (2) multiplying position with inversed rotation.

```C++
pose.Inverse();
pose.InverseMutable();
```
