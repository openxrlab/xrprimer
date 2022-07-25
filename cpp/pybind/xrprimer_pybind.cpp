
#include "pybind/xrprimer_pybind.h"

#include <Eigen/Eigen>
#include <pybind/calibration/calibrator_api.h>
#include <pybind/common/version.h>
#include <pybind/data_structure/camera.h>
#include <pybind/data_structure/pose.h>

void pybind_eigen_classes(py::module &m) {
    py::class_<Eigen::Quaterniond>(
        m, "Quaterniond",
        "Provides a unit quaternion binding of Eigen::Quaternion<double>.")
        .def(py::init([]() { return Eigen::Quaterniond::Identity(); }))
        .def_static("Identity", []() { return Eigen::Quaterniond::Identity(); })
        .def(py::init([](const Eigen::Vector4d &wxyz) {
                 Eigen::Quaterniond out(wxyz(0), wxyz(1), wxyz(2), wxyz(3));
                 return out;
             }),
             py::arg("wxyz"))
        .def(py::init([](double w, double x, double y, double z) {
                 Eigen::Quaterniond out(w, x, y, z);
                 return out;
             }),
             py::arg("w"), py::arg("x"), py::arg("y"), py::arg("z"))
        .def(py::init([](const Eigen::Matrix3d &rotation) {
                 Eigen::Quaterniond out(rotation);
                 return out;
             }),
             py::arg("rotation"))
        .def(py::init([](const Eigen::Quaterniond &other) { return other; }),
             py::arg("other"))
        .def("w", [](const Eigen::Quaterniond *self) { return self->w(); })
        .def("x", [](const Eigen::Quaterniond *self) { return self->x(); })
        .def("y", [](const Eigen::Quaterniond *self) { return self->y(); })
        .def("z", [](const Eigen::Quaterniond *self) { return self->z(); })
        .def("xyz",
             [](const Eigen::Quaterniond *self) {
                 return Eigen::Vector3d(self->vec());
             })
        .def("wxyz",
             [](Eigen::Quaterniond *self) {
                 Eigen::Vector4d wxyz;
                 wxyz << self->w(), self->vec();
                 return wxyz;
             })
        .def(
            "set_wxyz",
            [](Eigen::Quaterniond *self, const Eigen::Vector4d &wxyz) {
                Eigen::Quaterniond update;
                update.w() = wxyz(0);
                update.vec() = wxyz.tail(3);
                *self = update;
            },
            py::arg("wxyz"))
        .def(
            "set_wxyz",
            [](Eigen::Quaterniond *self, double w, double x, double y,
               double z) {
                Eigen::Quaterniond update(w, x, y, z);
                *self = update;
            },
            py::arg("w"), py::arg("x"), py::arg("y"), py::arg("z"))
        .def("rotation",
             [](const Eigen::Quaterniond *self) {
                 return self->toRotationMatrix();
             })
        .def("set_rotation",
             [](Eigen::Quaterniond *self, const Eigen::Matrix3d &rotation) {
                 Eigen::Quaterniond update(rotation);
                 *self = update;
             })
        .def("__str__",
             [](const Eigen::Quaterniond *self) {
                 return py::str("<quaternion>(w={}, x={}, y={}, z={})")
                     .format(self->w(), self->x(), self->y(), self->z());
             })
        .def(
            "multiply",
            [](const Eigen::Quaterniond &self,
               const Eigen::Quaterniond &other) { return self * other; },
            "Quaternion multiplication")
        .def(
            "slerp",
            [](const Eigen::Quaterniond &self, double t,
               const Eigen::Quaterniond &other) {
                return self.slerp(t, other);
            },
            py::arg("t"), py::arg("other"),
            "The spherical linear interpolation between the two quaternions "
            "(self and other) at the parameter t in [0;1].")
        .def("inverse",
             [](const Eigen::Quaterniond *self) { return self->inverse(); })
        .def("conjugate",
             [](const Eigen::Quaterniond *self) { return self->conjugate(); });

    // AngleAxis
    py::class_<Eigen::AngleAxisd>(m, "AngleAxisd",
                                  "Bindings for Eigen::AngleAxis<>.")
        .def(py::init([]() { return Eigen::AngleAxisd::Identity(); }))
        .def_static("Identity", []() { return Eigen::AngleAxisd::Identity(); })
        .def(py::init([](const double &angle, const Eigen::Vector3d &axis) {
                 Eigen::AngleAxisd out(angle, axis);
                 return out;
             }),
             py::arg("angle"), py::arg("axis"))
        .def(py::init([](const Eigen::Quaterniond &q) {
                 Eigen::AngleAxisd out(q);
                 return out;
             }),
             py::arg("quaternion"))
        .def(py::init([](const Eigen::Matrix3d &rotation) {
                 Eigen::AngleAxisd out(rotation);
                 return out;
             }),
             py::arg("rotation"))
        .def(py::init([](const Eigen::AngleAxisd &other) { return other; }),
             py::arg("other"))
        .def("angle",
             [](const Eigen::AngleAxisd *self) { return self->angle(); })
        .def("axis", [](const Eigen::AngleAxisd *self) { return self->axis(); })
        .def(
            "set_angle",
            [](Eigen::AngleAxisd *self, const double &angle) {
                // N.B. Since `axis` should already be valid, do not need to
                // check.
                self->angle() = angle;
            },
            py::arg("angle"))
        .def(
            "set_axis",
            [](Eigen::AngleAxisd *self, const Eigen::Vector3d &axis) {
                Eigen::AngleAxisd update(self->angle(), axis);
                *self = update;
            },
            py::arg("axis"))
        .def("rotation",
             [](const Eigen::AngleAxisd *self) {
                 return self->toRotationMatrix();
             })
        .def(
            "set_rotation",
            [](Eigen::AngleAxisd *self, const Eigen::Matrix3d &rotation) {
                Eigen::AngleAxisd update(rotation);
                *self = update;
            },
            py::arg("rotation"))
        .def("quaternion",
             [](const Eigen::AngleAxisd *self) {
                 return Eigen::Quaterniond(*self);
             })
        .def(
            "set_quaternion",
            [](Eigen::AngleAxisd *self, const Eigen::Quaterniond &q) {
                Eigen::AngleAxisd update(q);
                *self = update;
            },
            py::arg("q"))
        .def("__str__",
             [](const Eigen::AngleAxisd *self) {
                 return py::str("<AngleAxisd>(angle={}, axis={})")
                     .format(self->angle(), self->axis());
             })
        .def(
            "multiply",
            [](const Eigen::AngleAxisd &self, const Eigen::AngleAxisd &other) {
                return self * other;
            },
            py::arg("other"))
        .def("inverse",
             [](const Eigen::AngleAxisd *self) { return self->inverse(); });
}

PYBIND11_MODULE(xrprimer_cpp, m) {
    // later in binding code:
    py::bind_vector<std::vector<int>>(m, "VectorInt");
    py::bind_vector<std::vector<int64_t>>(m, "VectorInt64");
    py::bind_vector<std::vector<uint8_t>>(m, "VectorUint8");
    py::bind_vector<std::vector<float>>(m, "VectorFloat");
    py::bind_vector<std::vector<double>>(m, "VectorDouble");

    py::bind_vector<std::vector<PinholeCameraParameter>>(
        m, "VectorPinholeCameraParameter")
        .def(py::init(
            [](int i) { return std::vector<PinholeCameraParameter>(i); }));
    py::implicitly_convertible<py::tuple,
                               std::vector<PinholeCameraParameter>>();
    py::implicitly_convertible<py::list, std::vector<PinholeCameraParameter>>();

    pybind_eigen_classes(m);
    xrprimer_pybind_camera(m);
    xrprimer_pybind_calibrator(m);
    xrprimer_pybind_version(m);
    xrprimer_pybind_pose(m);
}
