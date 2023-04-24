#!/bin/bash
MMCV_VER=1.7.0
TORCH_VER=1.11.0
TORCHV_VER=0.12.0
MMCV_VER_DIGIT=${MMCV_VER//./}
TORCH_VER_DIGIT=${TORCH_VER//./}
TAG="openxrlab/xrprimer_ci:manylinux2014_x86_64_torch${TORCH_VER_DIGIT}_mmcv${MMCV_VER_DIGIT}"
echo "tag to build: $TAG"
BUILD_ARGS="--build-arg MMCV_VER=${MMCV_VER} --build-arg TORCH_VER=${TORCH_VER} --build-arg TORCHV_VER=${TORCHV_VER}"
# build according to Dockerfile
docker build -t $TAG -f dockerfiles/publish_manylinux/Dockerfile $BUILD_ARGS --progress=plain .
