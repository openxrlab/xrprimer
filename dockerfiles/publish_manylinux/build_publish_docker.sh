# build according to Dockerfile

TAG="openxrlab/xrprimer_ci:manylinux2014_x86_64_torch1110_mmcv170"
docker build -t $TAG -f dockerfiles/publish_manylinux/Dockerfile --progress=plain .
