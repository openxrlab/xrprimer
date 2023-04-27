#!/bin/bash
PY_VER=3.8
MMCV_VER=1.7.0
TORCH_VER=1.12.1
TORCHV_VER=0.13.1
PY_VER_DIGIT=${PY_VER//./}
MMCV_VER_DIGIT=${MMCV_VER//./}
TORCH_VER_DIGIT=${TORCH_VER//./}
TAG="openxrlab/xrprimer_runtime:ubuntu1804_x64_gcc7_py${PY_VER_DIGIT}_torch${TORCH_VER_DIGIT}_mmcv${MMCV_VER_DIGIT}"
echo "tag to build: $TAG"
BUILD_ARGS="--build-arg PY_VER=${PY_VER} --build-arg MMCV_VER=${MMCV_VER} --build-arg TORCH_VER=${TORCH_VER} --build-arg TORCHV_VER=${TORCHV_VER}"
# build according to Dockerfile
docker build -t $TAG -f dockerfiles/runtime_ubt18/Dockerfile $BUILD_ARGS --progress=plain .
