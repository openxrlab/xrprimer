
#pragma once

#include <data_structure/camera/pinhole_camera.h>
#include <vector>
#include <xrprimer_export.h>

XRPRIMER_EXPORT
void CalibrateMultiPinholeCamera(const std::string &calib_config_json,
                                 const std::vector<std::vector<std::string>>
                                     &img_groups, // frames/cameras/path
                                 std::vector<PinholeCameraParameter> &cameras);