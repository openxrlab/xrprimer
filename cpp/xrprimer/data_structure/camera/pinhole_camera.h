#pragma once

#include <data_structure/camera/camera.h>

class XRPRIMER_EXPORT PinholeCameraParameter : public BaseCameraParameter {
public:
  PinholeCameraParameter() = default;
  ~PinholeCameraParameter() = default;

  float k1_, k2_, k3_, k4_, k5_, k6_, p1_, p2_;

  void SaveFile(const std::string &filename) override;
  void LoadFile(const std::string &filename) override;
};
