if(NOT IOS)
    include(ExternalProject)

    externalproject_add(
        ext_pnpsolver
        PREFIX pnpsolver
        GIT_REPOSITORY https://github.com/GACLove/pnpsolver.git
        GIT_TAG 08182c16424d8730b36fce50168f820fc0733a74
        CMAKE_ARGS -DBUILD_SHARED_LIBS=OFF
                   -DCMAKE_INSTALL_PREFIX=${STAGED_INSTALL_PREFIX}/pnpsolver
                   -DCMAKE_PREFIX_PATH=${STAGED_INSTALL_PREFIX}
    )
    add_dependencies(ext_pnpsolver ext_ceres)
endif()
