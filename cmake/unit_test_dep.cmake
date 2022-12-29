include(CMakeParseArguments)

# get gtest library
if(BUILD_EXTERNAL)
  include(FetchContent)
  FetchContent_Declare(
    googletest
    GIT_REPOSITORY https://github.com/google/googletest.git
    GIT_TAG 703bd9caab50b139428cea1aaff9974ebee5742e # release-1.10.0
    SOURCE_DIR ${CMAKE_SOURCE_DIR}/_ext/googletest BINARY_DIR
    ${CMAKE_SOURCE_DIR}/_deps/googletest)

  FetchContent_GetProperties(googletest)
  if(NOT googletest_POPULATED)
    # Fetch the content using previously declared details
    FetchContent_Populate(googletest)

    set(CMAKE_POLICY_DEFAULT_CMP0077 NEW)
    set(INSTALL_GTEST OFF)

    add_subdirectory(${googletest_SOURCE_DIR} ${googletest_BINARY_DIR})
    target_compile_options(gtest PRIVATE -Wno-maybe-uninitialized)
  endif()
endif()

function(xr_add_test target)
  set(options)
  set(multiValueArgs LINKS SRCS)
  cmake_parse_arguments(_TEST "${options}" "${oneValueArgs}"
                        "${multiValueArgs}" ${ARGN})
  add_executable(${target} ${_TEST_SRCS})
  if(BUILD_EXTERNAL)
    target_link_libraries(${target} ${_TEST_LINKS} gtest)
  else()
    target_link_libraries(${target} ${_TEST_LINKS} GTest::gtest)
  endif()
  set_target_properties(${target} PROPERTIES RUNTIME_OUTPUT_DIRECTORY
                                             ${CMAKE_BINARY_DIR}/bin)
endfunction()

function(xr_add_test_catch2 target)
  set(options)
  set(multiValueArgs LINKS SRCS)
  cmake_parse_arguments(_TEST "${options}" "${oneValueArgs}"
                        "${multiValueArgs}" ${ARGN})
  add_executable(${target} ${_TEST_SRCS})
  set_target_properties(${target} PROPERTIES RUNTIME_OUTPUT_DIRECTORY
                                             ${CMAKE_BINARY_DIR}/bin)
endfunction()
