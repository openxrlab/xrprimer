#
# Pnp solver, ios not support
#

if(NOT IOS)

include(FetchContent)

FetchContent_Declare(
    pnpsolver
    GIT_REPOSITORY https://github.com/xxlxsyhl/pnpsolver.git
    GIT_TAG        33b87ca0b8857d248501715ebf2d9cab103e141f
    SOURCE_DIR     ${CMAKE_SOURCE_DIR}/_ext/pnpsolver
    BINARY_DIR     ${CMAKE_SOURCE_DIR}/_deps/pnpsolver
)

FetchContent_GetProperties(pnpsolver)
if(NOT pnpsolver_POPULATED)
    # Fetch the content using previously declared details
    FetchContent_Populate(pnpsolver)
    set(CMAKE_POLICY_DEFAULT_CMP0077 NEW)
    execute_process(COMMAND git reset --hard WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/_ext/pnpsolver)
    add_subdirectory(${pnpsolver_SOURCE_DIR} ${pnpsolver_BINARY_DIR})
endif()

else()
    message(STATUS "pnpsolver NOT support ios")
endif()
