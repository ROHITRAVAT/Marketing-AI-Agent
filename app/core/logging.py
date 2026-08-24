import logging
import sys


VALID_LOG_LEVELS = {
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
}


def setup_logging(level: str = "INFO") -> None:
    """Configure centralized logging for the entire application.

    Call this once at application startup. All modules can then use
    ``logging.getLogger(__name__)`` and inherit this configuration.
    """

    normalized_level = level.upper()

    if normalized_level not in VALID_LOG_LEVELS:
        raise ValueError(
            f"Invalid log level: {level}. "
            f"Expected one of: {', '.join(sorted(VALID_LOG_LEVELS))}"
        )

    logging.basicConfig(
        level=normalized_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        stream=sys.stdout,
        force=True,
    )