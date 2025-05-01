"""
Logging utilities for viby
"""

import logging


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Setup and configure logger"""
    logger = logging.getLogger("viby")
    logger.setLevel(level)
    
    # Create console handler with formatting
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger
