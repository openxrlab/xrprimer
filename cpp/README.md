# XRPrimer library (CPP)

## Requirements
+ C++11 compiler
+ CMake 3.15+

## Build from source

On Linux or Macos

```bash

# Maybe need proxy for github clone
# export http_proxy=http://proxy.sensetime.com:3128/
# export https_proxy=http://proxy.sensetime.com:3128/
# export HTTP_PROXY=http://proxy.sensetime.com:3128/
# export HTTPS_PROXY=http://proxy.sensetime.com:3128/

cmake -S. -Bbuild [Compilation options]
cmake --build . --target install -j4
```

## Compilation options

+ `ENABLE_TEST` Enable unit test. default: `OFF`
+ `PYTHON_BINDING` Enable Python binding. default: `ON`


## Uint Test

CPP

```bash
# compiler
cmake -S. -Bbuild -DENABLE_TEST=ON
cmake --build . --target -j4
#run test
cd build
wget -q http://10.4.11.59:18080/resources/XRlab/xrprimer.tar.gz && tar -xzf xrprimer.tar.gz && rm xrprimer.tar.gz
ln -sfn xrprimer/test test
./bin/ut_test
```

Python
```bash
cmake -S. -Bbuild
cd build
wget -q http://10.4.11.59:18080/resources/XRlab/xrprimer.tar.gz && tar -xzf xrprimer.tar.gz && rm xrprimer.tar.gz
PYTHONPATH=./lib/ python ../cpp/tests/test_multi_camera_calibrator.py
```

