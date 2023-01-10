find_package(LAPACK)

if(NOT LAPACK_FOUND)
    message(
        FATAL_ERROR
            "[LAPACK AND BLAS] is required to build Ceres,
--------------------------------------
Ubuntu: apt -y install libatlas-base-dev libsuitesparse-dev ibgoogle-glog-dev
Centos7: yum -y install atlas-devel
--------------------------------------
"
    )
endif()

include(ExternalProject)
externalproject_add(
    ext_ceres
    PREFIX ceres
    URL https://github.com/ceres-solver/ceres-solver/archive/refs/tags/2.1.0.zip
    URL_HASH
        SHA256=57149e2018f3cf3fe97bc1df4a36f33319800b3f752ec1d01b28788d21cd496e
    CMAKE_ARGS -DCMAKE_INSTALL_PREFIX=${STAGED_INSTALL_PREFIX}/ceres
               -DBUILD_EXAMPLES=OFF
               -DBUILD_TESTING=OFF
               -DMINIGLOG=ON
               -DMINIGLOG_MAX_LOG_LEVEL=-2
               -DGFLAGS=OFF
               -DTBB=OFF
               -DOPENMP=OFF
               -DLAPACK=ON
               -DBUILD_BENCHMARKS=OFF
               -DPROVIDE_UNINSTALL_TARGET=OFF
               -DCMAKE_PREFIX_PATH=${STAGED_INSTALL_PREFIX}/eigen3
               ${ExternalProject_CMAKE_ARGS_hidden}
)

add_dependencies(ext_ceres ext_eigen)
