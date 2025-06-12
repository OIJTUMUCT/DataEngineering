import logging
from colorlog import ColoredFormatter

def get_logger(name: str = __name__) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        handler.setFormatter(ColoredFormatter(
            fmt="%(log_color)s[%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%H:%M:%S",
            log_colors={
                'DEBUG':    'blue',
                'INFO':     'white',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CRITICAL': 'bold_red',
            }
        ))
        logger.addHandler(handler)

    return logger