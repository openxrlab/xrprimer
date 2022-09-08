# XRPrimer

<div align="left">

[![actions](https://github.com/openxrlab/xrprimer/workflows/build/badge.svg)](https://github.com/openxrlab/xrprimer/actions)
[![codecov](https://codecov.io/gh/openxrlab/xrprimer/branch/main/graph/badge.svg)](https://codecov.io/gh/openxrlab/xrprimer)
[![PyPI](https://img.shields.io/pypi/v/xrprimer)](https://pypi.org/project/xrprimer/)
[![LICENSE](https://img.shields.io/github/license/openxrlab/xrprimer.svg)](https://github.com/openxrlab/xrprimer/blob/main/LICENSE)

</div>

## Introduction

English | [简体中文](README_CN.md)

XRPrimer is a fundational library for XR-related algorithms.
The XRPrimer provides reusable data structures, efficient operaters and extensible interfaces both in C++ and Python.

### Major Features

- [x] Various camera models and conversion tools (Pinhole, Fisheye, Omni etc.)
- [x] Basic 3D operations (Triangulation, Projection etc.)
- [x] Multi-camera extrinsic calibration tools
- [ ] Rendering and visualization tools

### Operation Systems

It currently supports the following systems.

- Linux
- iOS

## Installation

### Python

If using xrprimer in a Python project, it can be installed by:

```bash
pip install xrprimer
```

If you want to use the latest updates of xrprimer, please refer to [Python Installation](docs/en/installation/python.md) for detailed installation.

### C++

If using xrprimer in a C++ project, please refer to [C++ Installation](docs/en/installation/cpp.md) for compilation and test.


## Getting started

### Use XRPrimer in Python projects

The below code is supposed to run successfully upon you finish the installation.

```bash
python -c "import xrprimer; print(xrprimer.__version__)"
```

### Use XRPrimer in C++ projects

An example is given below to show how to link xrprimer in C++ projects. More details can be found [here](docs/en/installation/cpp.md#how-to-link-in-c-projects).

```js
cmake_minimum_required(VERSION 3.16)

project(sample)

# set path for find XRPrimer package (config mode)
set(XRPrimer_DIR "<package_path>/lib/cmake")
find_package(XRPrimer REQUIRED)

add_executable(sample sample.cpp)

target_link_libraries(sample XRPrimer::xrprimer)
```

## FAQ

If you face some installation issues, you may first refer to this [Frequently Asked Questions](docs/en/faq.md).


## License

The license of our codebase is [Apache-2.0](LICENSE). Note that this license only applies to code in our library, the dependencies of which are separate and individually licensed. We would like to pay tribute to open-source implementations to which we rely on. Please be aware that using the content of dependencies may affect the license of our codebase.

## Citation

If you find this project useful in your research, please consider cite:

```bibtex
@misc{xrprimer,
    title={OpenXRLab Foundational Library for XR-related Algorithms},
    author={XRPrimer Contributors},
    howpublished = {\url{https://github.com/openxrlab/xrprimer}},
    year={2022}
}
```

## Contributing

We appreciate all contributions to improve XRPrimer. Please refer to [CONTRIBUTING.md](.github/CONTRIBUTING.md) for the contributing guideline.

## Acknowledgement

XRPrimer is an open source project that is contributed by researchers and engineers from both the academia and the industry.
We appreciate all the contributors who implement their methods or add new features, as well as users who give valuable feedbacks.
We wish that the toolbox and benchmark could serve the growing research community by providing a flexible toolkit to reimplement existing methods and develop their own new models.

## Projects in OpenXRLab

- [XRPrimer](https://github.com/openxrlab/xrprimer): OpenXRLab foundational library for XR-related algorithms.
- [XRSLAM](https://github.com/openxrlab/xrslam): OpenXRLab Visual-inertial SLAM Toolbox and Benchmark.
- [XRSfM](https://github.com/openxrlab/xrsfm): OpenXRLab Structure-from-Motion Toolbox and Benchmark.
- [XRLocalization](https://github.com/openxrlab/xrlocalization): OpenXRLab Visual Localization Toolbox and Server.
- [XRMoCap](https://github.com/openxrlab/xrmocap): OpenXRLab Multi-view Motion Capture Toolbox and Benchmark.
- [XRMoGen](https://github.com/openxrlab/xrmogen): OpenXRLab Human Motion Generation Toolbox and Benchmark.
- [XRNeRF](https://github.com/openxrlab/xrnerf): OpenXRLab Neural Radiance Field (NeRF) Toolbox and Benchmark.
