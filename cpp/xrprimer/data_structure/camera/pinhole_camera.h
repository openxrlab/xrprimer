// Copyright (c) OpenXRLab. All rights reserved.

#pragma once

#include <data_structure/camera/camera.h>

/// \class PinholeCameraParameter
///
/// \brief Contains the pinhole camera parameter.
class XRPRIMER_EXPORT PinholeCameraParameter : public BaseCameraParameter {
  public:
    PinholeCameraParameter() = default;
    ~PinholeCameraParameter() = default;

    std::string ClassName() const override;
    bool SaveFile(const std::string &filename) const override;
    bool LoadFile(const std::string &filename) override;
};
