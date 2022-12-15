// Copyright (c) OpenXRLab. All rights reserved.

#include <data_structure/pose.h>

Pose::Pose() {
    quaternion_.setIdentity();
    position_.setZero();
}

Pose::Pose(const Eigen::Quaterniond &quaternion,
           const Eigen::Vector3d &position) {
    quaternion_ = quaternion;
    position_ = position;
}

Pose::Pose(const Eigen::AngleAxisd &angle_axis,
           const Eigen::Vector3d &position) {
    quaternion_ = angle_axis;
    position_ = position;
}

Pose::Pose(const Eigen::Matrix3d &rotate_matrix,
           const Eigen::Vector3d &position) {
    quaternion_ = rotate_matrix;
    position_ = position;
}

// properties
const Eigen::Quaterniond &Pose::quaternion() const { return quaternion_; }

const Eigen::Vector3d &Pose::position() const { return position_; }

void Pose::set_quternion(const Eigen::Quaterniond &quaternion) {
    quaternion_ = quaternion;
}

void Pose::set_quternion(double w, double x, double y, double z) {
    quaternion_.w() = w;
    quaternion_.x() = x;
    quaternion_.y() = y;
    quaternion_.z() = z;
}
void Pose::set_quternion(const Eigen::Matrix3d &rotation) {
    quaternion_ = rotation;
}

void Pose::set_quternion(const Eigen::AngleAxisd &angle_axis) {
    quaternion_ = angle_axis;
}

void Pose::set_position(const Eigen::Vector3d &position) {
    position_ = position;
}

Eigen::Matrix3d Pose::get_rotation() const {
    return quaternion_.normalized().toRotationMatrix();
}

Eigen::AngleAxisd Pose::get_angle_axis() const {
    Eigen::AngleAxisd angle_axis(quaternion_.normalized());
    return angle_axis;
}

void Pose::SetIdentity() {
    quaternion_.setIdentity();
    position_.setZero();
}

void Pose::InverseMutable() {
    this->quaternion_ = this->quaternion_.inverse();
    this->position_ = -(this->quaternion_ * this->position_);
}

Pose Pose::Inverse() const {
    Pose pose = *this;
    pose.InverseMutable();
    return pose;
}

void Pose::ScaleMutable(double s) { this->position_ *= s; }

Pose Pose::Scale(double s) const {
    Pose pose = *this;
    pose.ScaleMutable(s);
    return pose;
}

Eigen::Vector3d Pose::Center() const {
    if (this) {
        return -(this->quaternion_.inverse() * this->position_);
    }
    return Eigen::Vector3d::Zero();
}

void Pose::PoseMult(const Pose &lhs, const Pose &rhs) {
    quaternion_ = lhs.quaternion() * rhs.quaternion();
    position_ = lhs(rhs.position_);
}

/// @brief the Pose of the vector
Eigen::Vector3d Pose::operator*(const Eigen::Vector3d &vec) const {
    return (*this)(vec);
}

/// @brief the Pose of the Quaternion
Eigen::Quaterniond Pose::operator*(const Eigen::Quaterniond &quaternion) const {
    return quaternion_ * quaternion;
}

/// @brief the Pose of the vector
Eigen::Vector3d Pose::operator()(const Eigen::Vector3d &vec) const {
    return quaternion_ * vec + position_;
}

bool operator!=(const Pose &lhs, const Pose &rhs) { return !(lhs == rhs); }

bool operator==(const Pose &lhs, const Pose &rhs) {
    return lhs.quaternion().coeffs() == rhs.quaternion().coeffs() &&
           lhs.position() == rhs.position();
}
