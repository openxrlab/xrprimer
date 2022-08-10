#!/bin/bash
cmake -S. -Bbuild/ios  -G Xcode \
-DCMAKE_TOOLCHAIN_FILE=cmake/Modules/Platform/ios.toolchain.cmake \
-D CMAKE_CONFIGURATION_TYPES=Release \
-D BUILD_EXTERNAL=ON \
-D IOS_PLATFORM=OS \
-D IOS_ARCH=arm64 \
-D ENABLE_BITCODE=0 \
-D IOS_DEPLOYMENT_TARGET=12.0 \
-D ENABLE_VISIBILITY=0

if [[ $? == 0 ]]
then
    cmake --build build/ios --target install -j4
else
    echo -e "cmake config error!"
fi
