import logging
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logging(log_dir: Path):
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"asr_scraper_{datetime.utcnow().strftime('%Y-%m-%d')}.log"
    logger = logging.getLogger()
    logger.setLevel("INFO")
    logger.handlers.clear()

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10_000_000,
        backupCount=5,
        encoding="utf-8",
    )

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | "
        "%(platform)s, %(channel_ref)s, %(video_id)s, %(url)s - %(message)s"
    )

    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)