if(BUILD_EXTERNAL)
    # build from source
    include(${CMAKE_SOURCE_DIR}/cmake/external/eigen.cmake)
    include(${CMAKE_SOURCE_DIR}/cmake/external/ceres.cmake)
    include(${CMAKE_SOURCE_DIR}/cmake/external/opencv.cmake)
    include(${CMAKE_SOURCE_DIR}/cmake/external/jsoncpp.cmake)
    include(${CMAKE_SOURCE_DIR}/cmake/external/spdlog.cmake)
    include(${CMAKE_SOURCE_DIR}/cmake/external/pybind11.cmake)
    include(${CMAKE_SOURCE_DIR}/cmake/external/pnpsolver.cmake)
else()
    # download prebuilt binary from conan
    include(${CMAKE_SOURCE_DIR}/cmake/conan.cmake)

    conan_cmake_autodetect(settings)
    conan_cmake_install(
        PATH_OR_REFERENCE ${CMAKE_SOURCE_DIR} REMOTE openxrlab SETTINGS
        ${settings}
    )
    conan_load_buildinfo()

    set(Eigen3_DIR "${CONAN_EIGEN_ROOT}/share/eigen3/cmake")
    set(Ceres_DIR "${CONAN_CERES-SOLVER_ROOT}/lib/cmake/Ceres")
    set(OpenCV_DIR "${CONAN_OPENCV_ROOT}/lib/cmake/opencv4")
    set(jsoncpp_DIR "${CONAN_JSONCPP_ROOT}/lib/cmake/jsoncpp")
    set(pybind11_DIR "${CONAN_PYBIND11_ROOT}/share/cmake/pybind11")
    set(spdlog_DIR "${CONAN_SPDLOG_ROOT}/lib/cmake/spdlog")
    set(GTest_DIR "${CONAN_GTEST_ROOT}/lib/cmake/GTest")
    set(PnpSolver_DIR "${CONAN_PNPSOLVER_ROOT}/lib/cmake")
    find_package(Eigen3 REQUIRED CONFIG)
    find_package(Ceres REQUIRED CONFIG)
    find_package(OpenCV REQUIRED CONFIG)
    find_package(pybind11 REQUIRED CONFIG)
    find_package(jsoncpp REQUIRED CONFIG)
    find_package(spdlog REQUIRED CONFIG)
    find_package(GTest REQUIRED CONFIG)
    find_package(PnpSolver REQUIRED CONFIG)

    xrlab_install_deps(
        TARGETS EIGEN CERES-SOLVER OPENCV JSONCPP SPDLOG PNPSOLVER
    )
endif()
