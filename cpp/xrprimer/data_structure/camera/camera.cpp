#include "camera.h"
#include "data_structure/math_util.h"
#include <Eigen/Eigen>

#include <iostream>

/*
intrinsics:
        perspective:
            [fx,   0,    px,   0],
            [0,   fy,    py,   0],
            [0,    0,    0,    1],
            [0,    0,    1,    0]

        orthographics:
            [fx,   0,    0,   px],
            [0,   fy,    0,   py],
            [0,    0,    1,    0],
            [0,    0,    0,    1]

*/

void BaseCameraParameter::set_intrinsic(int width, int height, double fx,
                                        double fy, double cx, double cy,
                                        bool perspective) {
  width_ = width;
  height_ = height;
  Eigen::Matrix3f insic;
  insic.setIdentity();
  insic(0, 0) = fx;
  insic(1, 1) = fy;
  insic(0, 2) = cx;
  insic(1, 2) = cy;
  set_intrinsic(insic, perspective);
}

void BaseCameraParameter::set_intrinsic(const Eigen::Matrix3f &mat,
                                        bool perspective) {
  intrinsic_.setZero();
  intrinsic_(0, 0) = mat(0, 0);
  intrinsic_(1, 1) = mat(1, 1);
  if (perspective) {
    intrinsic_(0, 2) = mat(0, 2);
    intrinsic_(1, 2) = mat(1, 2);
    intrinsic_(2, 3) = 1;
    intrinsic_(3, 2) = 1;
  } else {
    intrinsic_(0, 3) = mat(0, 2);
    intrinsic_(1, 3) = mat(1, 2);
    intrinsic_(2, 2) = 1;
    intrinsic_(3, 3) = 1;
  }
}

Eigen::Matrix3f BaseCameraParameter::intrinsic33() const {
  Eigen::Matrix3f mat;
  mat.setIdentity();

  mat(0, 0) = intrinsic_(0, 0);
  mat(1, 1) = intrinsic_(1, 1);

  if (IsPerspective()) {
    mat(0, 2) = intrinsic_(0, 2);
    mat(1, 2) = intrinsic_(1, 2);
  } else {
    mat(0, 2) = intrinsic_(0, 3);
    mat(1, 2) = intrinsic_(1, 3);
  }
  return mat;
}

bool BaseCameraParameter::IsPerspective() const {
  return intrinsic_(3, 3) == 0;
}
