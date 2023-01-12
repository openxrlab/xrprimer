if(CODE_COVERAGE)
    if(CMAKE_BUILD_TYPE)
        string(TOUPPER ${CMAKE_BUILD_TYPE} upper_build_type)
        if(NOT ${upper_build_type} STREQUAL "DEBUG")
            message(
                STATUS
                    "**WARNING** Code coverage need CMAKE_BUILD_TYPE=Debug, FORCE use Debug"
            )
        endif()
    endif()

    set(CMAKE_BUILD_TYPE Debug)
    set(CMAKE_CXX_OUTPUT_EXTENSION_REPLACE 1)
    set(CMAKE_C_OUTPUT_EXTENSION_REPLACE 1)

    if((CMAKE_C_COMPILER_ID STREQUAL "Clang" OR CMAKE_CXX_COMPILER_ID STREQUAL
                                                "Clang")
       AND (CMAKE_C_COMPILER_ID STREQUAL "AppleClang" OR CMAKE_CXX_COMPILER_ID
                                                         STREQUAL "AppleClang")
    )
        set(_GCOV_FLAGS "-fprofile-instr-generate -fcoverage-mapping")
    endif()
    if(CMAKE_COMPILER_IS_GNUCC OR CMAKE_COMPILER_IS_GNUCXX)
        set(_GCOV_FLAGS "-fprofile-arcs -ftest-coverage")
    endif()
    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} ${_GCOV_FLAGS}")
    set(CMAKE_C_FLAGS_DEBUG "${CMAKE_C_FLAGS_DEBUG} ${_GCOV_FLAGS}")
endif()
