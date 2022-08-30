#Download base image ubuntu 18.04
FROM ubuntu:18.04

# Install apt packages
RUN apt-get update && \
    apt-get install -y \
        wget git vim \
        gcc-7 g++-7 make \
        libblas-dev liblapack-dev libatlas-base-dev\
    && \
    apt-get autoclean

# Install miniconda
RUN wget -q \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh

# Update in bashrc
RUN echo "export CXX=/usr/bin/g++-7" >> /root/.bashrc && \
    echo "export CC=/usr/bin/gcc-7" >> /root/.bashrc && \
    echo "source /root/miniconda3/etc/profile.d/conda.sh" >> /root/.bashrc && \
    echo "conda deactivate" >> /root/.bashrc

# Source the new env
RUN . /root/miniconda3/etc/profile.d/conda.sh && \
    conda deactivate
ENV CXX /usr/bin/g++-7
ENV CC /usr/bin/gcc-7

# Prepare conda env
RUN . /root/miniconda3/etc/profile.d/conda.sh && \
    conda create -n openxrlab python=3.8 -y && \
    conda activate openxrlab && \
    conda install ffmpeg -y && \
    conda install cmake -y && \
    conda clean --all

# Prepare pip env
RUN . /root/miniconda3/etc/profile.d/conda.sh && \
    conda activate openxrlab && \
    pip install pre-commit interrogate coverage pytest twine -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install opencv-python-headless numpy -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install torch==1.8.1 torchvision==0.9.1 -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install mmcv==1.5.0 && \
    pip install conan && \
    conan remote add xrlab \
        http://conan.kestrel.sensetime.com/artifactory/api/conan/xrlab && \
    pip cache purge

# Clone xrprimer and install
RUN . /root/miniconda3/etc/profile.d/conda.sh && \
    conda activate openxrlab && \
    mkdir /workspace && cd /workspace && \
    git clone https://github.com/openxrlab/xrprimer.git && \
    cd xrprimer && pip install -e . && \
    pip cache purge
