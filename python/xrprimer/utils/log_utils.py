import logging
from typing import Union

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def setup_logger(logger_name: str = 'root',
                 file_level: int = logging.INFO,
                 console_level: int = logging.INFO,
                 logger_level: Union[int, None] = None,
                 logger_path: str = None,
                 logger_format: str = None) -> logging.Logger:
    """Set up a logger.

    Args:
        logger_name (str, optional):
            Name of the logger. Defaults to 'root'.
        file_level (int, optional):
            Set the logging level of file stream.
            Defaults to logging.INFO.
        console_level (int, optional):
            Set the logging level of console stream.
            Defaults to logging.INFO.
        logger_level (Union[int, None], optional):
            Set the logging level of this logger,
            level of every stream will be overwritten
            if logger_level is set.
            This argument has been deprecated.
            Defaults to None.
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
    level_candidates = [file_level, console_level]
    if logger_level is not None:
        level_candidates = [
            logger_level,
        ]
        console_level = logger_level
        file_level = logger_level
    min_level = min(level_candidates)
    logger.setLevel(level=min_level)
    # prevent logging twice in stdout
    logger.propagate = False
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(console_level)
    handlers = [stream_handler]
    if logger_path is not None:
        handler = logging.FileHandler(logger_path)
        handler.setLevel(file_level)
        handlers.append(handler)
    if logger_format is not None:
        formatter = logging.Formatter(logger_format)
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # assure handlers are not double
    while logger.hasHandlers():
        logger.removeHandler(logger.handlers[0])
    for handler in handlers:
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    if logger_level is not None:
        logger.warning('UserWarning: logger_level is now deprecated, ' +
                       'please specify file_level/console_level instead.')
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
