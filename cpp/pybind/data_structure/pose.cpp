#include "pybind/data_structure/pose.h"
#include <data_structure/pose.h>

void xrprimer_pybind_pose(py::module &m) {
    py::class_<Pose>(m, "Pose")
        .def(py::init<>(), "Pose constructor")
        .def(py::init<const Eigen::Quaterniond &, const Eigen::Vector3d &>(),
             "quaternion", "position")
        .def(py::init<const Eigen::AngleAxisd &, const Eigen::Vector3d &>(),
             "angle_axis", "position")
        .def(py::init<const Eigen::Matrix3d &, const Eigen::Vector3d &>(),
             "rotate_matrix", "position")
        .def("quaternion", &Pose::quaternion, "quaternion")
        .def("set_quaternion",
             py::overload_cast<const Eigen::Matrix3d &>(&Pose::set_quternion))
        .def("set_quaternion",
             py::overload_cast<const Eigen::AngleAxisd &>(&Pose::set_quternion),
             "AngleAxisd")
        .def("position", &Pose::position, "position")
        .def("set_position", &Pose::set_position)
        .def("rotation", &Pose::get_rotation, "rotation")
        .def("angle_axis", &Pose::get_angle_axis, "angle_axis")
        .def("SetIdentity", &Pose::SetIdentity)
        .def(py::self * Eigen::Vector3d())
        .def(py::self * Eigen::Quaterniond())
        .def("InverseMutable", &Pose::InverseMutable)
        .def("Inverse", &Pose::Inverse)
        .def("Scale", &Pose::Scale)
        .def("ScaleMutable", &Pose::ScaleMutable)
        .def("PoseMult", &Pose::PoseMult)
        .def("__eq__",
             py::overload_cast<const Pose &, const Pose &>(&operator==))
        .def("__ne__",
             py::overload_cast<const Pose &, const Pose &>(&operator!=));
}
