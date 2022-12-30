cmake_minimum_required(VERSION 3.15)

include(cmake/utils.cmake)
get_revison_from_vcs(${CMAKE_SOURCE_DIR} GIT_REV)

#
# meta info
#
set(META_PROJECT_NAME "xrprimer")
set(META_PROJECT_DESCRIPTION "OpenXRLab foundational library")
set(META_AUTHOR_ORGANIZATION "OpenXRLab")
set(META_AUTHOR_DOMAIN "OpenXRLab")
set(META_AUTHOR_MAINTAINER "openxrlab@pjlab.org.cn")

#
# parse version number
#
if(DEFINED XRPRIMER_VERSION_MAJOR AND DEFINED XRPRIMER_VERSION_MINOR
   AND DEFINED XRPRIMER_VERSION_PATCH
)
    set(XRPRIMER_VERSION_MAJOR ${XRPRIMER_VERSION_MAJOR})
    set(XRPRIMER_VERSION_MINOR ${XRPRIMER_VERSION_MINOR})
    set(XRPRIMER_VERSION_PATCH ${XRPRIMER_VERSION_PATCH})
else()
    file(STRINGS "version.txt" XRPRIMER_VERSION_READ)
    foreach(ver ${XRPRIMER_VERSION_READ})
        if(ver MATCHES "XRPRIMER_VERSION_(MAJOR|MINOR|PATCH) +([^ ]+)$")
            set(XRPRIMER_VERSION_${CMAKE_MATCH_1} "${CMAKE_MATCH_2}"
                CACHE INTERNAL ""
            )
        endif()
    endforeach()
endif()

set(META_VERSION_REVISION "${GIT_REV}")
set(META_VERSION
    "${XRPRIMER_VERSION_MAJOR}.${XRPRIMER_VERSION_MINOR}.${XRPRIMER_VERSION_PATCH}"
)
set(META_NAME_VERSION
    "${META_PROJECT_NAME} v${META_VERSION} (${META_VERSION_REVISION})"
)

project(${META_PROJECT_NAME} VERSION ${META_VERSION} LANGUAGES CXX)

#
# default install path
#
if(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
    set(_DEFAULT_INSTALL_PREFIX ${CMAKE_SOURCE_DIR}/install)
    set(CMAKE_INSTALL_PREFIX ${_DEFAULT_INSTALL_PREFIX}
        CACHE PATH "default install prefix" FORCE
    )
    if(IOS)
        set(CMAKE_INSTALL_PREFIX ${_DEFAULT_INSTALL_PREFIX}/ios
            CACHE PATH "ios default install prefix" FORCE
        )
    endif()
endif()

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

#
# install external deps
#
option(BUILD_EXTERNAL "force build third deps." OFF)
add_subdirectory(cmake/external)

#
# options
#
option(BUILD_SHARED_LIBS "Build shared instead of static libraries." OFF)
option(ENABLE_TEST "Build unit test case." OFF)
option(PYTHON_BINDING "Enable Python binding." ON)
option(CODE_COVERAGE "code coverage" OFF)

include(${CMAKE_SOURCE_DIR}/cmake/code-coverage.cmake)

#
# Set policies
#
cmake_policy(SET CMP0042 NEW) # ENABLE CMP0042: MACOSX_RPATH is enabled by
                              # default.
cmake_policy(SET CMP0063 NEW) # ENABLE CMP0063: Honor visibility properties for
                              # all target types.
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
