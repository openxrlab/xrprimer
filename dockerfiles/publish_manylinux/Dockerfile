#Download base image pypa/manylinux2014_x86_64
FROM quay.io/pypa/manylinux2014_x86_64:latest

# Install wget
RUN yum install wget atlas-devel \
    lapack-devel blas-devel \
    zlib \
    -y && \
    yum clean all
# Install miniconda
RUN wget -q \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && bash Miniconda3-latest-Linux-x86_64.sh -b -p /opt/miniconda \
    && rm -f Miniconda3-latest-Linux-x86_64.sh

# Prepare shared env
RUN . /opt/miniconda/etc/profile.d/conda.sh && \
    conda activate base && \
    pip install conan==1.51.1 && \
    pip install twine && \
    pip cache purge
RUN . /opt/miniconda/etc/profile.d/conda.sh && \
    conda activate base && \
    conda install cmake && \
    conda clean --all

# gmake[2]: *** No rule to make target `/usr/local/lib/libtiff.so', needed by `lib/xrprimer_cpp.cpython-36m-x86_64-linux-gnu.so'.  Stop.
RUN ln -s /opt/miniconda/bin/conan /opt/rh/devtoolset-10/root/usr/bin/conan && \
    ln -s /opt/miniconda/bin/twine /opt/rh/devtoolset-10/root/usr/bin/twine && \
    ln -s /opt/miniconda/bin/cmake /opt/rh/devtoolset-10/root/usr/bin/cmake

# Update in bashrc
RUN echo "source /opt/miniconda/etc/profile.d/conda.sh" >> /root/.bashrc && \
    echo "conda deactivate" >> /root/.bashrc

ARG MMCV_VER
# Install py-3.6, py-3.7, py-3.8, py-3.9, py-3.10
RUN . /opt/miniconda/etc/profile.d/conda.sh && \
    for i in 6 7 8 9 10; do \
        conda create -n "py-3.$i" python="3.$i" -y && \
        conda activate "py-3.$i" && \
        pip install --upgrade pip setuptools wheel && \
        pip install torch==1.11.0 torchvision==0.12.0 && \
        pip install mmcv==$MMCV_VER && \
        pip cache purge && \
        conda clean --all; \
    done
