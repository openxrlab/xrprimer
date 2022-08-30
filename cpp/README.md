# XRPrimer library (CPP)


## Quick Start

### Requirements
+ C++14 or later compiler
+ GCC 7.5+
+ CMake 3.15+

Optional:
+ [Conan](https://docs.conan.io/en/1.46/installation.html) (for using pre-built 3rd-party libraries)
    ``` bash
    # config
    # 1. first run
    conan profile new --detect --force default
    conan profile update settings.compiler.libcxx=libstdc++11 default

    # 2. add conan registry
    conan remote add xrlab http://conan.kestrel.sensetime.com/artifactory/api/conan/xrlab

    ```

### Build

Theoretically it can compile on Linux or Macos or Windows, Currently tested on Linux

```bash
git clone https://github.com/openxrlab/xrprimer.git
cd xrprimer/

cmake -S. -Bbuild [Compilation options]
cmake --build build --target install -j4
```

#### Compilation options

+ `ENABLE_TEST` Enable unit test. default: `OFF`
+ `PYTHON_BINDING` Enable Python binding. default: `ON`
+ `BUILD_EXTERNAL` Enable build external. default: `OFF`, download deps libraries from conan.


```bash
# build external from source
cmake -S. -Bbuild -DBUILD_EXTERNAL=ON -DCMAKE_BUILD_TYPE=Release
cmake --build build --target install

# use conan for external
cmake -S. -Bbuild -DCMAKE_BUILD_TYPE=Release
cmake --build build --target install
```


### Test

CPP library

```bash
# compiler
cmake -S. -Bbuild -DCMAKE_BUILD_TYPE=Release -DENABLE_TEST=ON
cmake --build build -j4
#run test
cd build
wget -q https://openxrlab-share.oss-cn-hongkong.aliyuncs.com/xrprimer/xrprimer.tar.gz && tar -xzf xrprimer.tar.gz && rm xrprimer.tar.gz
ln -sfn xrprimer/test test
./bin/test_calibrator
```

Python library

```bash
cmake -S. -Bbuild -DCMAKE_BUILD_TYPE=Release
cmake --build build -j4
cd build
wget -q https://openxrlab-share.oss-cn-hongkong.aliyuncs.com/xrprimer/xrprimer.tar.gz && tar -xzf xrprimer.tar.gz && rm xrprimer.tar.gz
PYTHONPATH=./cpp/pybind/ python ../cpp/tests/test_multi_camera_calibrator.py
```

## How use in C++ projects

see [sample](samples)

```js
cmake_minimum_required(VERSION 3.16)

project(sample)

# set path for find XRPrimer package (config mode)
set(XRPrimer_DIR "<package_path>/lib/cmake")
find_package(XRPrimer REQUIRED)

add_executable(sample sample.cpp)

target_link_libraries(sample XRPrimer::xrprimer)
```
