# Installation (CPP)

<!-- TOC -->

- [Installation (CPP)](#installation-cpp)
    - [Requirements](#requirements)
    - [Compilation](#compilation)
      - [Compilation options](#compilation-options)
      - [Compilation on iOS](#compilation-on-ios)
    - [Test](#test)
    - [How to link in C++ projects](#how-to-link-in-c-projects)

<!-- TOC -->

### Requirements
+ C++14 or later compiler
+ GCC 7.5+
+ CMake 3.15+
+ LAPACK & BLAS
    1. If using conda, `conda install -c conda-forge lapack`
    2. If sudo is available, `apt update & apt -y install libatlas-base-dev`

Optional:
+ [Conan](https://docs.conan.io/en/1.46/installation.html) (for using pre-built 3rd-party libraries)
    ``` bash
    # 0. install conan
    pip install conan

    # 1. first run
    conan profile new --detect --force default
    conan profile update settings.compiler.libcxx=libstdc++11 default

    # 2. add conan artifactory
    conan remote add openxrlab http://conan.openxrlab.org.cn/artifactory/api/conan/openxrlab

    # 3. check
    conan remote list
    ```

### Compilation

```bash
git clone https://github.com/openxrlab/xrprimer.git
cd xrprimer/

# build and install deps
cmake -S. -Bbuild_deps -D3RT_FROM_LOCAL=ON
cmake --build build_deps -j4

# compiler xrprimer
cmake -S. -Bbuild [Compilation options]
cmake --build build --target install -j4
```

It is currently tested on Linux and iOS. Ideally it can be also compiled on macOS or Windows.

#### Compilation options

> Get external dependencies

- `3RT_FROM_LOCAL` Dependencies library will be built or find in local host. default: `OFF`
- `3RT_FROM_CONAN` Dependencies library will be download from openxrlab conan remote. default: `OFF`

> Config xrprimer

- `ENABLE_TEST` Enable unit test. default: `OFF`
- `PYTHON_BINDING` Enable Python binding. default: `ON`

```bash
#1. First run, get external dependencies, will install external deps to 3rdparty
cmake -S. -Bbuild_deps <-D3RT_FROM_LOCAL=ON/-D3RT_FROM_CONAN=ON>
cmake -S. -Bbuild_deps -D3RT_FROM_LOCAL=ON
cmake --build build_deps

#2. build xrprimer
cmake -S. -Bbuild -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=install
cmake --build build --target install

```

#### Compilation on iOS

Refer to [build_ios.sh](../../../scripts/build_ios.sh) for more details.

### Test

CPP library

```bash
# compile (Skip the following two lines if it has been compiled)
cmake -S. -Bbuild -DCMAKE_BUILD_TYPE=Release -DENABLE_TEST=ON
cmake --build build -j4

# run test
cd build
wget -q https://openxrlab-share-mainland.oss-cn-hangzhou.aliyuncs.com/xrprimer/xrprimer.tar.gz && tar -xzf xrprimer.tar.gz && rm xrprimer.tar.gz
ln -sfn xrprimer/test test
./bin/test_calibrator
```

Python library

```bash
# compile (Skip the following two lines if it has been compiled)
cmake -S. -Bbuild -DCMAKE_BUILD_TYPE=Release -DENABLE_TEST=ON
cmake --build build -j4

# run test
cd build
wget -q https://openxrlab-share-mainland.oss-cn-hangzhou.aliyuncs.com/xrprimer/xrprimer.tar.gz && tar -xzf xrprimer.tar.gz && rm xrprimer.tar.gz
PYTHONPATH=./lib/ python ../cpp/tests/test_multi_camera_calibrator.py
```

### How to link in C++ projects

see [cpp sample](../../../cpp/samples)

```js
cmake_minimum_required(VERSION 3.16)

project(sample)

# set path for find XRPrimer package (config mode)
set(XRPrimer_DIR "<package_path>/lib/cmake")
find_package(XRPrimer REQUIRED)

add_executable(sample sample.cpp)

target_link_libraries(sample XRPrimer::xrprimer)
```
