
include(${CMAKE_SOURCE_DIR}/cmake/unit_test_dep.cmake)
xr_add_test(ut_test SRCS test.cpp filesystem_utils.cpp)
target_link_libraries(ut_test XRPrimer::xrprimer ceres Ceres::ceres Eigen3::Eigen opencv_imgcodecs opencv_calib3d opencv_core)
