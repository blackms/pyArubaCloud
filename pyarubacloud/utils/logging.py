"""
Logging utilities for the pyArubaCloud library.

This module provides logging functionality for the ArubaCloud API client,
including configurable log levels and output destinations.
"""

import logging
import sys
from typing import Optional, Union, TextIO


def setup_logger(
    name: str = "pyarubacloud",
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    log_format: Optional[str] = None,
    stream: Optional[TextIO] = None
) -> logging.Logger:
    """
    Set up a logger with the specified configuration.
    
    Args:
        name: The name of the logger.
        level: The logging level.
        log_file: An optional file path to write logs to.
        log_format: An optional log format string.
        stream: An optional stream to write logs to.
        
    Returns:
        A configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Set default format if not provided
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    formatter = logging.Formatter(log_format)
    
    # Add stream handler if requested
    if stream is not None:
        stream_handler = logging.StreamHandler(stream)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
    elif log_file is None:
        # Add console handler by default if no file or stream is specified
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Add file handler if requested
    if log_file is not None:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


class ArubaLogger:
    """
    Logger wrapper for the ArubaCloud API client.
    
    This class provides a simplified interface for logging messages
    at different levels, with support for context-specific loggers.
    """
    
    def __init__(
        self,
        name: str = "pyarubacloud",
        level: int = logging.INFO,
        log_file: Optional[str] = None,
        log_format: Optional[str] = None,
        stream: Optional[TextIO] = None
    ):
        """
        Initialize the logger.
        
        Args:
            name: The name of the logger.
            level: The logging level.
            log_file: An optional file path to write logs to.
            log_format: An optional log format string.
            stream: An optional stream to write logs to.
        """
        self.logger = setup_logger(name, level, log_file, log_format, stream)
    
    def get_child(self, name: str) -> 'ArubaLogger':
        """
        Get a child logger with the specified name.
        
        Args:
            name: The name of the child logger.
            
        Returns:
            A new ArubaLogger instance with the child logger.
        """
        child_logger = self.logger.getChild(name)
        result = ArubaLogger()
        result.logger = child_logger
        return result
    
    def set_level(self, level: int) -> None:
        """
        Set the logging level.
        
        Args:
            level: The logging level.
        """
        self.logger.setLevel(level)
    
    def debug(self, msg: str, *args, **kwargs) -> None:
        """
        Log a debug message.
        
        Args:
            msg: The message to log.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        self.logger.debug(msg, *args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs) -> None:
        """
        Log an info message.
        
        Args:
            msg: The message to log.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        self.logger.info(msg, *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs) -> None:
        """
        Log a warning message.
        
        Args:
            msg: The message to log.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        self.logger.warning(msg, *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs) -> None:
        """
        Log an error message.
        
        Args:
            msg: The message to log.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        self.logger.error(msg, *args, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs) -> None:
        """
        Log a critical message.
        
        Args:
            msg: The message to log.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        self.logger.critical(msg, *args, **kwargs)
    
    def exception(self, msg: str, *args, **kwargs) -> None:
        """
        Log an exception message.
        
        Args:
            msg: The message to log.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        self.logger.exception(msg, *args, **kwargs)