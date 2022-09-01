#include <data_structure/pose.h>

#include <Eigen/Eigen>

#define CATCH_CONFIG_MAIN // This tells Catch to provide a main() - only do this
                          // in one cpp file
#include "catch.hpp"

TEST_CASE("Pose api test", "xrprimer Pose") {

    Pose pose;

    Eigen::Vector3d vec3d;

    Eigen::Quaterniond quaternion;
    Pose pose1(quaternion.setIdentity(), vec3d.setZero());

    Eigen::AngleAxisd angleAxis(30, Eigen::Vector3d::UnitY());
    Pose pose2(angleAxis, vec3d.setZero());

    Eigen::Matrix3d mat3d;
    Pose pose3(mat3d.setIdentity(), vec3d.setZero());

    const auto &quat = pose3.quaternion();
    const auto &posi = pose3.position();

    auto rot = pose3.get_rotation();
    auto angle = pose3.get_angle_axis();

    pose3.set_quternion(Eigen::Quaterniond(1, 0, 0, 0));
    pose3.set_quternion(1, 0, 0, 0);
    pose3.set_quternion(Eigen::Matrix3d().setIdentity());
    pose3.set_quternion(Eigen::AngleAxisd(10.0, Eigen::Vector3d::UnitX()));
    pose3.set_position(Eigen::Vector3d(1.0, 3.0, 4.0));
    pose3.SetIdentity();

    pose3.Inverse();
    pose3.InverseMutable();
    auto p = pose3.Scale(1.2);
    pose3.ScaleMutable(1.4);
    auto vec = pose3.Center();
}
