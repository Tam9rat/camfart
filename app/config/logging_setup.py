from __future__ import annotations

import logging
import logging.handlers
import os
import pathlib


def configure_logging() -> None:
    log_dir = pathlib.Path(os.getenv("LOG_DIR", "/tmp/camfart_logs"))
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "camfart.log"

    root = logging.getLogger()
    if root.handlers:
        return  # already configured (Streamlit reruns this module)

    root.setLevel(logging.INFO)

    fmt = logging.Formatter(
        "%(asctime)s %(levelname)-8s %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    fh = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    fh.setFormatter(fmt)
    root.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    ch.setLevel(logging.WARNING)
    root.addHandler(ch)
