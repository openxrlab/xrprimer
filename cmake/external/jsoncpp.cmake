include(FetchContent)

FetchContent_Declare(
  jsoncpp
  GIT_REPOSITORY https://github.com/open-source-parsers/jsoncpp.git
  GIT_TAG 5defb4ed1a4293b8e2bf641e16b156fb9de498cc # 1.9.5
  SOURCE_DIR ${CMAKE_SOURCE_DIR}/_ext/jsoncpp BINARY_DIR
  ${CMAKE_SOURCE_DIR}/_deps/jsoncpp)

FetchContent_GetProperties(jsoncpp)
if(NOT jsoncpp_POPULATED)
  # Fetch the content using previously declared details
  set(JSONCPP_WITH_TESTS
      OFF
      CACHE BOOL "" FORCE)
  set(JSONCPP_WITH_POST_BUILD_UNITTEST
      OFF
      CACHE BOOL "" FORCE)
  set(JSONCPP_WITH_PKGCONFIG_SUPPORT
      OFF
      CACHE BOOL "" FORCE)
  set(BUILD_OBJECT_LIBS
      OFF
      CACHE BOOL "" FORCE)

  FetchContent_Populate(jsoncpp)
  add_subdirectory(${jsoncpp_SOURCE_DIR} ${jsoncpp_BINARY_DIR})
  target_compile_options(jsoncpp_static PRIVATE -fPIC)
  set_target_properties(jsoncpp_static PROPERTIES CXX_VISIBILITY_PRESET hidden
                                                  VISIBILITY_INLINES_HIDDEN ON)
endif()
