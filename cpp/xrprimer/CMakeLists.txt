set(Headers
    common/version.h
    calibration/calibrator.h
    calibration/calibrator_api.h
    data_structure/math_util.h
    data_structure/camera/camera.h
    data_structure/camera/pinhole_camera.h
    data_structure/camera/omni_camera.h
    data_structure/camera/fisheye_camera.h
    data_structure/image.h
    utils/logging.h
)
source_group("Headers" FILES ${Headers})

set(Sources
    common/version.cpp
    calibration/calibrator.cpp
    calibration/calibrator_api.cpp
    data_structure/camera/camera.cpp
    data_structure/camera/pinhole_camera.cpp
    data_structure/camera/omni_camera.cpp
    data_structure/camera/fisheye_camera.cpp
    data_structure/image.cpp
    utils/logging.cpp
)

source_group("Sources" FILES ${Sources})

set(target xrprimer)

add_library(${target} ${Headers} ${Sources})
add_library(XRPrimer::${target} ALIAS ${target})

target_compile_options(${target} PRIVATE -fPIC)

include(GenerateExportHeader)
generate_export_header(${target} EXPORT_FILE_NAME ${CMAKE_CURRENT_BINARY_DIR}/xrprimer_export.h)

target_include_directories(${target}
    PUBLIC
    $<BUILD_INTERFACE:${CMAKE_SOURCE_DIR}/cpp/xrprimer>
    $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}/>
    $<INSTALL_INTERFACE:include/>
)

# target_link_libraries(${target} PUBLIC Eigen3::Eigen Ceres::ceres opencv_core jsoncpp_static spdlog::spdlog_header_only PnpSolver::pnpsolver)
target_link_libraries(${target} PUBLIC Eigen3::Eigen Ceres::ceres opencv_core jsoncpp_static spdlog::spdlog_header_only)

install(TARGETS ${target} DESTINATION lib EXPORT ${target}-targets)
install(EXPORT ${target}-targets DESTINATION lib/cmake NAMESPACE XRPrimer::)
install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    DESTINATION include
    FILES_MATCHING
    PATTERN "*.h"
)

include(CMakePackageConfigHelpers)
configure_package_config_file(${CMAKE_SOURCE_DIR}/cmake/XRPrimerConfig.cmake.in
    "${CMAKE_CURRENT_BINARY_DIR}/XRPrimerConfig.cmake"
    INSTALL_DESTINATION lib/cmake/
    NO_CHECK_REQUIRED_COMPONENTS_MACRO
)

write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/XRPrimerConfigVersion.cmake"
    VERSION "${XRPRIMER_VERSION_MAJOR}.${XRPRIMER_VERSION_MINOR}.${XRPRIMER_VERSION_PATCH}"
    COMPATIBILITY AnyNewerVersion
)

install(FILES
    "${CMAKE_CURRENT_BINARY_DIR}/XRPrimerConfig.cmake"
    "${CMAKE_CURRENT_BINARY_DIR}/XRPrimerConfigVersion.cmake"
    DESTINATION lib/cmake
)

configure_file(common/config.h.in common/config.h)
