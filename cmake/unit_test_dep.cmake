
include(CMakeParseArguments)

# get gtest library

include(FetchContent)
FetchContent_Declare(
    googletest
    GIT_REPOSITORY https://github.com/google/googletest.git
    GIT_TAG        703bd9caab50b139428cea1aaff9974ebee5742e # release-1.10.0
    SOURCE_DIR     ${CMAKE_SOURCE_DIR}/_ext/googletest
    BINARY_DIR     ${CMAKE_SOURCE_DIR}/_deps/googletest
)

FetchContent_GetProperties(googletest)
if(NOT googletest_POPULATED)
    # Fetch the content using previously declared details
    FetchContent_Populate(googletest)
    add_subdirectory(${googletest_SOURCE_DIR} ${googletest_BINARY_DIR})
    target_compile_options(gtest PRIVATE -Wno-maybe-uninitialized)
endif()

function(xr_add_test target)
    set(options)
    set(multiValueArgs LINKS SRCS)
    cmake_parse_arguments(_TEST "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})
    add_executable(${target} ${_TEST_SRCS})
    target_link_libraries(${target} ${_TEST_LINKS} gtest)
endfunction()

