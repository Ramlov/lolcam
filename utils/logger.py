import logging
import os
from pathlib import Path

def setup_logging(config):
    """Setup application logging"""
    log_level = getattr(logging, config.get('app.log_level', 'INFO'))
    log_file = config.get('directories.logs_path', '/tmp') + '/selfie-booth.log'
    
    # Ensure log directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    # Reduce verbosity for some noisy libraries
    logging.getLogger('googleapiclient').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)