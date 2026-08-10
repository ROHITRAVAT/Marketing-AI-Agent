import logging
import sys


def setup_logging(level: str = "INFO") -> None:
    """Configure centralized logging for the entire application.

    Call this once at application startup. All modules can then use
    ``logging.getLogger(__name__)`` and inherit this configuration.
    """
    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        stream=sys.stdout,
        force=True,
    )