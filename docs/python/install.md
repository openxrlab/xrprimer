# Installation

<!-- TOC -->

- [Installation](#installation)
  - [Requirements](#requirements)
  - [Prepare environment](#prepare-environment)
  - [Install XRprimer(python)](#install-xrprimerpython)

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

## Install XRprimer(python)


a. Install build requirements and then install xrprimer.

```shell
cd python
pip install -r requirements/runtime.txt
pip install -v -e .  # or "python setup.py develop"
```
