cmake_minimum_required(VERSION 3.14)

project(sample)

if(NOT XRPrimer_DIR)
    # set XRPrimer_DIR pointer to XRPrimerConfig.cmake directory
    list(APPEND CMAKE_PREFIX_PATH "${CMAKE_CURRENT_SOURCE_DIR}/../../install/")
    message(
        STATUS
            "**[XRPrimer]** XRPrimer_DIR default path: ${CMAKE_CURRENT_SOURCE_DIR}/../../install/"
    )
endif()

find_package(XRPrimer REQUIRED)

add_executable(sample sample.cpp)
target_link_libraries(sample XRPrimer::xrprimer)
