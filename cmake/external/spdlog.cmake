include(ExternalProject)

externalproject_add(
    ext_spdlog
    PREFIX spdlog
    GIT_REPOSITORY https://github.com/gabime/spdlog.git
    GIT_TAG 5b4c4f3f770acbd25400d866f3fc2fdf669d5b7e # 1.9.1
    CMAKE_ARGS -DSPDLOG_INSTALL=ON ${ExternalProject_CMAKE_ARGS_hidden}
               -DCMAKE_INSTALL_PREFIX=${STAGED_INSTALL_PREFIX}/spdlog
)
