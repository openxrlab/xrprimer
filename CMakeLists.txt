cmake_minimum_required(VERSION 3.13)

#
# default install path
#

#
# install external deps
#
include(${CMAKE_SOURCE_DIR}/cmake/eigen.cmake)
include(${CMAKE_SOURCE_DIR}/cmake/ceres.cmake)
include(${CMAKE_SOURCE_DIR}/cmake/opencv.cmake)
include(${CMAKE_SOURCE_DIR}/cmake/jsoncpp.cmake)

include(cmake/utils.cmake)
get_revison_from_vcs(${CMAKE_SOURCE_DIR} GIT_REV)


set(CMAKE_INSTALL_PREFIX ${CMAKE_SOURCE_DIR}/install CACHE PATH "default install prefix" FORCE)
# if(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
    
# endif()


#
# meta info
#
set(META_PROJECT_NAME        "xrprimer")
set(META_PROJECT_DESCRIPTION "XR base library")
set(META_AUTHOR_ORGANIZATION "Sensetime XRlab")
set(META_AUTHOR_DOMAIN       "Sensetime")
set(META_AUTHOR_MAINTAINER   "openxrlab@sensetime.com")
set(META_VERSION_MAJOR       "0")
set(META_VERSION_MINOR       "0")
set(META_VERSION_PATCH       "1")
set(META_VERSION_REVISION    "${GIT_REV}")
set(META_VERSION             "${META_VERSION_MAJOR}.${META_VERSION_MINOR}.${META_VERSION_PATCH}")
set(META_NAME_VERSION        "${META_PROJECT_NAME} v${META_VERSION} (${META_VERSION_REVISION})")

#
# options
#
option(BUILD_SHARED_LIBS      "Build shared instead of static libraries."             OFF)
option(ENABLE_TEST           "Build unit test case."                                 OFF)

project(${META_PROJECT_NAME} VERSION  ${META_VERSION} LANGUAGES CXX)

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
# c++17
#
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

#
# hidden
#
set(CMAKE_CXX_VISIBILITY_PRESET hidden)
set(CMAKE_VISIBILITY_INLINES_HIDDEN YES)

#
# cpp
#
add_subdirectory(cpp)
