#pragma once

#include <iostream>
#include <opencv2/core.hpp>
#include <vector>

#include "data_structure/camera/pinhole_camera.h"

struct MultiCalibrator {
    MultiCalibrator(std::vector<PinholeCameraParameter> &params) : pinhole_params(params){};
    cv::Size pattern_size;  ///< chess pattern size
    cv::Size2f square_size; ///< chess size
    std::vector<PinholeCameraParameter> &pinhole_params;
    std::vector<std::vector<int>> found_corners_list;
    // frames/camera/points
    std::vector<std::vector<std::vector<cv::Point2f>>> point2d_lists;

    void Clear() { point2d_lists.clear(); }
    bool Push(const std::vector<std::string> &image_paths);
    bool Init();
    void OptimizeExtrinsics();
    void NormalizeCamExtrinsics();
};
