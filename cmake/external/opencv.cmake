# IOS USE framework
if(NOT IOS)
    include(FetchContent)

    fetchcontent_declare(
        opencv GIT_REPOSITORY https://github.com/opencv/opencv.git
        GIT_TAG b0dc474160e389b9c9045da5db49d03ae17c6a6b # 4.6.0
    )

    if(NOT opencv_POPULATED)
        fetchcontent_populate(opencv)

        set(WITH_1394 OFF CACHE BOOL "" FORCE) #
        set(WITH_ADE OFF CACHE BOOL "" FORCE)
        set(WITH_ARAVIS OFF CACHE BOOL "" FORCE)
        set(WITH_CLP OFF CACHE BOOL "" FORCE)
        set(WITH_CUDA OFF CACHE BOOL "" FORCE)
        set(WITH_CUFFT OFF CACHE BOOL "" FORCE)
        set(WITH_NVCUVID OFF CACHE BOOL "" FORCE)
        set(WITH_CUBLAS OFF CACHE BOOL "" FORCE)
        set(WITH_FFMPEG OFF CACHE BOOL "" FORCE)
        set(WITH_FREETYPE OFF CACHE BOOL "" FORCE)
        set(WITH_GDAL OFF CACHE BOOL "" FORCE)
        set(WITH_GDCM OFF CACHE BOOL "" FORCE)
        set(WITH_GPHOTO2 OFF CACHE BOOL "" FORCE)
        set(WITH_GSTREAMER OFF CACHE BOOL "" FORCE)
        set(WITH_GTK OFF CACHE BOOL "" FORCE)
        set(WITH_GTK_2_X OFF CACHE BOOL "" FORCE)
        set(WITH_HALIDE OFF CACHE BOOL "" FORCE)
        set(WITH_HPX OFF CACHE BOOL "" FORCE)
        set(WITH_INF_ENGINE OFF CACHE BOOL "" FORCE)
        set(WITH_IPP OFF CACHE BOOL "" FORCE)
        set(WITH_ITT OFF CACHE BOOL "" FORCE)
        set(WITH_QUIRC OFF CACHE BOOL "" FORCE)

        set(WITH_EIGEN ON CACHE BOOL "" FORCE)
        set(WITH_IMGCODEC_HDR ON CACHE BOOL "" FORCE)
        set(WITH_IMGCODEC_PFM ON CACHE BOOL "" FORCE)
        set(WITH_IMGCODEC_PXM ON CACHE BOOL "" FORCE)
        set(WITH_IMGCODEC_SUNRASTER ON CACHE BOOL "" FORCE)
        set(WITH_JASPER ON CACHE BOOL "" FORCE)
        set(WITH_JPEG ON CACHE BOOL "" FORCE)

        set(BUILD_PROTOBUF OFF CACHE BOOL "" FORCE)
        set(BUILD_opencv_apps OFF CACHE BOOL "" FORCE)

        set(BULID_PNG ON CACHE BOOL "" FORCE)

        set(OPENCV_SKIP_PYTHON_WARNING ON CACHE BOOL "" FORCE)

        set(BUILD_LIST
            "calib3d,core,features2d,flann,highgui,imgcodecs,imgproc,video,videoio"
            CACHE STRING "" FORCE
        )

        add_subdirectory(${opencv_SOURCE_DIR} ${opencv_BINARY_DIR})

        add_library(OpenCV::OpenCV INTERFACE IMPORTED GLOBAL)

        string(REPLACE "," ";" _CV_MODULE_LIST ${BUILD_LIST})

        foreach(_module ${_CV_MODULE_LIST})
            list(APPEND cv_includes_list
                 ${OPENCV_MODULE_opencv_${_module}_LOCATION}/include
            )
            list(APPEND cv_library_list opencv_${_module})
        endforeach()

        target_include_directories(
            OpenCV::OpenCV INTERFACE ${OPENCV_CONFIG_FILE_INCLUDE_DIR}
                                     ${cv_includes_list}
        )
        target_link_libraries(OpenCV::OpenCV INTERFACE ${cv_library_list})
    endif()

else()
    message(STATUS "using opencv framework")

    if(NOT TARGET Opencv::OpenCV)
        fetchcontent_declare(
            opencv
            URL https://github.com/opencv/opencv/releases/download/4.0.1/opencv-4.0.1-ios-framework.zip
            URL_MD5 35ebe10de1089f6b1e1cce04d822f740
            SOURCE_DIR ${CMAKE_INSTALL_PREFIX}/framework/opencv2.framework
        )
        fetchcontent_getproperties(opencv)

        if(NOT opencv_POPULATED)
            message(STATUS "Fetching precompiled OpenCV framework")
            fetchcontent_populate(opencv)
            message(STATUS "Fetching precompiled OpenCV framework - done")
            message(STATUS "Configuring OpenCV framework")
            message(STATUS "Configuring OpenCV framework - done")
        endif()

        add_library(OpenCV::OpenCV INTERFACE IMPORTED GLOBAL)
        target_compile_options(
            OpenCV::OpenCV
            INTERFACE
                -framework opencv2 -F${CMAKE_INSTALL_PREFIX}/framework
                $<$<COMPILE_LANGUAGE:CXX>:-Wno-unused-command-line-argument>
        )
        target_link_libraries(OpenCV::OpenCV INTERFACE "-framework opencv2")
        target_link_options(
            OpenCV::OpenCV INTERFACE "-F${CMAKE_INSTALL_PREFIX}/framework"
        )
    endif()
endif()
