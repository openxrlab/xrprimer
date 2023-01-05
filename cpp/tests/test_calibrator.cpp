
#include "filesystem_utils.hpp"
#include <calibration/calibrator_api.h>
#include <iostream>
#include <iterator>
#define CATCH_CONFIG_MAIN
#include "catch.hpp"

TEST_CASE("test_calibrator", "MultiPinholeCamera") {

    const std::string images_folder =
        "test/data/calib_pinhole_camera/input/images/";
    const std::string config_folder =
        "test/data/calib_pinhole_camera/input/config/";

    std::vector<std::string> image_files;
    FileSysUtilsFindFilesInPath(images_folder, image_files);
    // std::copy(images.begin(), images.end(),
    //           std::ostream_iterator<std::string>(std::cout, "\n"));

    std::vector<std::string> cameras_json_files;
    FileSysUtilsFindFilesInPath(config_folder, cameras_json_files);
    // std::copy(cameras_json_files.begin(), cameras_json_files.end(),
    //           std::ostream_iterator<std::string>(std::cout, "\n"));

    REQUIRE(0 != image_files.size());
    REQUIRE(0 != cameras_json_files.size());

    int max_frame_idx = 0;
    std::for_each(
        image_files.begin(), image_files.end(), [&](const std::string &name) {
            int frame_idx;
            int cam_idx;
            sscanf(name.c_str(), "img%d_cam%d.jpg", &frame_idx, &cam_idx);
            if (max_frame_idx < frame_idx) {
                max_frame_idx = frame_idx;
            }
        });

    // aligned frames
    std::vector<std::vector<std::string>> images(max_frame_idx + 1);
    std::for_each(
        image_files.begin(), image_files.end(), [&](const std::string &name) {
            int frame_idx;
            int cam_idx;
            sscanf(name.c_str(), "img%d_cam%d.jpg", &frame_idx, &cam_idx);
            if (images[frame_idx].empty()) {
                images[frame_idx].resize(cameras_json_files.size());
            }

            std::string path = images_folder + name;
            if (FileSysUtilsPathExists(path)) {
                images[frame_idx][cam_idx] = images_folder + name;
            } else {
                std::cerr << "Not found [" << path << "]" << std::endl;
            }
        });

    // set camera intrinsic
    std::vector<PinholeCameraParameter> cameras(cameras_json_files.size());
    std::for_each(cameras_json_files.begin(), cameras_json_files.end(),
                  [&](const std::string &name) {
                      int cam_idx = 0;
                      sscanf(name.c_str(), "cam_%d.json", &cam_idx);

                      std::string path = config_folder + name;
                      if (FileSysUtilsPathExists(path)) {
                          cameras[cam_idx].LoadFile(path);
                      } else {
                          std::cerr << "Not found [" << path << "]"
                                    << std::endl;
                      }
                  });

    std::string calib_config = R"(
    {
      "chessboard_width": 6,
      "chessboard_height": 7,
      "chessboard_square_size": 100
    }
  )";

    CalibrateMultiPinholeCamera(calib_config, images, cameras);

    // compare
    std::vector<PinholeCameraParameter> loadcamera(cameras.size());
    std::string postfix = ".json";
    for (size_t i = 0; i < cameras.size(); i++) {
        std::string prefix = "cam_out_";
        cameras[i].SaveFile(prefix + std::to_string(i) + postfix);

        // check load file
        loadcamera[i].LoadFile(prefix + std::to_string(i) + postfix);
        prefix = "cam_load_";
        loadcamera[i].SaveFile(prefix + std::to_string(i) + postfix);
        std::cerr << "cam id: " << i
                  << " param file: " << (prefix + std::to_string(i) + postfix)
                  << std::endl;

        REQUIRE(cameras[i].intrinsic_ == loadcamera[i].intrinsic_);
        REQUIRE(cameras[i].extrinsic_r_ == loadcamera[i].extrinsic_r_);
        REQUIRE(cameras[i].extrinsic_t_ == loadcamera[i].extrinsic_t_);
    }
}
