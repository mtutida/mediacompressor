import logging
from pathlib import Path

from app.core.paths import APP_ROOT


LOG_DIR = APP_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "app.log"


class LoggingService:

    _initialized = False

    def __init__(self):

        if LoggingService._initialized:
            self.logger = logging.getLogger("app")
            return

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            handlers=[
                logging.FileHandler(LOG_FILE, encoding="utf-8"),
                logging.StreamHandler()
            ]
        )

        self.logger = logging.getLogger("app")

        LoggingService._initialized = True

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)
        