
include(${CMAKE_SOURCE_DIR}/cmake/unit_test_dep.cmake)

xr_add_test(test_calibrator SRCS test_main.cpp test_calibrator.cpp filesystem_utils.cpp)
target_link_libraries(test_calibrator XRPrimer::xrprimer ceres Ceres::ceres Eigen3::Eigen opencv_imgcodecs opencv_calib3d opencv_core)

xr_add_test(test_image SRCS test_main.cpp test_image.cpp)
target_link_libraries(test_image XRPrimer::xrprimer ceres Ceres::ceres Eigen3::Eigen opencv_imgcodecs opencv_calib3d opencv_core)

xr_add_test(test_version SRCS test_main.cpp test_version.cpp)
target_link_libraries(test_version XRPrimer::xrprimer)
