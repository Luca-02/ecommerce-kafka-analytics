import sys

from loguru import logger

logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{extra[component]: <16}</cyan> | "
           f"<cyan>{{file}}</cyan>:<cyan>{{line}}</cyan> - "
           "{message}"
)


def get_logger(component: str):
    """
    Returns a logger with the specified component name.

    :param component: Component name.
    :return: loguru.Logger with extra['component']
    """
    return logger.bind(component=component)
