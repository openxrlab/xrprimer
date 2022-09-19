import logging
import os
import shutil

import pytest

from xrprimer.utils.log_utils import get_logger, setup_logger

input_dir = 'tests/data/utils/test_log_utils'
output_dir = 'tests/data/output/utils/test_log_utils'


@pytest.fixture(scope='module', autouse=True)
def fixture():
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=False)


def test_setup_logger():
    # test name
    test_logger = setup_logger(logger_name='test_name')
    assert get_logger('test_name') == test_logger
    # test level
    test_logger = setup_logger(
        logger_name='test_level', logger_level=logging.DEBUG)
    assert test_logger.level == logging.DEBUG
    # test level
    test_logger = setup_logger(
        logger_name='test_path',
        logger_path=os.path.join(output_dir, 'log.txt'))
    test_logger.info('test msg')
    assert os.path.exists(os.path.join(output_dir, 'log.txt'))
    # test format
    test_logger = setup_logger(
        logger_name='test_path',
        logger_format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    test_logger.info('test msg')


def test_get_logger():
    # test None
    test_logger = get_logger()
    assert test_logger.name == 'root'
    # test name
    test_logger = get_logger('any')
    assert test_logger.name == 'any'
    # test logger type
    test_logger = get_logger(test_logger)
    assert test_logger.name == 'any'
