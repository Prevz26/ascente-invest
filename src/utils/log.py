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
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    file_handler = logging.FileHandler(os.path.join(log_dir, "app.log"))
    file_handler.setLevel(logging.ERROR)  # Set file handler to ERROR level
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Stream handler - INFO and above
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)  # Set stream handler to INFO level
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)
