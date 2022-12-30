#
if(IOS)
    message(STATUS "[XRPrimer] Disable pybind11 on ios")
    return()
endif()

include(FetchContent)

fetchcontent_declare(
    pybind11
    URL https://github.com/pybind/pybind11/archive/refs/tags/v2.6.2.tar.gz
    URL_HASH
        SHA256=8ff2fff22df038f5cd02cea8af56622bc67f5b64534f1b83b9f133b8366acff2
)

if(NOT pybind11_POPULATED)
    fetchcontent_populate(pybind11)

    add_subdirectory(${pybind11_SOURCE_DIR} ${pybind11_BINARY_DIR})
endif()
