cmake_minimum_required(VERSION 3.15)

# meta info
#
set(META_PROJECT_NAME "xrprimer")
set(META_PROJECT_DESCRIPTION "OpenXRLab foundational library")
set(META_AUTHOR_ORGANIZATION "OpenXRLab")
set(META_AUTHOR_DOMAIN "OpenXRLab")
set(META_AUTHOR_MAINTAINER "openxrlab@pjlab.org.cn")

include(cmake/version.cmake)

project(${META_PROJECT_NAME} VERSION ${META_VERSION} LANGUAGES C CXX)

option(BUILD_ONLY_BASE "Only build base library" OFF)

if(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
    set(_DEFAULT_INSTALL_PREFIX ${CMAKE_SOURCE_DIR}/install)
    set(CMAKE_INSTALL_PREFIX ${_DEFAULT_INSTALL_PREFIX}
        CACHE PATH "default install prefix" FORCE
    )
endif()

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

#
# for project dependencies libraries
#
# Setup dependencies library, when first run
#
option(3RT_FROM_LOCAL
       "Dependencies library will be built or find in local host." OFF
)
option(3RT_FROM_CONAN
       "Dependencies library will be download from openxrlab conan remote" OFF
)

# set external project install prefix
set(STAGED_INSTALL_PREFIX
    ${CMAKE_SOURCE_DIR}/3rdparty
    CACHE
        STRING
        "dependencies install directory, if not exist, need setup You need to get the dependencies first"
)

# add cmake prefix path for find external project, find_package(<xxx>)
list(INSERT CMAKE_PREFIX_PATH 0 ${STAGED_INSTALL_PREFIX})

if(IOS)
    # for find external framework bundle（same as 3rdparty）
    set(xrprimer_framework_path ${STAGED_INSTALL_PREFIX})
endif()

# install 3rdparty for dist.
install(DIRECTORY ${STAGED_INSTALL_PREFIX}/ DESTINATION 3rdparty/)

if(NOT EXISTS ${STAGED_INSTALL_PREFIX} AND NOT 3RT_FROM_LOCAL
   AND NOT 3RT_FROM_CONAN
)
    message(
        FATAL_ERROR
            "
    ---------------------------------------------------------------------------
    You need to get the dependencies first, Configure cmake with `-D3RT_FROM_LOCAL=ON` OR `-D3RT_FROM_CONAN=ON`
    and cmake --build <build_path>
    3RT_FROM_LOCAL: Dependencies library will be built or find in local host
    3RT_FROM_CONAN: Dependencies library will be download from openxrlab conan remote
    ---------------------------------------------------------------------------
    "
    )
endif()

if(3RT_FROM_LOCAL OR 3RT_FROM_CONAN)
    # Only build deps from source or download prebuilt library
    include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/setup_deps.cmake)

    return()
endif()

#
# for project
#
option(BUILD_SHARED_LIBS "Build shared instead of static libraries." OFF)
option(ENABLE_TEST "Build unit test case." OFF)
option(PYTHON_BINDING "Enable Python binding." ON)
option(CODE_COVERAGE "code coverage" OFF)

include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/dependencies.cmake)
include(${CMAKE_SOURCE_DIR}/cmake/code-coverage.cmake)

cmake_policy(SET CMP0042 NEW) # ENABLE CMP0042: MACOSX_RPATH is enabled by
cmake_policy(SET CMP0063 NEW) # ENABLE CMP0063: Honor visibility properties for
cmake_policy(SET CMP0077 NEW) # ENABLE CMP0077: option() honors normal variables

#
# c++11
#
set(CMAKE_CXX_STANDARD 14)
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
