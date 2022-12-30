include(FetchContent)

fetchcontent_declare(
    spdlog GIT_REPOSITORY https://github.com/gabime/spdlog.git
    GIT_TAG 5b4c4f3f770acbd25400d866f3fc2fdf669d5b7e # 1.9.1
)

fetchcontent_getproperties(spdlog)

if(NOT spdlog_POPULATED)
    fetchcontent_populate(spdlog)

    set(SPDLOG_INSTALL ON CACHE BOOL "" FORCE)

    add_subdirectory(${spdlog_SOURCE_DIR} ${spdlog_BINARY_DIR})
endif()
