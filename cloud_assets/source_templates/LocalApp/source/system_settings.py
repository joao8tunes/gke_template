#!/usr/bin/env python
# encoding: utf-8

# João Antunes <joao8tunes@gmail.com>
# https://github.com/joao8tunes

import coloredlogs
import logging
import yaml
import sys
import os

from google.cloud import logging as gcp_logging

LOG_LEVELS = ("NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


def get_settings() -> dict:
    """
    Import application settings from YAML-based file.

    Returns
    -------
    dict
        Application settings.
    """
    # Loading YAML-based settings file:
    this_dir_path = os.path.abspath(os.path.join(os.path.realpath(__file__), os.pardir))
    settings_filepath = os.path.join(*[this_dir_path, "..", "assets", "settings.yaml"])
    settings = read_yaml(settings_filepath)

    return settings


def read_yaml(filepath: str) -> dict:
    """
    Read YAML-based file content.

    Parameters
    ----------
    filepath : str
        YAML-based filepath.

    Returns
    -------
    dict
        Content from YAML-based file.
    """
    with open(filepath, mode="rt", encoding="utf-8") as file:
        content = yaml.safe_load(file)

    return content


def setup_logging(
        name: str,
        log_filepath: str = None,
        mode: str = "a",
        primary_level: str = None,
        secondary_level: str = "CRITICAL",
        secondary_modules: list = ("google", "urllib3", "matplotlib", "json5", "logs", "numba", "mlflow", "git")
) -> None:
    """
    Setup default logging.

    Parameters
    ----------
    name : str
        Module name.
    log_filepath : str
        Log filepath.
    mode : str
        Log file open mode.
    primary_level : str
        Primary log level.
    secondary_level : str
        Secondary log level.
    secondary_modules : list
        Secondary modules to filter.
    """
    # Loading settings
    settings = get_settings()
    log_level = settings.get('system').get('log_level')

    if not primary_level:
        primary_level = log_level

    # Remove all existing handlers to avoid duplication
    logger = logging.getLogger()  # Root logger

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    if any(var in os.environ for var in ['KUBERNETES_SERVICE_HOST', 'K_SERVICE', 'FUNCTION_NAME']):
        # Setup GCP logging
        try:
            logging_client = gcp_logging.Client()
            logging_client.setup_logging(log_level=primary_level, excluded_loggers=secondary_modules)
        except Exception as e:
            # Handle exceptions that occur during GCP logging setup
            logging.error(f"Failed to setup GCP logging: {e}")
    else:
        # Configure logging
        logger = logging.getLogger(name)  # Named logger

        logging_handlers = [logging.StreamHandler(sys.stdout)]

        if log_filepath:
            logging_handlers.append(logging.FileHandler(log_filepath, mode=mode))

        logging.basicConfig(
            format="%(asctime)s %(name)s %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            level=primary_level,
            handlers=logging_handlers
        )

        # Install coloredlogs for better log readability
        coloredlogs.install(level=primary_level, logger=logger, isatty=True)

        # Suppress warnings not sent by `logging` module
        if secondary_level in ("ERROR", "CRITICAL"):
            os.environ["PYTHONWARNINGS"] = "ignore"

        # Filter secondary logs
        for module in secondary_modules:
            secondary_logger = logging.getLogger(module)
            secondary_logger.setLevel(secondary_level)
