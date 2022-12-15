// Copyright (c) OpenXRLab. All rights reserved.

#pragma once

/**
 * @brief Interface to calibrate multiple pinhole camera
 * @param calib_config_json Config in json format for calibration
 * @param img_groups A vector contains multiple frames, where each frame is a
 * vector containing images captured from multiple cameras
 * @param pinhole_params A vector of PinholeCameraParamter
 */

#include <data_structure/camera/pinhole_camera.h>
#include <vector>
#include <xrprimer_export.h>

XRPRIMER_EXPORT
void CalibrateMultiPinholeCamera(
    const std::string &calib_config_json,
    const std::vector<std::vector<std::string>>
        &img_groups, // frames/cameras/path
    std::vector<PinholeCameraParameter> &pinhole_params);
