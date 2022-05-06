#include <vector>

#include <json/json.h>
#include <opencv2/calib3d.hpp>
#include <opencv2/core.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/imgcodecs.hpp>
#include <opencv2/imgproc.hpp>

#include <calibration/calibrator.h>
#include <data_structure/camera/pinhole_camera.h>
#include <xrprimer_export.h>

XRPRIMER_EXPORT
void CalibrateMultiPinholeCamera(const std::string &calib_config_json,
                                 const std::vector<std::vector<std::string>>
                                     &img_groups, // frames/cameras/path
                                 std::vector<PinholeCameraParameter> &cameras) {

  MultiCalibrator calibrator(cameras);
  {
    // TODO: maybe use construtor
    Json::Value calib_config; // will contains the root value after parsing.
    Json::Reader reader;
    reader.parse(calib_config_json, calib_config, false);
    int chessboard_width = calib_config["chessboard_width"].asInt();
    int chessboard_height = calib_config["chessboard_height"].asInt();
    // unit: mm
    int chessboard_square_size = calib_config["chessboard_square_size"].asInt();

    calibrator.patternSize = cv::Size(chessboard_width, chessboard_height);
    calibrator.squareSize = cv::Size2f(1e-3f * chessboard_square_size,
                                       1e-3f * chessboard_square_size);
  }

  for (int gi = 0; gi < (int)img_groups.size(); ++gi) {
    std::cout << "Push frame idx: " << gi << std::endl;
    if (!calibrator.Push(img_groups[gi])) {
      std::cerr << "Invalid frame idx:" << gi << ", less than 2 camera!"
                << std::endl;
    }
  }
  if (!calibrator.Init()) {
    std::cout << "ExternalCalibrator: Can't Initialize External Param for All "
                 "Cameras!"
              << std::endl;
    return;
  }
  calibrator.optimizeExtrinsics();
  calibrator.NormalizeCamExtrinsics();
}