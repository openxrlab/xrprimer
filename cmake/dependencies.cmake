#
# find external project and embbed to main project
#

if(NOT IOS)
    find_package(Eigen3 REQUIRED CONFIG)

    # find_package(Ceres REQUIRED CONFIG)

    # if(NOT TARGET Ceres::ceres)
    # add_library(Ceres::ceres INTERFACE IMPORTED)
    # set_target_properties(
    # Ceres::ceres PROPERTIES INTERFACE_LINK_LIBRARIES ceres
    # )
    # endif()

    # find_package(OpenCV REQUIRED CONFIG)

    # if(OpenCV_FOUND)
    # add_library(OpenCV::OpenCV INTERFACE IMPORTED GLOBAL)
    # target_include_directories(
    # OpenCV::OpenCV INTERFACE ${OpenCV_INCLUDE_DIRS}
    # )
    # target_link_libraries(OpenCV::OpenCV INTERFACE ${OpenCV_LIBS})
    # endif()
    find_package(pybind11 REQUIRED CONFIG)
    find_package(jsoncpp REQUIRED CONFIG)
    find_package(spdlog REQUIRED CONFIG)

# find_package(PnpSolver REQUIRED CONFIG)
else()
    # 指定opencv_framework_path
    if(EXISTS ${xrprimer_framework_path})
        add_library(OpenCV::OpenCV INTERFACE IMPORTED GLOBAL)
        target_compile_options(
            OpenCV::OpenCV INTERFACE -F${xrprimer_framework_path}
        )
        target_link_options(OpenCV::OpenCV INTERFACE -framework opencv2)
    else()
        message(
            FATAL_ERROR
            "[XRPrimer] can not found opencv2 framework on IOS, please check xrprimer_framework_path ${xrprimer_framework_path}"
        )
    endif()
endif()
