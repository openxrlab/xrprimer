#
# Pnp solver, ios not support
#

if(NOT IOS)

include(FetchContent)

FetchContent_Declare(
    pnpsolver
    GIT_REPOSITORY https://github.com/xxlxsyhl/pnpsolver.git
    GIT_TAG        8710099931eb2ab8112b2a17800d638df3ec8c0a
    SOURCE_DIR     ${CMAKE_SOURCE_DIR}/_ext/pnpsolver
    BINARY_DIR     ${CMAKE_SOURCE_DIR}/_deps/pnpsolver
)

FetchContent_GetProperties(pnpsolver)
if(NOT pnpsolver_POPULATED)
    # Fetch the content using previously declared details
    FetchContent_Populate(pnpsolver)
    set(CMAKE_POLICY_DEFAULT_CMP0077 NEW)
    set(BUILD_SHARED_LIBS OFF)
    execute_process(COMMAND git reset --hard WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/_ext/pnpsolver)
    add_subdirectory(${pnpsolver_SOURCE_DIR} ${pnpsolver_BINARY_DIR})
endif()

else()
    message(STATUS "pnpsolver NOT support ios")
endif()
