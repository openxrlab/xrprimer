# Running Tests

- [Data Preparation](#data-preparation)
- [Environment Preparation](#environment-preparation)
- [Running tests through pytest](#running-tests-through-pytest)

## Data Preparation

Download data from the file server, and extract files to `python/tests/data`.

```
cd python/tests
wget -q https://openxrlab-share.oss-cn-hongkong.aliyuncs.com/xrprimer/xrprimer.tar.gz
tar -xzf xrprimer.tar.gz && rm xrprimer.tar.gz
cp -r xrprimer/tests/data ./
rm -rf xrprimer && cd ../../
```

## Environment Preparation

Install packages for test.

```
pip install -r requirements/test.txt
```

## Running tests through pytest

Running all the tests below `python/tests`. It is a good way to validate whether `XRPrimer` has been correctly installed:

```
cd python
pytest tests/
cd ..
```

Generate a coverage for the test:

```
cd python
coverage run --source xrprimer -m pytest tests/
coverage xml
coverage report -m
cd ..
```
