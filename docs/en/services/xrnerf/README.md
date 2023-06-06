# XRNeRF Serving

## 1 Quick Start

### 1.1 Install Dependencies

```shell
# create a virtual environment
conda create -n BridgeServer python=3.7
conda activate BridgeServer

# make sure that your current working directory is xrprimer/requirements/
cd xrprimer/requirements

# install dependencies
pip install -r service_xrnerf.txt
```

### 1.2 Start Server

Once you have dependencies installed, start the server using: 

```shell
# make sure that your current working directory is xrprimer/python/
cd xrprimer/python/xrprimer/services/xrnerf

# start the bridge server
python run.py
```