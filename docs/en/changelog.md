# Changelog

### v0.6.0 (01/09/2022/)

**Highlights**

- Support iOS and Linux compilation
- Support installation via pypi, ranging from python 3.6 to 3.10
- Support various camera models (Pinhole, Fisheye, Omni etc.)
- Support basic 3D operations (Triangulator, Projector etc.)
- Support Multi-camera extrinsic calibration tools

**New Features**

- Add pybind to create Python bindings of C++ data structures and switch python backend to C++ code
- Add camera convention convert method
- Add camera calibrator in python to support 3 types of calibration
- Add image class and support the conversion with OpenCV
- Add external deps and use conan manager to accelerate the compilation
- Provide samples to demonstrate linking XRPrimer in other C++ projects
