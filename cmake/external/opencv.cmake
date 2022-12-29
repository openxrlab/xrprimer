# IOS USE framework
if(NOT IOS)

  include(FetchContent)

  FetchContent_Declare(
    opencv
    GIT_REPOSITORY https://github.com/opencv/opencv.git
    GIT_TAG b0dc474160e389b9c9045da5db49d03ae17c6a6b # 4.6.0
    SOURCE_DIR ${CMAKE_SOURCE_DIR}/_ext/opencv BINARY_DIR
    ${CMAKE_SOURCE_DIR}/_deps/opencv)

  FetchContent_GetProperties(opencv)
  if(NOT opencv_POPULATED)
    # Fetch the content using previously declared details
    FetchContent_Populate(opencv)
    # cmake 3.13
    set(CMAKE_POLICY_DEFAULT_CMP0077 NEW)

    set(WITH_1394 OFF)
    set(WITH_ADE OFF)
    set(WITH_EIGEN ON)
    set(WITH_ARAVIS OFF)
    set(WITH_CLP OFF)
    set(WITH_CUDA OFF)
    set(WITH_CUFFT OFF)
    set(WITH_NVCUVID OFF)
    set(WITH_CUBLAS OFF)
    set(WITH_FFMPEG OFF)
    set(WITH_FREETYPE OFF)
    set(WITH_GDAL OFF)
    set(WITH_GDCM OFF)
    set(WITH_GPHOTO2 OFF)
    set(WITH_GSTREAMER OFF)
    set(WITH_GTK OFF)
    set(WITH_GTK_2_X OFF)
    set(WITH_HALIDE OFF)
    set(WITH_HPX OFF)
    set(WITH_IMGCODEC_HDR ON)
    set(WITH_IMGCODEC_PFM ON)
    set(WITH_IMGCODEC_PXM ON)
    set(WITH_IMGCODEC_SUNRASTER ON)
    set(WITH_INF_ENGINE OFF)
    set(WITH_IPP OFF)
    set(WITH_ITT OFF)
    set(BUILD_JASPER ON)
    set(BUILD_JPEG ON)
    set(BULID_PNG ON)
    set(WITH_JASPER ON)
    set(WITH_JPEG ON)
    set(WITH_LAPACK OFF)
    set(WITH_LIBREALSENSE OFF)
    set(WITH_MFX OFF)
    set(WITH_NGRAPH OFF)
    set(WITH_ONNX OFF)
    set(WITH_OPENCL OFF)
    set(WITH_OPENCLAMDBLAS OFF)
    set(WITH_OPENCLAMDFFT OFF)
    set(WITH_OPENCL_SVM OFF)
    set(WITH_OPENEXR OFF)
    set(WITH_OPENGL OFF)
    set(WITH_OPENJPEG ON)
    set(WITH_OPENMP OFF)
    set(WITH_OPENNI OFF)
    set(WITH_OPENNI2 OFF)
    set(WITH_OPENVX OFF)
    set(WITH_PLAIDML OFF)
    set(WITH_PNG ON)
    set(WITH_PROTOBUF OFF)
    set(WITH_PTHREADS_PF OFF)
    set(WITH_PVAPI OFF)
    set(WITH_QT OFF)
    set(WITH_QUIRC OFF)
    set(WITH_TBB OFF)
    set(WITH_TIFF OFF)
    set(WITH_UEYE OFF)
    set(WITH_V4L OFF)
    set(WITH_VA OFF)
    set(WITH_VA_INTEL OFF)
    set(WITH_VTK OFF)
    set(WITH_VULKAN OFF)
    set(WITH_WEBP OFF)
    set(WITH_XIMEA OFF)
    set(WITH_XINE OFF)
    set(BUILD_JAVE OFF)
    set(BUILD_DOCS OFF)
    set(BUILD_opencv_java_bindings_generator OFF)
    set(BUILD_opencv_js_bindings_generator OFF)
    set(BUILD_opencv_objc_bindings_generator OFF)
    set(BUILD_opencv_python_bindings_generator OFF)
    set(BUILD_PERF_TESTS OFF)
    set(BUILD_EXAMPLES OFF)
    set(BUILD_TESTS OFF)
    set(BUILD_opencv_apps OFF)

    add_subdirectory(${opencv_SOURCE_DIR} ${opencv_BINARY_DIR})

    set(OpenCV_INCLUDE_DIRS)
    list(APPEND OpenCV_INCLUDE_DIRS ${OPENCV_CONFIG_FILE_INCLUDE_DIR}/)
    list(APPEND OpenCV_INCLUDE_DIRS
         ${CMAKE_SOURCE_DIR}/_ext/opencv/modules/calib3d/include)
    list(APPEND OpenCV_INCLUDE_DIRS
         ${CMAKE_SOURCE_DIR}/_ext/opencv/modules/core/include)
    list(APPEND OpenCV_INCLUDE_DIRS
         ${CMAKE_SOURCE_DIR}/_ext/opencv/modules/dnn/include)
    list(APPEND OpenCV_INCLUDE_DIRS
         ${CMAKE_SOURCE_DIR}/_ext/opencv/modules/features2d/include)
    list(APPEND OpenCV_INCLUDE_DIRS
         ${CMAKE_SOURCE_DIR}/_ext/opencv/modules/flann/include)
    list(APPEND OpenCV_INCLUDE_DIRS
         ${CMAKE_SOURCE_DIR}/_ext/opencv/modules/gapi/include)
    list(APPEND OpenCV_INCLUDE_DIRS
         ${CMAKE_SOURCE_DIR}/_ext/opencv/modules/highgui/include)
    list(APPEND OpenCV_INCLUDE_DIRS
         ${CMAKE_SOURCE_DIR}/_ext/opencv/modules/imgcodecs/include)
    list(APPEND OpenCV_INCLUDE_DIRS
         ${CMAKE_SOURCE_DIR}/_ext/opencv/modules/imgproc/include)
    list(APPEND OpenCV_INCLUDE_DIRS
         ${CMAKE_SOURCE_DIR}/_ext/opencv/modules/objdetect/include)
    list(APPEND OpenCV_INCLUDE_DIRS
         ${CMAKE_SOURCE_DIR}/_ext/opencv/modules/photo/include)
    list(APPEND OpenCV_INCLUDE_DIRS
         ${CMAKE_SOURCE_DIR}/_ext/opencv/modules/stitching/include)
    list(APPEND OpenCV_INCLUDE_DIRS
         ${CMAKE_SOURCE_DIR}/_ext/opencv/modules/ts/include)
    list(APPEND OpenCV_INCLUDE_DIRS
         ${CMAKE_SOURCE_DIR}/_ext/opencv/modules/video/include)
    list(APPEND OpenCV_INCLUDE_DIRS
         ${CMAKE_SOURCE_DIR}/_ext/opencv/modules/videoio/include)
    include_directories(${OpenCV_INCLUDE_DIRS})

    set(OPENCV_VERSION_FILE
        "${CMAKE_SOURCE_DIR}/_ext/opencv/modules/core/include/opencv2/core/version.hpp"
    )
    file(STRINGS "${OPENCV_VERSION_FILE}" OPENCV_VERSION_PARTS
         REGEX "#define CV_VERSION_[A-Z]+[ ]+")
    string(REGEX REPLACE ".+CV_VERSION_MAJOR[ ]+([0-9]+).*" "\\1"
                         OPENCV_VERSION_MAJOR "${OPENCV_VERSION_PARTS}")
    string(REGEX REPLACE ".+CV_VERSION_MINOR[ ]+([0-9]+).*" "\\1"
                         OPENCV_VERSION_MINOR "${OPENCV_VERSION_PARTS}")
    string(REGEX REPLACE ".+CV_VERSION_REVISION[ ]+([0-9]+).*" "\\1"
                         OPENCV_VERSION_PATCH "${OPENCV_VERSION_PARTS}")
    string(REGEX REPLACE ".+CV_VERSION_STATUS[ ]+\"([^\"]*)\".*" "\\1"
                         OPENCV_VERSION_STATUS "${OPENCV_VERSION_PARTS}")
  endif()

else()
  message(STATUS "using opencv framework")
  if(NOT TARGET Opencv::OpenCV)
    FetchContent_Declare(
      opencv
      URL https://github.com/opencv/opencv/releases/download/4.0.1/opencv-4.0.1-ios-framework.zip
      URL_MD5 35ebe10de1089f6b1e1cce04d822f740
      SOURCE_DIR ${CMAKE_INSTALL_PREFIX}/framework/opencv2.framework)
    FetchContent_GetProperties(opencv)
    if(NOT opencv_POPULATED)
      message(STATUS "Fetching precompiled OpenCV framework")
      FetchContent_Populate(opencv)
      message(STATUS "Fetching precompiled OpenCV framework - done")
      message(STATUS "Configuring OpenCV framework")
      message(STATUS "Configuring OpenCV framework - done")
    endif()
    add_library(OpenCV::OpenCV INTERFACE IMPORTED GLOBAL)
    target_compile_options(
      OpenCV::OpenCV
      INTERFACE -framework opencv2 -F${CMAKE_INSTALL_PREFIX}/framework
                $<$<COMPILE_LANGUAGE:CXX>:-Wno-unused-command-line-argument>)
    target_link_libraries(OpenCV::OpenCV INTERFACE "-framework opencv2")
    target_link_options(OpenCV::OpenCV INTERFACE
                        "-F${CMAKE_INSTALL_PREFIX}/framework")
  endif()

endif()
