include(${CMAKE_SOURCE_DIR}/cmake/unit_test_dep.cmake)

xr_add_test_catch2(
    test_calibrator SRCS test_calibrator.cpp filesystem_utils.cpp
)
target_link_libraries(
    test_calibrator XRPrimer::xrprimer ceres Ceres::ceres Eigen3::Eigen
    opencv_imgcodecs opencv_calib3d opencv_core
)

xr_add_test_catch2(test_image SRCS test_image.cpp)
target_link_libraries(
    test_image XRPrimer::xrprimer ceres Ceres::ceres Eigen3::Eigen
    opencv_imgcodecs opencv_calib3d opencv_core
)

xr_add_test_catch2(test_version SRCS test_version.cpp)
target_link_libraries(test_version XRPrimer::xrprimer)

xr_add_test_catch2(test_camera SRCS test_camera.cpp)
target_link_libraries(test_camera XRPrimer::xrprimer)

xr_add_test_catch2(test_pose SRCS test_pose.cpp)
target_link_libraries(test_pose XRPrimer::xrprimer)
