import os
import shutil

import pytest

from xrprimer.utils.path_utils import (
    Existence,
    check_path_existence,
    check_path_suffix,
)

input_dir = 'tests/data/utils/test_path_utils'
output_dir = 'tests/data/output/utils/test_path_utils'


@pytest.fixture(scope='module', autouse=True)
def fixture():
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=False)


def test_check_path_existence():
    # test FileExist
    path = os.path.join(output_dir, 'FileExist.txt')
    with open(path, 'w') as f_write:
        f_write.write('\n')
    assert check_path_existence(path) == Existence.FileExist
    # test DirectoryExistEmpty
    path = os.path.join(output_dir, 'DirectoryExistEmpty')
    os.mkdir(path)
    assert check_path_existence(path) == Existence.DirectoryExistEmpty
    # test DirectoryExistNotEmpty
    path = os.path.join(output_dir, 'DirectoryExistNotEmpty')
    os.mkdir(path)
    with open(os.path.join(path, 'test_file.txt'), 'w') as f_write:
        f_write.write('\n')
    assert check_path_existence(path) == Existence.DirectoryExistNotEmpty
    # test MissingParent
    path = os.path.join(output_dir, 'MissingParent', 'test_file.txt')
    assert check_path_existence(path) == Existence.MissingParent
    # test DirectoryNotExist
    path = os.path.join(output_dir, 'DirectoryNotExist')
    assert check_path_existence(path) == Existence.DirectoryNotExist
    # test DirectoryNotExist
    path = os.path.join(output_dir, 'FileNotExist.txt')
    assert check_path_existence(path) == Existence.FileNotExist


def test_check_path_suffix():
    # test True
    path = os.path.join(output_dir, 'check_path_suffix.txt')
    with open(path, 'w') as f_write:
        f_write.write('\n')
    assert check_path_suffix(path, [])
    # test single str
    assert check_path_suffix(path, '.txt')
    # test list
    assert check_path_suffix(path, ['.txt'])
    assert check_path_suffix(path, ['.bin', '.txt'])
    # test upper case
    assert check_path_suffix(path, ['.bin', '.TXT'])
    # test dir
    path = os.path.join(output_dir, 'check_path_suffix_dir')
    os.mkdir(path)
    assert check_path_suffix(path, '')
    assert check_path_suffix(path, [''])
    assert not check_path_suffix(path, ['.txt'])
