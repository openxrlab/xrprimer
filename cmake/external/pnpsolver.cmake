#
# Pnp solver, ios not support
#

if(NOT IOS)
    include(FetchContent)

    fetchcontent_declare(
        pnpsolver GIT_REPOSITORY https://github.com/xxlxsyhl/pnpsolver.git
        GIT_TAG 8710099931eb2ab8112b2a17800d638df3ec8c0a
    )

    fetchcontent_getproperties(pnpsolver)

    if(NOT pnpsolver_POPULATED)
        fetchcontent_populate(pnpsolver)

        set(BUILD_SHARED_LIBS OFF CACHE BOOL "" FORCE)

        add_subdirectory(${pnpsolver_SOURCE_DIR} ${pnpsolver_BINARY_DIR})
    endif()

else()
    message(STATUS "pnpsolver NOT support ios")
endif()
