if(NOT BUILD_ONLY_BASE)
    add_subdirectory(calibration)
endif()

add_library(xrprimer)
add_library(XRPrimer::xrprimer ALIAS xrprimer)

target_sources(
    xrprimer
    PRIVATE common/version.cpp
            data_structure/image.cpp
            data_structure/pose.cpp
            data_structure/camera/camera.cpp
            data_structure/camera/fisheye_camera.cpp
            data_structure/camera/omni_camera.cpp
            data_structure/camera/pinhole_camera.cpp
)

target_compile_options(xrprimer PRIVATE -fPIC)

include(GenerateExportHeader)
generate_export_header(
    xrprimer EXPORT_FILE_NAME ${CMAKE_CURRENT_BINARY_DIR}/xrprimer_export.h
)

target_include_directories(
    xrprimer
    PUBLIC $<BUILD_INTERFACE:${CMAKE_SOURCE_DIR}/cpp/xrprimer>
           $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}/>
           $<INSTALL_INTERFACE:include/xrprimer>
)

target_link_libraries(
    xrprimer PUBLIC $<$<TARGET_EXISTS:calibrator_obj>:calibrator_obj>
                    ${XRPRIMER_PUBLIC_TARGET}
)

install(TARGETS xrprimer DESTINATION lib EXPORT xrprimer-targets)
install(EXPORT xrprimer-targets DESTINATION lib/cmake/xrprimer
        NAMESPACE XRPrimer::
)
install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR} DESTINATION include FILES_MATCHING
        PATTERN "*.h"
)

include(CMakePackageConfigHelpers)
configure_package_config_file(
    ${CMAKE_SOURCE_DIR}/cmake/XRPrimerConfig.cmake.in
    "${CMAKE_CURRENT_BINARY_DIR}/XRPrimerConfig.cmake"
    INSTALL_DESTINATION lib/cmake/xrprimer NO_CHECK_REQUIRED_COMPONENTS_MACRO
)

file(READ ${CMAKE_SOURCE_DIR}/cmake/dependencies.cmake DEPS_FILE_CONTENTS)
string(REPLACE "find_package" "find_dependency" DEPS_FILE_CONTENTS
               ${DEPS_FILE_CONTENTS}
)
file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/dependencies.cmake ${DEPS_FILE_CONTENTS})

write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/XRPrimerConfigVersion.cmake"
    VERSION
        "${XRPRIMER_VERSION_MAJOR}.${XRPRIMER_VERSION_MINOR}.${XRPRIMER_VERSION_PATCH}"
    COMPATIBILITY AnyNewerVersion
)

install(
    FILES "${CMAKE_CURRENT_BINARY_DIR}/XRPrimerConfig.cmake"
          "${CMAKE_CURRENT_BINARY_DIR}/XRPrimerConfigVersion.cmake"
          "${CMAKE_CURRENT_BINARY_DIR}/dependencies.cmake"
    DESTINATION lib/cmake/xrprimer
)

configure_file(common/config.h.in common/config.h)

install(FILES ${CMAKE_CURRENT_BINARY_DIR}/xrprimer_export.h
        DESTINATION include/xrprimer
)
