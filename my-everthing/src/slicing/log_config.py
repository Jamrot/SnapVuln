import logging.config
import yaml
import os

def setup_logging(default_filename='logging.yaml', default_level=logging.DEBUG, env_key='LOG_CONFIG'):
    """Setup logging configuration"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(script_dir, default_filename)
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        print(f"Logging config file not found at: {path}")
        logging.basicConfig(level=default_level)


if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")
