cmake_minimum_required(VERSION 3.13)

include(cmake/utils.cmake)
get_revison_from_vcs(${CMAKE_SOURCE_DIR} GIT_REV)

#
# meta info
#
set(META_PROJECT_NAME "xrprimer")
set(META_PROJECT_DESCRIPTION "XR base library")
set(META_AUTHOR_ORGANIZATION "Sensetime XRlab")
set(META_AUTHOR_DOMAIN "Sensetime")
set(META_AUTHOR_MAINTAINER "openxrlab@sensetime.com")
set(META_VERSION_MAJOR "0")
set(META_VERSION_MINOR "0")
set(META_VERSION_PATCH "1")
set(META_VERSION_REVISION "${GIT_REV}")
set(META_VERSION "${META_VERSION_MAJOR}.${META_VERSION_MINOR}.${META_VERSION_PATCH}")
set(META_NAME_VERSION "${META_PROJECT_NAME} v${META_VERSION} (${META_VERSION_REVISION})")

project(${META_PROJECT_NAME} VERSION ${META_VERSION} LANGUAGES CXX)

#
# default install path
#
if(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
    set(CMAKE_INSTALL_PREFIX ${CMAKE_SOURCE_DIR}/install CACHE PATH "default install prefix" FORCE)
endif()

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

#
# install external deps
#
option(BUILD_EXTERNAL "force build third deps." OFF)

if(BUILD_EXTERNAL)
    # build local
    include(${CMAKE_SOURCE_DIR}/cmake/external/eigen.cmake)
    include(${CMAKE_SOURCE_DIR}/cmake/external/ceres.cmake)
    include(${CMAKE_SOURCE_DIR}/cmake/external/opencv.cmake)
    include(${CMAKE_SOURCE_DIR}/cmake/external/jsoncpp.cmake)
    include(${CMAKE_SOURCE_DIR}/cmake/external/pybind11.cmake)
    include(${CMAKE_SOURCE_DIR}/cmake/external/spdlog.cmake)
else()
    # use conan
    include(${CMAKE_SOURCE_DIR}/cmake/conan.cmake)

    conan_cmake_autodetect(settings)
    conan_cmake_install(PATH_OR_REFERENCE ${CMAKE_SOURCE_DIR}
        BUILD missing
        REMOTE xrlab
        SETTINGS ${settings})
    conan_load_buildinfo()

    set(Eigen3_DIR "${CONAN_EIGEN_ROOT}/share/eigen3/cmake")
    set(Ceres_DIR "${CONAN_CERES-SOLVER_ROOT}/lib/cmake/Ceres")
    set(OpenCV_DIR "${CONAN_OPENCV_ROOT}/lib/cmake/opencv4")
    set(jsoncpp_DIR "${CONAN_JSONCPP_ROOT}/lib/cmake/jsoncpp")
    set(pybind11_DIR "${CONAN_PYBIND11_ROOT}/share/cmake/pybind11")
    set(spdlog_DIR "${CONAN_SPDLOG_ROOT}/lib/cmake/spdlog")
    set(GTest_DIR "${CONAN_GTEST_ROOT}/lib/cmake/GTest")
    set(PnpSolver_DIR "${CONAN_PNPSOLVER_ROOT}/lib/cmake")

    find_package(Eigen3 REQUIRED CONFIG)
    find_package(Ceres REQUIRED CONFIG)
    find_package(OpenCV REQUIRED CONFIG)
    find_package(pybind11 REQUIRED CONFIG)
    find_package(jsoncpp REQUIRED CONFIG)
    find_package(spdlog REQUIRED CONFIG)
    find_package(GTest REQUIRED CONFIG)
    find_package(PnpSolver REQUIRED CONFIG)

    XRLAB_INSTALL_DEPS(TARGETS EIGEN CERES-SOLVER OPENCV JSONCPP SPDLOG PNPSOLVER)
endif()

#
# options
#
option(BUILD_SHARED_LIBS "Build shared instead of static libraries." OFF)
option(ENABLE_TEST "Build unit test case." OFF)
option(PYTHON_BINDING "Enable Python binding." ON)

#
# Set policies
#
cmake_policy(SET CMP0042 NEW) # ENABLE CMP0042: MACOSX_RPATH is enabled by default.
cmake_policy(SET CMP0063 NEW) # ENABLE CMP0063: Honor visibility properties for all target types.
cmake_policy(SET CMP0077 NEW) # ENABLE CMP0077: option() honors normal variables

#
# compile_commands.json
#
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

#
# c++11
#
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

#
# hidden
#
set(CMAKE_CXX_VISIBILITY_PRESET hidden)
set(CMAKE_VISIBILITY_INLINES_HIDDEN YES)

# include(GNUInstallDirs)

#
# cpp
#
add_subdirectory(cpp)
