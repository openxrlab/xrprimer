include(ExternalProject)

externalproject_add(
    ext_jsoncpp
    PREFIX jsoncpp
    GIT_REPOSITORY https://github.com/open-source-parsers/jsoncpp.git
    GIT_TAG 5defb4ed1a4293b8e2bf641e16b156fb9de498cc # 1.9.5
    CMAKE_ARGS ${ExternalProject_CMAKE_ARGS_hidden}
    -DJSONCPP_WITH_TESTS=OFF
    -DJSONCPP_WITH_POST_BUILD_UNITTEST=OFF
    -DJSONCPP_WITH_PKGCONFIG_SUPPORT=OFF
    -DBUILD_OBJECT_LIBS=OFF
    -DCMAKE_CXX_FLAGS="-fPIC"
    -DCMAKE_INSTALL_PREFIX=${STAGED_INSTALL_PREFIX}/jsoncpp
)
