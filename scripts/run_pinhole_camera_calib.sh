#/bin/env bash

# set -x
cmake -S. -Bbuild -DENABLE_TEST=ON
cmake --build build -j$(nproc)
cd build
wget -q https://drive.google.com/file/d/1MJx367I2_ezK3vKdV4eJ9d0cBzgs2jtR/view?usp=sharing && tar -xzf xrprimer.tar.gz && rm xrprimer.tar.gz
ln -sfn xrprimer/test test
./bin/test_calibrator
