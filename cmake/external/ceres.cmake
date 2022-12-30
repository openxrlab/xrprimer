include(FetchContent)

fetchcontent_declare(
    ceres GIT_REPOSITORY https://github.com/ceres-solver/ceres-solver.git
    GIT_TAG f68321e7de8929fbcdb95dd42877531e64f72f66 # 2.1.0
)

fetchcontent_getproperties(ceres)

if(NOT ceres_POPULATED)
    # Fetch the content using previously declared details
    fetchcontent_populate(ceres)

    find_package(LAPACK)

    if(NOT LAPACK_FOUND)
        message(
            FATAL_ERROR
                "[LAPACK AND BLAS] is required to build Ceres,
--------------------------------------
Ubuntu: apt -y install libatlas-base-dev
Centos7: yum -y install atlas-devel
--------------------------------------
"
        )
    endif()

    set(BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
    set(BUILD_TESTING OFF CACHE BOOL "" FORCE)
    set(MINIGLOG ON CACHE BOOL "" FORCE)
    set(MINIGLOG_MAX_LOG_LEVEL -2 CACHE STRING "" FORCE)
    set(GFLAGS OFF CACHE BOOL "" FORCE)
    set(TBB OFF CACHE BOOL "" FORCE)
    set(OPENMP OFF CACHE BOOL "" FORCE)
    set(LAPACK ON CACHE BOOL "" FORCE)
    set(BUILD_BENCHMARKS OFF CACHE BOOL "" FORCE)
    set(PROVIDE_UNINSTALL_TARGET OFF CACHE BOOL "" FORCE)

    execute_process(
        COMMAND git reset --hard
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/_ext/ceres-solver
    )
    add_subdirectory(${ceres_SOURCE_DIR} ${ceres_BINARY_DIR})
endif()
