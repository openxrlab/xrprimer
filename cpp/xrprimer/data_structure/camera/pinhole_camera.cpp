
#include "json_helper_internal.h"
#include <data_structure/camera/pinhole_camera.h>
#include <iostream>

std::string PinholeCameraParameter::ClassName() const {
  return "PinholeCameraParameter";
}

bool PinholeCameraParameter::SaveFile(const std::string &filename) const {
  Json::Value obj;
  SaveBaseCameraParameter(obj, *this);
  return JsonToFile(obj, filename);
}

bool PinholeCameraParameter::LoadFile(const std::string &filename) {
  Json::Value obj;

  if (JsonFromFile(obj, filename)) {
    return LoadBaseCameraParameter(obj, *this);
  }
  return false;
}