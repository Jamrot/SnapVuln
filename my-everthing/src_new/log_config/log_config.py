import logging.config
import yaml
import os
from pytz import timezone
from datetime import datetime

class CustomFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, tz='Asia/Shanghai'):
        super().__init__(fmt=fmt, datefmt=datefmt)
        self.tz = timezone(tz)

    def formatTime(self, record, datefmt=None):
        ct = datetime.fromtimestamp(record.created).astimezone(self.tz)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime("%Y-%m-%d %H:%M:%S")
            s = f"{t},{record.msecs:03d}"
        return s

def setup_logging(default_filename='logging.yaml', default_level=logging.DEBUG, env_key='LOG_CONFIG', log_filename='log.log'):
    """Setup logging configuration"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(script_dir, default_filename)
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
        config['handlers']['file']['filename'] = log_filename
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
