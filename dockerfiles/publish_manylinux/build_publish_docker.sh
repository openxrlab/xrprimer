# build according to Dockerfile

TAG="openxrlab/xrprimer_ci:manylinux2010_x86_64_torch180_mmcv150"
docker build -t $TAG -f dockerfiles/publish/Dockerfile --progress=plain .
