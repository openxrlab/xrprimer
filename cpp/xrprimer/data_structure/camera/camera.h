#pragma once

#include <Eigen/Core>

#include <string>
#include <vector>

#include <data_structure/math_util.h>
#include <xrprimer_export.h>

class XRPRIMER_EXPORT BaseCameraParameter {
public:
  BaseCameraParameter() = default;

  BaseCameraParameter(const std::string &name, int width, int height,
                      bool world2cam, const Eigen::Matrix4f &intrinsic,
                      const Eigen::Matrix3f &extrinsic_r,
                      const Eigen::Vector3f &extrinsic_t,
                      const std::string &convention)
      : name_(name), width_(width), height_(height), world2cam_(world2cam),
        intrinsic_(intrinsic), extrinsic_r_(extrinsic_r),
        extrinsic_t_(extrinsic_t), convention_(convention) {}

  BaseCameraParameter(const Eigen::Matrix4f &intrinsic,
                      const Eigen::Matrix3f &extrinsic_r,
                      const Eigen::Vector3f &extrinsic_t)
      : BaseCameraParameter("default", 1920, 1080, true, intrinsic, extrinsic_r,
                            extrinsic_t, "opencv") {}

  virtual ~BaseCameraParameter() = default;

  void set_intrinsic(int width, int height, double fx, double fy, double cx,
                     double cy, bool perspective = true);
  void set_intrinsic(const Eigen::Matrix3f &mat, bool prespective = true);
  Eigen::Matrix3f intrinsic33() const;

  //
  // interface
  //
  virtual void SaveFile(const std::string &filename) = 0;
  virtual void LoadFile(const std::string &filename) = 0;

  //
  // properties
  //
  std::string name_;
  Eigen::Matrix4f intrinsic_;
  Eigen::Matrix3f extrinsic_r_;
  Eigen::Vector3f extrinsic_t_;
  bool world2cam_;
  std::string convention_; // opencv or other
  int width_;
  int height_;

private:
  bool IsPerspective() const;
};
