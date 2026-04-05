"""Logging utility."""

from __future__ import annotations

import logging
import sys


class Logger:
    """Logger wrapper."""

    _loggers: dict = {}

    @classmethod
    def get_logger(
        cls,
        name: str,
        level: int = logging.INFO,
    ) -> logging.Logger:
        """Get logger.

        Args:
            name: Logger name
            level: Logging level

        Returns:
            Logger instance
        """
        if name in cls._loggers:
            return cls._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(level)

        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(level)

            formatter = logging.Formatter("[%(levelname)s] %(name)s: %(message)s")
            handler.setFormatter(formatter)

            logger.addHandler(handler)

        cls._loggers[name] = logger

        return logger
