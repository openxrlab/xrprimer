# Installation

<!-- TOC -->

- [Installation](#installation)
  - [Requirements](#requirements)
  - [Prepare environment](#prepare-environment)
  - [Install XRPrimer(python)](#install-xrprimerpython)

<!-- TOC -->

## Requirements

- Linux
- Conda
- Python 3.7+

## Prepare environment

a. Create a conda virtual environment and activate it.

```shell
conda create -n openxrlab python=3.8 -y
conda activate openxrlab
```

## Install XRPrimer(python)


a. As a user, install XRPrimer by WHL.

```shell
# for python3.7
pip install http://10.10.30.159:8999/xrprimer-0.3.0-cp37-cp37m-linux_x86_64.whl
# for python3.8
pip install http://10.10.30.159:8999/xrprimer-0.3.0-cp38-cp38-linux_x86_64.whl
```

b. As a developer, compile XRPrimer(cpp), and install XRPrimer(python) in editable mode.

```shell
# As a developer, compile from source code:
pip install conan
conan remote add xrlab http://conan.kestrel.sensetime.com/artifactory/api/conan/xrlab
cmake -S. -Bbuild && cmake --build build -j4
cd python && pip install -e . && cd ..
python -c "import xrprimer; print(xrprimer.__version__)"
```

