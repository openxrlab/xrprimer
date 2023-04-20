#Download base image pypa/manylinux2014_x86_64
FROM quay.io/pypa/manylinux2014_x86_64:latest

# Install wget
RUN yum install wget atlas-devel \
    lapack-devel blas-devel \
    zlib libjpeg libpng \
    libwebp \
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
    ln -s /opt/miniconda/bin/cmake /opt/rh/devtoolset-10/root/usr/bin/cmake && \
    ln -s /usr/lib64/libjpeg.so.62 /usr/local/lib64/libjpeg.so && \
    ln -s /usr/lib64/libwebp.so.4 /usr/local/lib/libwebp.so && \
    ln -s /usr/lib64/libpng15.so.15 /usr/local/lib/libpng.so

# Update in bashrc
RUN echo "source /opt/miniconda/etc/profile.d/conda.sh" >> /root/.bashrc && \
    echo "conda deactivate" >> /root/.bashrc

# Set proxy
ENV HTTPS_PROXY http://172.16.1.135:3128
ENV HTTP_PROXY http://172.16.1.135:3128

# Prepare py-3.6 conda env
RUN . /opt/miniconda/etc/profile.d/conda.sh && \
    conda create -n py-3.6 python=3.6 -y && \
    conda activate py-3.6 && \
    pip install --upgrade pip setuptools wheel && \
    pip install torch==1.8.0 torchvision==0.9.0  && \
    pip install mmcv==1.7.0 && \
    pip cache purge

# conda install cmake -y
# pip install conan
# pip install twine -i https://pypi.tuna.tsinghua.edu.cn/simple
# pip install torch==1.8.0 torchvision -i https://pypi.tuna.tsinghua.edu.cn/simple
# pip install mmcv==1.5.0
