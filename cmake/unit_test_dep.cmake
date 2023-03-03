include(CMakeParseArguments)

include(CTest)
enable_testing()

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
    add_test(NAME ${target} COMMAND ${target})
endfunction()
