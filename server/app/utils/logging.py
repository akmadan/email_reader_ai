import logging
import sys
import os
from typing import Optional

class GlobalLogger:
    
    _instance: Optional['GlobalLogger'] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GlobalLogger, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._logger is None:
            self.setup_logger()
    
    def setup_logger(self):
        """Initialize the logger with console-only configuration"""
        # Get environment variable (defaults to 'prod' if not set)
        env = os.getenv('APP_ENV', 'prod').lower()
        
        # Create logger
        self._logger = logging.getLogger('app_logger')
        self._logger.setLevel(logging.DEBUG if env == 'debug' else logging.INFO)
        
        # Clear any existing handlers
        self._logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(funcName)s() | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console Handler - only handler we need
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(detailed_formatter if env == 'debug' else simple_formatter)
        console_handler.setLevel(logging.DEBUG if env == 'debug' else logging.INFO)
        self._logger.addHandler(console_handler)
        
        # Log the initialization
        self._logger.info(f"Logger initialized in {env.upper()} mode")
        
    def get_logger(self) -> logging.Logger:
        """Get the configured logger instance"""
        return self._logger
    
    # Convenience methods for direct logging
    def debug(self, message: str, *args, **kwargs):
        """Log debug message"""
        self._logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """Log info message"""
        self._logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """Log warning message"""
        self._logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """Log error message"""
        self._logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """Log critical message"""
        self._logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        """Log exception with traceback"""
        self._logger.exception(message, *args, **kwargs)

# Global logger instance
logger = GlobalLogger()


