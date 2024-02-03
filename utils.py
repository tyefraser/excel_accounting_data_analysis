import os
from pathlib import Path
import logging
import logging.config
import yaml

def project_absolute_path() -> Path:
    return Path(__file__).resolve().parents[0]

def absolute_path(dir: str) -> str:
    return os.path.join(project_absolute_path(), dir)


def setup_logging(default_path='logging_config.yaml', default_level=logging.INFO, env_key='LOG_CFG'):
    """
    Setup logging configuration
    """
    path = absolute_path(dir=default_path)
    
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        logging.info('Running yaml logger')
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.info('Running default logger, not from the yaml')
        logging.basicConfig(level=default_level)

# Set up logging using the configuration file
setup_logging()

# Create a logger variable
logger = logging.getLogger(__name__)

def create_directory_if_not_exists(absolute_path):
    # Extract the directory path
    directory_path = os.path.dirname(absolute_path)

    # Check if the directory exists, if not, create it
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

def assert_file_extension(
        file_name,
        expected_extension: str = '.xlsx',
):
    logger.debug('\n\n\nRunning: assert_file_extension')

    file_extension=os.path.splitext(file_name)[1]
    try:
        assert (file_extension == expected_extension), (
            f"Incorrect file extension, expecting '{expected_extension}' but got '{file_extension}'"
        )
        return True        
    except AssertionError as e:
        logger.info(f"AssertionError: {e}")
        raise AssertionError(f"AssertionError: {e}")
