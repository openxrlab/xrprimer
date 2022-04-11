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
    execute_process(COMMAND git reset --hard WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/_ext/ceres-solver)
    execute_process(COMMAND git apply ${CMAKE_CURRENT_LIST_DIR}/ceres_cmake.diff 
                    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/_ext/ceres-solver)
    execute_process(COMMAND git rm cmake/FindGlog.cmake
                    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/_ext/ceres-solver)
    add_subdirectory(${ceres_SOURCE_DIR} ${ceres_BINARY_DIR})
endif()


