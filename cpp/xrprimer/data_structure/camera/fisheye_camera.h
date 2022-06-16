#pragma once

#include <data_structure/camera/camera.h>

class XRPRIMER_EXPORT FisheyeCameraParameter : public BaseCameraParameter {
  public:
    FisheyeCameraParameter();
    ~FisheyeCameraParameter() = default;

    float k1_, k2_, k3_, k4_, k5_, k6_, p1_, p2_;

    std::string ClassName() const override;
    bool SaveFile(const std::string &filename) const override;
    bool LoadFile(const std::string &filename) override;
};
