# Changelog

### v0.7.0 (05/05/2023/)

**Highlights**

- Add `synbody_utils.py` and `exr_reader.py` module to help with using synbody dataset.
- Support points and lines visualization by OpenCV and by Matplotlib.
- Improve external dependencies by splitting external and project build.
- Update dockerfiles, build scripts and docker images.

**New Features**

- Add points and lines visualization by OpenCV and by Matplotlib, with features such as PointPalette and LinePalette for visualization backends sharing the same definition of data.
- Add fast undistortion in Python.
- Add Keypoints, Limbs and keypoints_convention from XRMoCap.
- Add world convention for 3D spaces.
- Add `VideoReader` to ffmpeg_utils in Python. Together with `VideoWriter`, now we can visualize a really long video on a machine with poor RAM.

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
