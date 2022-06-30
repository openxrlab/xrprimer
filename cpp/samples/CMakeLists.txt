
cmake_minimum_required(VERSION 3.14)

project(sample)

#set XRPrimer_DIR pointer to XRPrimerConfig.cmake directory
set(XRPrimer_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../install/lib/cmake")
find_package(XRPrimer REQUIRED)

add_executable(sample sample.cpp)
target_link_libraries(sample XRPrimer::xrprimer)
