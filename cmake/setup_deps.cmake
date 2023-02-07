#
# when first config, only configure external project
#

if(3RT_FROM_LOCAL)
    include(${CMAKE_SOURCE_DIR}/cmake/external/common.cmake)
    include(${CMAKE_SOURCE_DIR}/cmake/external/eigen.cmake)
    include(${CMAKE_SOURCE_DIR}/cmake/external/ceres.cmake)
    include(${CMAKE_SOURCE_DIR}/cmake/external/opencv.cmake)
    include(${CMAKE_SOURCE_DIR}/cmake/external/pybind11.cmake)
    include(${CMAKE_SOURCE_DIR}/cmake/external/spdlog.cmake)
    include(${CMAKE_SOURCE_DIR}/cmake/external/jsoncpp.cmake)
    include(${CMAKE_SOURCE_DIR}/cmake/external/pnpsolver.cmake)
endif()

if(3RT_FROM_CONAN)
    # download prebuilt binary from conan
    include(${CMAKE_SOURCE_DIR}/cmake/conan.cmake)

    conan_add_remote(
        NAME openxrlab INDEX 0 URL
        http://conan.openxrlab.org.cn/artifactory/api/conan/openxrlab
        VERIFY_SSL True
    )

    conan_cmake_autodetect(settings)
    conan_cmake_install(
        PATH_OR_REFERENCE ${CMAKE_SOURCE_DIR} REMOTE openxrlab SETTINGS
        ${settings} UPDATE
    )
endif()
