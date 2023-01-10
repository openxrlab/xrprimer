find_package(Eigen3 REQUIRED CONFIG)
find_package(Ceres REQUIRED CONFIG)

if(NOT TARGET Ceres::ceres)
    add_library(Ceres::ceres INTERFACE IMPORTED)
    set_target_properties(
        Ceres::ceres PROPERTIES INTERFACE_LINK_LIBRARIES ceres
    )
endif()

find_package(OpenCV REQUIRED CONFIG)

if(OpenCV_FOUND)
    add_library(OpenCV::OpenCV INTERFACE IMPORTED GLOBAL)
    target_include_directories(OpenCV::OpenCV INTERFACE ${OpenCV_INCLUDE_DIRS})

    target_link_libraries(OpenCV::OpenCV INTERFACE ${OpenCV_LIBS})
endif()

find_package(pybind11 REQUIRED CONFIG)
find_package(jsoncpp REQUIRED CONFIG)
find_package(spdlog REQUIRED CONFIG)
find_package(PnpSolver REQUIRED CONFIG)
