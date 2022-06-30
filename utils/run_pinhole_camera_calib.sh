#/bin/env bash

# set -x
# maybe use proxy for github clone (sensetime)
# export HTTPS_PROXY=http://172.16.1.135:3128
cmake -S. -Bbuild -DENABLE_TEST=ON
cmake --build build -j$(nproc)
cd build
wget -q http://10.4.11.59:18080/resources/XRlab/xrprimer.tar.gz && tar -xzf xrprimer.tar.gz && rm xrprimer.tar.gz
ln -sfn xrprimer/test test
./bin/test_calibrator
