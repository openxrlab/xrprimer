#/bin/env bash

# set -x
cmake -S. -Bbuild -DENABLE_TEST=ON
cmake --build build -j$(nproc)
cd build
pip install gdown
gdown https://docs.google.com/uc?id=1MJx367I2_ezK3vKdV4eJ9d0cBzgs2jtR && tar -xzf xrprimer.tar.gz && rm xrprimer.tar.gz
ln -sfn xrprimer/test test
./bin/test_calibrator
