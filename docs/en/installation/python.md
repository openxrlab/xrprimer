# Installation (Python)

<!-- TOC -->

- [Installation](#installation)
  - [Requirements](#requirements)
  - [Prepare environment](#prepare-environment)
  - [Install XRPrimer(python)](#install-xrprimerpython)

<!-- TOC -->

## Requirements

- Linux
- Conda
- Python 3.6+

## Prepare environment

a. Create a conda virtual environment and activate it.


## Install XRPrimer (python)


### Install XRPrimer with pip

```shell
pip install xrprimer
```

### Install XRPrimer by compiling from source

a. Create a conda virtual environment and activate it.

```shell
conda create -n openxrlab python=3.8 -y
conda activate openxrlab
```

b. Clone the repo.

```shell
git clone https://github.com/openxrlab/xrprimer.git
cd xrprimer/
```
c. (Optional) Install conan


```shell
# (Optional) compile from source code with conan, otherwise it will build external libs from source
pip install conan
conan remote add xrlab http://conan.kestrel.sensetime.com/artifactory/api/conan/xrlab
```
d. Install PyTorch and MMCV

Install PyTorch and torchvision following [official instructions](https://pytorch.org/).

E.g., install PyTorch 1.8.2 & CPU

```shell
pip install torch==1.8.2+cpu torchvision==0.9.2+cpu -f https://download.pytorch.org/whl/lts/1.8/torch_lts.html
```

Install mmcv without cuda operations

```shell
pip install mmcv
```

e. Install xrprimer in editable mode

```shell
pip install -e .  # or "python setup.py develop"
python -c "import xrprimer; print(xrprimer.__version__)"
```
