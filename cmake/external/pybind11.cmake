include(FetchContent)

FetchContent_Declare(
    pybind11
    URL https://github.com/pybind/pybind11/archive/refs/tags/v2.6.2.tar.gz
    URL_HASH SHA256=8ff2fff22df038f5cd02cea8af56622bc67f5b64534f1b83b9f133b8366acff2
    SOURCE_DIR     ${CMAKE_SOURCE_DIR}/_ext/pybind11
    BINARY_DIR     ${CMAKE_SOURCE_DIR}/_deps/pybind11
)

FetchContent_MakeAvailable(pybind11)
