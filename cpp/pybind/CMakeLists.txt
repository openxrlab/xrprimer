find_package(Python3 COMPONENTS Interpreter Development)

find_package(pybind11 REQUIRED CONFIG)

if(Python3_FOUND)
    set(PYTHON_EXECUTABLE
        ${Python3_EXECUTABLE}
        CACHE STRING
              "Deprecated path to the Python executable (for 3rdparty only)"
              FORCE
    )
endif()

if(NOT Python3_EXECUTABLE)
    message(FATAL_ERROR "Python 3 not found in top level file")
endif()

set(PYTHON_VERSION "${Python3_VERSION_MAJOR}.${Python3_VERSION_MINOR}")

pybind11_add_module(xrprimer_cpp)
target_sources(
    xrprimer_cpp PRIVATE xrprimer_pybind.cpp data_structure/camera.cpp
                         data_structure/pose.cpp common/version.cpp
)

set(EXTERNAL_MODULES XRPrimer::xrprimer)

if(NOT BUILD_ONLY_BASE)
    set(EXTERNAL_MODULES ${EXTERNAL_MODULES} opencv_imgcodecs opencv_calib3d
                         opencv_core
    )
else()
    target_compile_definitions(xrprimer_cpp PRIVATE XRPRIMER_BUILD_BASE)
endif()

add_subdirectory(calibration)
add_subdirectory(ops)

target_link_libraries(xrprimer_cpp PUBLIC ${EXTERNAL_MODULES})
target_include_directories(
    xrprimer_cpp PUBLIC $<BUILD_INTERFACE:${CMAKE_SOURCE_DIR}/cpp/>
                        $<INSTALL_INTERFACE:include/>
)
set_target_properties(
    xrprimer_cpp PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib
)
