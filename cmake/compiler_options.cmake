
# MSVC compiler options
if ("${CMAKE_CXX_COMPILER_ID}" MATCHES "MSVC")
    set(DEFAULT_COMPILE_OPTIONS ${DEFAULT_COMPILE_OPTIONS}
        PRIVATE
            /MP           # -> build with multiple processes
            /W4           # -> warning level 4
            # /WX         # -> treat warnings as errors

            #$<$<CONFIG:Debug>:
            #/RTCc         # -> value is assigned to a smaller data type and results in a data loss
            #>

            $<$<CONFIG:Release>:
            /Gw           # -> whole program global optimization
            /GS-          # -> buffer security check: no
            /GL           # -> whole program optimization: enable link-time code generation (disables Zi)
            /GF           # -> enable string pooling
            >

            # No manual c++11 enable for MSVC as all supported MSVC versions for cmake-init have C++11 implicitly enabled (MSVC >=2013)

        PUBLIC
            /wd4251       # -> disable warning: 'identifier': class 'type' needs to have dll-interface to be used by clients of class 'type2'
            /wd4592       # -> disable warning: 'identifier': symbol will be dynamically initialized (implementation limitation)
            # /wd4201     # -> disable warning: nonstandard extension used: nameless struct/union (caused by GLM)
            # /wd4127     # -> disable warning: conditional expression is constant (caused by Qt)
    )
endif ()

# GCC and Clang compiler options
if ("${CMAKE_CXX_COMPILER_ID}" MATCHES "GNU" OR "${CMAKE_CXX_COMPILER_ID}" MATCHES "Clang")
    set(DEFAULT_COMPILE_OPTIONS ${DEFAULT_COMPILE_OPTIONS}
        PRIVATE
            -Wall
            -Wextra
            -Wunused

            -Wreorder
            -Wignored-qualifiers
            -Wmissing-braces
            -Wreturn-type
            -Wswitch
            -Wswitch-default
            -Wuninitialized
            -Wmissing-field-initializers

            $<$<CXX_COMPILER_ID:GNU>:
                -Wmaybe-uninitialized

                $<$<VERSION_GREATER:$<CXX_COMPILER_VERSION>,4.8>:
                    -Wpedantic
                    -Wreturn-local-addr
                >
            >

            $<$<CXX_COMPILER_ID:Clang>:
                -Wpedantic
                # -Wreturn-stack-address # gives false positives
            >

            $<$<BOOL:${OPTION_COVERAGE_ENABLED}>:
                -fprofile-arcs
                -ftest-coverage
            >

        PUBLIC
            $<$<PLATFORM_ID:Darwin>:
                -pthread
            >
    )
endif ()
