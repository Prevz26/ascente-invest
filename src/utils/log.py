import logging
import os 

def setup_root_logger() -> None:
    """Set up the root logger."""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)  # Set to INFO to allow INFO level logs
    
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)-8s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # File handler - ERROR and above only
    # Get the absolute path to the `logs` directory inside `src`
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # this resolves to src/utils
    LOG_DIR = os.path.join(BASE_DIR, '..', 'logs')
    os.makedirs(LOG_DIR, exist_ok=True)

    file_handler = logging.FileHandler(os.path.join(LOG_DIR, 'error.log'))
    file_handler.setLevel(logging.ERROR)  # Set file handler to ERROR level
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Stream handler - INFO and above
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)  # Set stream handler to INFO level
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)
    
import os

# This resolves to your project root, assuming this file is in `src/utils`
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
LOG_DIR = os.path.join(PROJECT_ROOT, 'src', 'logs')
print("\n" + LOG_DIR + "\n")

# Ensure logs directory exists
os.makedirs(LOG_DIR, exist_ok=True)

def get_log_path(filename: str) -> str:
    return os.path.join(LOG_DIR, filename)
