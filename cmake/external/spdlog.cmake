include(FetchContent)

FetchContent_Declare(
  spdlog
  GIT_REPOSITORY https://github.com/gabime/spdlog.git
  GIT_TAG 5b4c4f3f770acbd25400d866f3fc2fdf669d5b7e # 1.9.1
  SOURCE_DIR ${CMAKE_SOURCE_DIR}/_ext/spdlog BINARY_DIR
  ${CMAKE_SOURCE_DIR}/_deps/spdlog)

FetchContent_GetProperties(spdlog)

if(NOT spdlog_POPULATED)
  # Fetch the content using previously declared details
  FetchContent_Populate(spdlog)
  set(CMAKE_POLICY_DEFAULT_CMP0077 NEW)
  set(SPDLOG_INSTALL
      ON
      CACHE BOOL "" FORCE)
  execute_process(COMMAND git reset --hard
                  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/_ext/spdlog)
  add_subdirectory(${spdlog_SOURCE_DIR} ${spdlog_BINARY_DIR})
endif()
