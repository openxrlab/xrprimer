if(NOT IOS)
    include(ExternalProject)

    externalproject_add(
        ext_pybind11
        PREFIX pybind11
        URL https://github.com/pybind/pybind11/archive/refs/tags/v2.10.4.tar.gz
        CMAKE_ARGS ${ExternalProject_CMAKE_ARGS_hidden}
                   -DCMAKE_INSTALL_PREFIX=${STAGED_INSTALL_PREFIX}/pybind11
                   -DBUILD_TESTING=OFF -DPYBIND11_USE_STATIC_PYTHON=ON
    )
else()
    message(STATUS "[XRPrimer] Disable pybind11 on IOS")
endif()
