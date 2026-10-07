import logging
import json
import sys
from pathlib import Path
from datetime import datetime
from app.config import settings

class JSONFormatter(logging.Formatter):
    """Format logs as JSON for easier parsing"""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add any extra data
        if hasattr(record, 'extra_data'):
            log_data['data'] = record.extra_data
        
        return json.dumps(log_data)

class DebugLogger:
    """Conditional debug logging"""
    
    _instance = None
    _debug_enabled = False
    _loggers = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def enable_debug(cls, enable=True):
        """Enable/disable debug logging"""
        cls._debug_enabled = enable
        print(f"🔧 Debug logging {'enabled' if enable else 'disabled'}")
    
    @classmethod
    def is_debug_enabled(cls):
        """Check if debug is enabled"""
        return cls._debug_enabled
    
    @classmethod
    def get_logger(cls, name):
        """Get or create a logger"""
        if name not in cls._loggers:
            logger = logging.getLogger(name)
            
            # Console handler (always)
            console_handler = logging.StreamHandler(sys.stdout)
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
            
            # File handler (for debug logs)
            try:
                log_file = settings.LOGS_DIR / 'debug.log'
                file_handler = logging.FileHandler(log_file)
                file_formatter = JSONFormatter()
                file_handler.setFormatter(file_formatter)
                logger.addHandler(file_handler)
            except Exception as e:
                print(f"⚠️  Could not create file handler: {e}")
            
            cls._loggers[name] = logger
        
        return cls._loggers[name]

# Create global logger instance
logger = DebugLogger()
