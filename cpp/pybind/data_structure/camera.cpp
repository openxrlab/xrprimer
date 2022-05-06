
#include "pybind/data_structure/camera.h"
#include <data_structure/camera/camera.h>
#include <data_structure/camera/fisheye_camera.h>
#include <data_structure/camera/omni_camera.h>
#include <data_structure/camera/pinhole_camera.h>

// Base
class PyBaseCameraParameter : public BaseCameraParameter {
public:
  using BaseCameraParameter::BaseCameraParameter;

  std::string ClassName() const override {
    PYBIND11_OVERRIDE_PURE(std::string, BaseCameraParameter, ClassName, );
  }

  bool SaveFile(const std::string &filename) const override {
    PYBIND11_OVERRIDE_PURE(bool, BaseCameraParameter, SaveFile, filename);
  }

  bool LoadFile(const std::string &filename) override {
    PYBIND11_OVERRIDE_PURE(bool, BaseCameraParameter, LoadFile, filename);
  }
};

// Pinhole
class PyPinholeCameraParameter : public PinholeCameraParameter {
public:
  using PinholeCameraParameter::PinholeCameraParameter;

  std::string ClassName() const override {
    PYBIND11_OVERRIDE(std::string, PinholeCameraParameter, ClassName, );
  }

  bool SaveFile(const std::string &filename) const override {
    PYBIND11_OVERRIDE(bool, PinholeCameraParameter, SaveFile, filename);
  }

  bool LoadFile(const std::string &filename) override {
    PYBIND11_OVERRIDE(bool, PinholeCameraParameter, LoadFile, filename);
  }
};

// Omni
class PyOmniCameraParameter : public OmniCameraParameter {
public:
  using OmniCameraParameter::OmniCameraParameter;

  std::string ClassName() const override {
    PYBIND11_OVERRIDE(std::string, OmniCameraParameter, ClassName, );
  }

  bool SaveFile(const std::string &filename) const override {
    PYBIND11_OVERRIDE(bool, OmniCameraParameter, SaveFile, filename);
  }

  bool LoadFile(const std::string &filename) override {
    PYBIND11_OVERRIDE(bool, OmniCameraParameter, LoadFile, filename);
  }
};

// Fisheye
class PyFisheyeCameraParameter : public FisheyeCameraParameter {
public:
  using FisheyeCameraParameter::FisheyeCameraParameter;

  std::string ClassName() const override {
    PYBIND11_OVERRIDE(std::string, FisheyeCameraParameter, ClassName, );
  }

  bool SaveFile(const std::string &filename) const override {
    PYBIND11_OVERRIDE(bool, FisheyeCameraParameter, SaveFile, filename);
  }

  bool LoadFile(const std::string &filename) override {
    PYBIND11_OVERRIDE(bool, FisheyeCameraParameter, LoadFile, filename);
  }
};

// pybind modules
void pybind_camera_classes(py::module &m) {
  // Base
  py::class_<BaseCameraParameter, PyBaseCameraParameter>(m,
                                                         "BaseCameraParameter")
      .def(py::init<const Eigen::Matrix4f &, const Eigen::Matrix3f &,
                    const Eigen::Vector3f &>(),
           "intrinsic"_a, "extrinsic_r"_a, "extrinsic_t"_a)
      .def("ClassName", &BaseCameraParameter::ClassName)
      .def("SaveFile", &BaseCameraParameter::SaveFile)
      .def("LoadFile", &BaseCameraParameter::LoadFile)
      .def("set_intrinsic",
           static_cast<void (BaseCameraParameter::*)(int, int, double, double,
                                                     double, double, bool)>(
               &BaseCameraParameter::set_intrinsic),
           "width"_a, "height"_a, "fx"_a, "fy"_a, "cx"_a, "cy"_a,
           "perspective"_a = true)
      .def("set_intrinsic",
           static_cast<void (BaseCameraParameter::*)(const Eigen::Matrix3f &,
                                                     bool)>(
               &BaseCameraParameter::set_intrinsic),
           "mat3x3"_a, "perspective"_a = true)
      .def("intrinsic33", &BaseCameraParameter::intrinsic33)
      .def_property(
          "intrinsic",
          [](BaseCameraParameter &p) -> Eigen::Ref<Eigen::Matrix4f> {
            return p.intrinsic_;
          },
          [](BaseCameraParameter &p, const Eigen::Matrix4f &mat) {
            p.intrinsic_ = mat;
          },
          "camera intrinsic (4x4): numpy.ndarray[numpy.float32[4, 4]] or list")
      .def_property(
          "extrinsic_r",
          [](BaseCameraParameter &p) -> Eigen::Ref<Eigen::Matrix3f> {
            return p.extrinsic_r_;
          },
          [](BaseCameraParameter &p, const Eigen::Matrix3f &mat) {
            p.extrinsic_r_ = mat;
          },
          "camera extrinsics R: numpy.ndarray[numpy.float32[3, 3]] or list")
      .def_property(
          "extrinsic_t",
          [](BaseCameraParameter &p) -> Eigen::Ref<Eigen::Vector3f> {
            return p.extrinsic_t_;
          },
          [](BaseCameraParameter &p, const Eigen::Vector3f &vec) {
            p.extrinsic_t_ = vec;
          },
          "camera extrinsics T: numpy.ndarray[numpy.float32[3, 1]] or list")
      .def_readwrite("name", &BaseCameraParameter::name_, "camera tag name")
      .def_readwrite("height", &BaseCameraParameter::height_,
                     "camera image height: int")
      .def_readwrite("width", &BaseCameraParameter::width_,
                     "camera image width: int")
      .def_readwrite("convention", &BaseCameraParameter::convention_,
                     "transform convention, default is opencv: str")
      .def_readwrite("world2cam", &BaseCameraParameter::world2cam_,
                     "world to camera flag: bool");

  // Pinhole
  py::class_<PinholeCameraParameter, BaseCameraParameter,
             PyPinholeCameraParameter>(m, "PinholeCameraParameter")
      .def(py::init<>(), "PinholeCameraParameter constructor");

  // Omni
  py::class_<OmniCameraParameter, BaseCameraParameter, PyOmniCameraParameter>(
      m, "OmniCameraParameter")
      .def(py::init<>(), "OmniCameraParameter constructor")
      .def_readwrite("k1", &OmniCameraParameter::k1_, " : float ")
      .def_readwrite("k2", &OmniCameraParameter::k2_, " : float ")
      .def_readwrite("k3", &OmniCameraParameter::k3_, " : float ")
      .def_readwrite("k4", &OmniCameraParameter::k4_, " : float ")
      .def_readwrite("k5", &OmniCameraParameter::k5_, " : float ")
      .def_readwrite("k6", &OmniCameraParameter::k6_, " : float ")
      .def_readwrite("p1", &OmniCameraParameter::p1_, " : float ")
      .def_readwrite("p2", &OmniCameraParameter::p2_, " : float ")
      .def_readwrite("xi", &OmniCameraParameter::xi_, " : float ")
      .def_property(
          "D",
          [](OmniCameraParameter &p) -> Eigen::Ref<Eigen::Vector4f> {
            return p.D_;
          },
          [](OmniCameraParameter &p, const Eigen::Vector4f &vec) {
            p.D_ = vec;
          },

          "omni camera D: numpy.ndarray[numpy.float32[4, 1]] or list");

  // Fisheye
  py::class_<FisheyeCameraParameter, BaseCameraParameter,
             PyFisheyeCameraParameter>(m, "FisheyeCameraParameter")
      .def(py::init<>(), "FisheyeCameraParameter constructor")
      .def_readwrite("k1", &FisheyeCameraParameter::k1_, " : float")
      .def_readwrite("k2", &FisheyeCameraParameter::k2_, " : float")
      .def_readwrite("k3", &FisheyeCameraParameter::k3_, " : float")
      .def_readwrite("k4", &FisheyeCameraParameter::k4_, " : float")
      .def_readwrite("k5", &FisheyeCameraParameter::k5_, " : float")
      .def_readwrite("k6", &FisheyeCameraParameter::k6_, " : float")
      .def_readwrite("p1", &FisheyeCameraParameter::p1_, " : float")
      .def_readwrite("p2", &FisheyeCameraParameter::p2_, " : float");
}

void xrprimer_pybind_camera(py::module &m) {
  py::module m_submodule = m.def_submodule("camera");
  pybind_camera_classes(m_submodule);
}
