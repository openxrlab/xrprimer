#/bin/env bash

# set -x
cmake -S. -Bbuild -DENABLE_TEST=ON
cmake --build build -j$(nproc)
cd build
wget -q https://openxrlab-share.oss-cn-hongkong.aliyuncs.com/xrprimer/xrprimer.tar.gz && tar -xzf xrprimer.tar.gz && rm xrprimer.tar.gz
ln -sfn xrprimer/test test
./bin/test_calibrator
