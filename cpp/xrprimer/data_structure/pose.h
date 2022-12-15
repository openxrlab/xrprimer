// Copyright (c) OpenXRLab. All rights reserved.

#pragma once

#include <Eigen/Eigen>

class Pose {

  public:
    Pose();
    Pose(const Eigen::Quaterniond &quaternion, const Eigen::Vector3d &position);
    Pose(const Eigen::AngleAxisd &angle_axis, const Eigen::Vector3d &position);
    Pose(const Eigen::Matrix3d &rotate_matrix, const Eigen::Vector3d &position);

    // properties
    const Eigen::Quaterniond &quaternion() const;
    const Eigen::Vector3d &position() const;
    Eigen::Matrix3d get_rotation() const;
    Eigen::AngleAxisd get_angle_axis() const;

    void set_quternion(const Eigen::Quaterniond &quaternion);
    void set_quternion(double w, double x, double y, double z);
    void set_quternion(const Eigen::Matrix3d &rotation);
    void set_quternion(const Eigen::AngleAxisd &angle_axis);

    void set_position(const Eigen::Vector3d &position);

    void SetIdentity();
    Pose Inverse() const;
    void InverseMutable();
    Pose Scale(double s) const;
    void ScaleMutable(double s);
    Eigen::Vector3d Center() const;

    ///
    /// @brief Set the current Pose as the value of the product of two
    /// Pose, This = Pose1 * Pose2
    ///
    void PoseMult(const Pose &lhs, const Pose &rhs);

    ///
    /// @brief the Pose of the vector
    ///
    Eigen::Vector3d operator*(const Eigen::Vector3d &vec) const;

    ///
    /// @brief the Pose of the Quaternion
    ///
    Eigen::Quaterniond operator*(const Eigen::Quaterniond &quaternion) const;

    ///
    /// @brief the Pose of the vector
    ///
    Eigen::Vector3d operator()(const Eigen::Vector3d &vec) const;

  private:
    Eigen::Quaterniond quaternion_;
    Eigen::Vector3d position_;

    friend bool operator!=(const Pose &lhs, const Pose &rhs);
    friend bool operator==(const Pose &lhs, const Pose &rhs);
};

bool operator!=(const Pose &lhs, const Pose &rhs);
bool operator==(const Pose &lhs, const Pose &rhs);
