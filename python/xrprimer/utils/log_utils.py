import logging
from typing import Union

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def setup_logger(logger_name: str = 'root',
                 logger_level: int = logging.INFO,
                 logger_path: str = None,
                 logger_format: str = None) -> logging.Logger:
    """Set up a logger.

    Args:
        logger_name (str, optional):
            Name of the logger. Defaults to 'root'.
        logger_level (int, optional):
            Set the logging level of this logger.
            Defaults to logging.INFO.
        logger_path (str, optional):
            Path to the log file.
            Defaults to None, no file will be written,
            StreamHandler will be used.
        logger_format (str, optional):
            The formatter for logger handler.
            Defaults to None.

    Returns:
        logging.Logger:
            A logger with settings above.
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(level=logger_level)
    if logger_path is not None:
        handler = logging.FileHandler(logger_path)
    else:
        handler = logging.StreamHandler()
    if logger_format is not None:
        formatter = logging.Formatter(logger_format)
        handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def get_logger(
        logger: Union[None, str, logging.Logger] = None) -> logging.Logger:
    """Get logger.

    Args:
        logger (Union[None, str, logging.Logger]):
            None for root logger. Besides, pass name of the
            logger or the logger itself.
            Defaults to None.

    Returns:
        logging.Logger
    """
    if logger is None or isinstance(logger, str):
        ret_logger = logging.getLogger(logger)
    else:
        ret_logger = logger
    return ret_logger
