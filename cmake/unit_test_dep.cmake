include(CMakeParseArguments)

# get gtest library
if(BUILD_EXTERNAL)
    include(FetchContent)
    fetchcontent_declare(
        googletest GIT_REPOSITORY https://github.com/google/googletest.git
        GIT_TAG 703bd9caab50b139428cea1aaff9974ebee5742e # release-1.10.0
    )

    fetchcontent_getproperties(googletest)

    if(NOT googletest_POPULATED)
        fetchcontent_populate(googletest)

        set(INSTALL_GTEST OFF CACHE BOOL "" FORCE)

        add_subdirectory(${googletest_SOURCE_DIR} ${googletest_BINARY_DIR})
        target_compile_options(gtest PRIVATE -Wno-maybe-uninitialized)
    endif()
endif()

function(xr_add_test target)
    set(options)
    set(multiValueArgs LINKS SRCS)
    cmake_parse_arguments(
        _TEST "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN}
    )
    add_executable(${target} ${_TEST_SRCS})

    if(BUILD_EXTERNAL)
        target_link_libraries(${target} ${_TEST_LINKS} gtest)
    else()
        target_link_libraries(${target} ${_TEST_LINKS} GTest::gtest)
    endif()

    set_target_properties(
        ${target} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
    )
endfunction()

function(xr_add_test_catch2 target)
    set(options)
    set(multiValueArgs LINKS SRCS)
    cmake_parse_arguments(
        _TEST "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN}
    )
    add_executable(${target} ${_TEST_SRCS})
    set_target_properties(
        ${target} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
    )
endfunction()
