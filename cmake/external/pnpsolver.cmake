include(FetchContent)

FetchContent_Declare(
    pnpsolver
    GIT_REPOSITORY https://github.com/xxlxsyhl/pnpsolver.git
    GIT_TAG        6835de05bc2310b6e507d4463f7ac86f99a17628
    SOURCE_DIR     ${CMAKE_SOURCE_DIR}/_ext/pnpsolver
    BINARY_DIR     ${CMAKE_SOURCE_DIR}/_deps/pnpsolver
)

FetchContent_GetProperties(pnpsolver)
if(NOT pnpsolver_POPULATED)
    # Fetch the content using previously declared details
    FetchContent_Populate(pnpsolver)
    set(CMAKE_POLICY_DEFAULT_CMP0077 NEW)
    execute_process(COMMAND git reset --hard WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/_ext/pnpsolver)
    add_subdirectory(${pnpsolver_SOURCE_DIR} ${pnpsolver_BINARY_DIR})
endif()
