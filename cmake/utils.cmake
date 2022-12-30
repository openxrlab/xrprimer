# source_group_by_path("${CMAKE_CURRENT_SOURCE_DIR}/src"
# "\\\\.h$|\\\\.inl$|\\\\.cpp$|\\\\.c$|\\\\.ui$|\\\\.qrc$" "Source" ${sources})
# source_group_by_path("${CMAKE_CURRENT_SOURCE_DIR}/include" "\\\\.h$" "Header"
# ${headers})
function(source_group_by_path PARENT_PATH REGEX GROUP)
    foreach(FILENAME ${ARGN})
        get_filename_component(FILEPATH "${FILENAME}" REALPATH)
        file(RELATIVE_PATH FILEPATH ${PARENT_PATH} ${FILEPATH})
        get_filename_component(FILEPATH "${FILEPATH}" DIRECTORY)
        string(REPLACE "/" "\\" FILEPATH "${FILEPATH}")
        source_group(
            "${GROUP}\\${FILEPATH}" REGULAR_EXPRESSION "${REGEX}"
            FILES ${FILENAME}
        )
    endforeach()
endfunction(source_group_by_path)

function(get_revison_from_vcs repo_path revision)
    # find_package(Git QUIET REQUIRED)
    set(abbrev 0)
    if(${ARGC} GREATER 1)
        if(${ARGV2})
            set(abbrev ${ARGV2})
        endif()
    endif()
    execute_process(
        COMMAND git describe --match=NeVeRmAtCh --always --abbrev=${abbrev}
                --dirty WORKING_DIRECTORY "${repo_path}" OUTPUT_VARIABLE rev
        ERROR_QUIET OUTPUT_STRIP_TRAILING_WHITESPACE
    )
    set(${revision} ${rev} PARENT_SCOPE)
endfunction()

function(get_commit_date_from_vcs repo_path commit_date)
    set(date_pattern "%Y-%m-%d %H:%M:%S")
    execute_process(
        COMMAND git --no-pager log --pretty=format:%cd
                --date=format:${date_pattern} HEAD -1
        WORKING_DIRECTORY "${repo_path}"
        OUTPUT_VARIABLE date
        ERROR_QUIET OUTPUT_STRIP_TRAILING_WHITESPACE
    )
    set(${commit_date} ${date} PARENT_SCOPE)
endfunction()
