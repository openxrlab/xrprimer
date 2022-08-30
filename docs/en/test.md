# Running Tests

- [Running Tests](#running-tests)
  - [Data Preparation](#data-preparation)
  - [Environment Preparation](#environment-preparation)
  - [Running tests through pytest](#running-tests-through-pytest)

## Data Preparation

Download data from the file server, and extract files to `python/test/data`.

```
cd python/test
wget -q https://openxrlab-share.oss-cn-hongkong.aliyuncs.com/xrprimer/xrprimer.tar.gz
tar -xzf xrprimer.tar.gz && rm xrprimer.tar.gz
cp -r xrprimer/test/data ./
rm -rf xrprimer && cd ../../
```

## Environment Preparation

Install packages for test.

```
pip install -r python/requirements/test.txt
```

## Running tests through pytest

Running all the tests below `python/test`. It is a good way to validate whether `XRprimer` has been correctly installed:

```
cd python
pytest test/
cd ..
```

Generate a coverage for the test:

```
cd python
coverage run --source xrprimer -m pytest test/
coverage xml
coverage report -m
cd ..
```
