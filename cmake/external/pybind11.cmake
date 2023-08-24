if(NOT IOS)
    include(ExternalProject)

    externalproject_add(
        ext_pybind11
        PREFIX pybind11
        URL https://github.com/pybind/pybind11/archive/refs/tags/v2.6.2.tar.gz
        URL_HASH
        SHA256=8ff2fff22df038f5cd02cea8af56622bc67f5b64534f1b83b9f133b8366acff2
        CMAKE_ARGS ${ExternalProject_CMAKE_ARGS_hidden}
        -DCMAKE_INSTALL_PREFIX=${STAGED_INSTALL_PREFIX}/pybind11
        -DBUILD_TESTING=OFF
        -DPYBIND11_USE_STATIC_PYTHON=ON
    )
else()
    message(STATUS "[XRPrimer] Disable pybind11 on IOS")
endif()
