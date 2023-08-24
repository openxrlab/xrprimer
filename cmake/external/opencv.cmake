include(ExternalProject)

if(NOT IOS)
    set(OPENCV_URL https://github.com/opencv/opencv/archive/refs/tags/4.6.0.zip)
    message(STATUS "opencv url: ${OPENCV_URL}")
    externalproject_add(
        ext_opencv
        PREFIX opencv
        URL ${OPENCV_URL}
        URL_HASH
        SHA256=158db5813a891c7eda8644259fc1dbd76b21bd1ffb9854a8b4b8115a4ceec359
        CMAKE_ARGS
        ${ExternalProject_CMAKE_ARGS_hidden}
        -DBUILD_ZLIB=ON
        -DWITH_1394=OFF
        -DWITH_ADE=OFF
        -DWITH_ARAVIS=OFF
        -DWITH_CLP=OFF
        -DWITH_CUDA=OFF
        -DWITH_CUFFT=OFF
        -DWITH_NVCUVID=OFF
        -DWITH_CUBLAS=OFF
        -DWITH_FFMPEG=OFF
        -DWITH_FREETYPE=OFF
        -DWITH_GDAL=OFF
        -DWITH_GDCM=OFF
        -DWITH_GPHOTO2=OFF
        -DWITH_GSTREAMER=OFF
        -DWITH_GTK=OFF
        -DWITH_GTK_2_X=OFF
        -DWITH_HALIDE=OFF
        -DWITH_HPX=OFF
        -DWITH_INF_ENGINE=OFF
        -DWITH_IPP=OFF
        -DWITH_ITT=OFF
        -DWITH_QUIRC=OFF
        -DWITH_EIGEN=ON
        -DWITH_IMGCODEC_HDR=ON
        -DWITH_IMGCODEC_PFM=ON
        -DWITH_IMGCODEC_PXM=ON
        -DWITH_IMGCODEC_SUNRASTER=ON
        -DWITH_JASPER=ON
        -DWITH_JPEG=ON
        -DBUILD_PROTOBUF=OFF
        -DBUILD_opencv_apps=OFF
        -DBULID_PNG=ON
        -DOPENCV_SKIP_PYTHON_WARNING=ON
        -DCMAKE_INSTALL_PREFIX=${STAGED_INSTALL_PREFIX}/opencv
        -DBUILD_LIST="core,calib3d,features2d,flann,highgui,imgcodecs,imgproc,video,videoio"
        -DCMAKE_PREFIX_PATH=${STAGED_INSTALL_PREFIX}/eigen3
    )

    add_dependencies(ext_opencv ext_eigen)
else()
    # iOS use framework
    set(OPENCV_URL
        https://github.com/opencv/opencv/releases/download/4.6.0/opencv-4.6.0-ios-framework.zip
    )
    message(STATUS "opencv url: ${OPENCV_URL}")

    # only download
    externalproject_add(
        ext_opencv
        PREFIX opencv
        URL ${OPENCV_URL}
        SOURCE_DIR "${STAGED_INSTALL_PREFIX}/opencv2.framework"
        CONFIGURE_COMMAND ""
        BUILD_COMMAND ""
        INSTALL_COMMAND ""
    )
endif()
