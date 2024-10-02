#!/usr/bin/env python
# encoding: utf-8

# João Antunes <joao8tunes@gmail.com>
# https://github.com/joao8tunes

import logging
import time

from source.system_settings import setup_logging


setup_logging(__name__)


def hello_world():
    """
    Continuously prints 'Hello World!' to the console every n seconds.

    This function runs an infinite loop that prints 'Hello World!' to the
    console and then sleeps for n seconds. This function does not return
    any value and will keep running indefinitely until interrupted.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    while True:
        message = "Hello World!"
        waiting_time = 60

        print(message)
        logging.info(message)
        logging.debug(f"Waiting {waiting_time} seconds before running again...")
        time.sleep(waiting_time)
