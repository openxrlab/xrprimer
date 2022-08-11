# Frequently Asked Questions

We list some common troubles faced by many users and their corresponding solutions here. Feel free to enrich the list if you find any frequent issues and have ways to help others to solve them. If the contents here do not cover your issue, do not hesitate to create an issue!


## Installation

- 'ImportError: libpng16.so.16: cannot open shared object file: No such file or directory'

    1. If using conda, `conda install -c anaconda libpng`
    2. If sudo is available, `apt update & apt -y install libpng16-16`

- 'ImportError: liblapack.so.3: cannot open shared object file: No such file or directory'

    1. If using conda, `conda install -c conda-forge lapack`
    2. If sudo is available, `apt update & apt -y install libatlas-base-dev`
