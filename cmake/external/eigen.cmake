include(FetchContent)

FetchContent_Declare(
    eigen
    GIT_REPOSITORY https://gitlab.com/libeigen/eigen.git
    GIT_TAG        3147391d946bb4b6c68edd901f2add6ac1f31f8c   #3.4.0
    SOURCE_DIR     ${CMAKE_SOURCE_DIR}/_ext/eigen
    BINARY_DIR     ${CMAKE_SOURCE_DIR}/_deps/eigen
)

FetchContent_GetProperties(eigen)
if(NOT eigen_POPULATED)
    # Fetch the content using previously declared details
    FetchContent_Populate(eigen)
    execute_process(COMMAND git reset --hard WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/_ext/eigen)
    execute_process(COMMAND git apply ${CMAKE_CURRENT_LIST_DIR}/eigen_cmake.patch
                    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/_ext/eigen)
    add_subdirectory(${eigen_SOURCE_DIR} ${eigen_BINARY_DIR})
    set(Eigen3_DIR ${eigen_BINARY_DIR})
endif()
