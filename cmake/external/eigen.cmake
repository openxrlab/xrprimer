include(FetchContent)

fetchcontent_declare(
    eigen GIT_REPOSITORY https://gitlab.com/libeigen/eigen.git
    GIT_TAG 3147391d946bb4b6c68edd901f2add6ac1f31f8c # 3.4.0
)

fetchcontent_getproperties(eigen)

if(NOT eigen_POPULATED)
    # Fetch the content using previously declared details
    fetchcontent_populate(eigen)
    execute_process(
        COMMAND git reset --hard
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/_ext/eigen
    )

    # https://gitlab.kitware.com/cmake/cmake/-/issues/22687
    execute_process(
        COMMAND git apply ${CMAKE_CURRENT_LIST_DIR}/eigen_cmake.patch
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/_ext/eigen
    )
    add_subdirectory(${eigen_SOURCE_DIR} ${eigen_BINARY_DIR})
    set(Eigen3_DIR ${eigen_BINARY_DIR})
endif()
