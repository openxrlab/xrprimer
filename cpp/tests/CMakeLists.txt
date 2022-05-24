
include(${CMAKE_SOURCE_DIR}/cmake/unit_test_dep.cmake)

xr_add_test(calibrator_test SRCS test_main.cpp calibrator_test.cpp filesystem_utils.cpp)
target_link_libraries(calibrator_test XRPrimer::xrprimer ceres Ceres::ceres Eigen3::Eigen opencv_imgcodecs opencv_calib3d opencv_core)

xr_add_test(image_test SRCS test_main.cpp image_test.cpp)
target_link_libraries(image_test XRPrimer::xrprimer ceres Ceres::ceres Eigen3::Eigen opencv_imgcodecs opencv_calib3d opencv_core)
