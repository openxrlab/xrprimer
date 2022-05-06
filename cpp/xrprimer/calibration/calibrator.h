#pragma once

#include <iostream>
#include <opencv2/core.hpp>
#include <vector>

#include "data_structure/camera/pinhole_camera.h"

struct MultiCalibrator {
  MultiCalibrator(std::vector<PinholeCameraParameter> &cms) : cams(cms){};
  cv::Size patternSize;  ///< chess pattern size
  cv::Size2f squareSize; ///< chess size
  std::vector<PinholeCameraParameter> &cams;
  std::vector<std::vector<int>> foundCornersList;
  // frames/camera/points
  std::vector<std::vector<std::vector<cv::Point2f>>> p2ds;

  void Clear() { p2ds.clear(); }
  bool Push(const std::vector<std::string> &imgs);
  bool Init();
  void optimizeExtrinsics();
  void NormalizeCamExtrinsics();
};
