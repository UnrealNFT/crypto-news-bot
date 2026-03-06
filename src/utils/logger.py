import logging


def setup_logger(name: str = __name__, level: str = "INFO"):
    """Setup and return a configured logger."""
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=getattr(logging, level, logging.INFO),
    )
    return logging.getLogger(name)
