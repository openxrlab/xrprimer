include(FetchContent)

FetchContent_Declare(
    ceres
    GIT_REPOSITORY https://github.com/ceres-solver/ceres-solver.git
    GIT_TAG        399cda773035d99eaf1f4a129a666b3c4df9d1b1 #2.0.0
    SOURCE_DIR     ${CMAKE_SOURCE_DIR}/_ext/ceres-solver
    BINARY_DIR     ${CMAKE_SOURCE_DIR}/_deps/ceres-solver
)

FetchContent_GetProperties(ceres)
if(NOT ceres_POPULATED)
    # Fetch the content using previously declared details
    FetchContent_Populate(ceres)

    set(CMAKE_POLICY_DEFAULT_CMP0077 NEW)

    set(MINIGLOG ON)
    set(GFLAGS OFF)
    set(LAPACK OFF)
    set(CUSTOM_BLAS OFF)
    set(BUILD_TESTING OFF)
    set(BUILD_EXAMPLES OFF)
    set(BUILD_BENCHMARKS OFF)
    set(PROVIDE_UNINSTALL_TARGET OFF)

    execute_process(COMMAND git reset --hard WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/_ext/ceres-solver)
    add_subdirectory(${ceres_SOURCE_DIR} ${ceres_BINARY_DIR})
endif()


