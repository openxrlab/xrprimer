# Download base image ubuntu 18.04
FROM ubuntu:18.04

# Install apt packages
RUN apt-get update && \
    apt-get install -y \
        wget git vim \
        gcc-7 g++-7 make ninja-build \
        libblas-dev liblapack-dev libatlas-base-dev\
    && \
    apt-get autoclean

# Install miniconda
RUN wget -q \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b -p /opt/miniconda \
    && rm -f Miniconda3-latest-Linux-x86_64.sh

# Update gcc/g++/conda in bashrc
RUN echo "export CXX=/usr/bin/g++-7" >> /root/.bashrc && \
    echo "export CC=/usr/bin/gcc-7" >> /root/.bashrc && \
    echo "source /opt/miniconda/etc/profile.d/conda.sh" >> /root/.bashrc && \
    echo "conda deactivate" >> /root/.bashrc

# Source the new env
RUN . /opt/miniconda/etc/profile.d/conda.sh && \
    conda deactivate
ENV CXX /usr/bin/g++-7
ENV CC /usr/bin/gcc-7

ARG PY_VER
# Prepare conda env
RUN . /opt/miniconda/etc/profile.d/conda.sh && \
    conda create -n openxrlab python=$PY_VER -y && \
    conda activate openxrlab && \
    conda install ffmpeg -y && \
    conda install cmake -y && \
    conda clean --all

# Prepare torch env
ARG TORCH_VER
ARG TORCHV_VER
RUN . /opt/miniconda/etc/profile.d/conda.sh && \
    conda activate openxrlab && \
    conda install pytorch==$TORCH_VER torchvision==$TORCHV_VER cpuonly -c pytorch && \
    conda clean --all

ARG MMCV_VER
# Prepare pip env
RUN . /opt/miniconda/etc/profile.d/conda.sh && \
    conda activate openxrlab && \
    pip install pre-commit interrogate coverage pytest && \
    pip install numpy matplotlib && \
    pip install mmcv==$MMCV_VER && \
    pip install conan==1.51.1 && \
    pip cache purge

# Install basic requirements
RUN . /opt/miniconda/etc/profile.d/conda.sh && \
    conda activate openxrlab && \
    pip install -r https://raw.githubusercontent.com/openxrlab/xrprimer/main/requirements/runtime.txt && \
    pip cache purge

RUN . /opt/miniconda/etc/profile.d/conda.sh && \
    conda activate openxrlab && \
    pip uninstall opencv-python opencv-python-headless -y && \
    pip install opencv-python-headless && \
    pip cache purge
