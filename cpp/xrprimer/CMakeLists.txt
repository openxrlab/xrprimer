set(Headers
    calibration/calibrator.h
    calibration/calibrator_api.h
    data_structure/camera/camera.h
    data_structure/camera/pinhole_camera.h
    data_structure/math_util.h
)
source_group("Headers" FILES ${Headers})

set(Sources
    calibration/calibrator.cpp
    calibration/calibrator_api.cpp
    data_structure/camera/camera.cpp
    data_structure/camera/pinhole_camera.cpp
)

source_group("Sources" FILES ${Sources})

set(target xrprimer)

add_library(${target} ${Headers} ${Sources})
add_library(XRPrimer::${target} ALIAS ${target})

include(GenerateExportHeader)
generate_export_header(${target} EXPORT_FILE_NAME ${CMAKE_CURRENT_BINARY_DIR}/xrprimer_export.h)

target_include_directories(${target} 
        PUBLIC
            $<BUILD_INTERFACE:${CMAKE_SOURCE_DIR}/cpp/xrprimer>
            $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}/>
            $<INSTALL_INTERFACE:include/>
)

target_link_libraries(${target} PUBLIC Ceres::ceres Eigen3::Eigen opencv_core jsoncpp_static)

install(TARGETS ${target} DESTINATION lib EXPORT ${target}-targets)
install(EXPORT  ${target}-targets DESTINATION lib/cmake NAMESPACE XRPrimer::)
install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    DESTINATION include
    FILES_MATCHING
        PATTERN "*.h"
)

