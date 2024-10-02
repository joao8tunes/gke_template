#!/usr/bin/env python
# encoding: utf-8

# João Antunes <joao8tunes@gmail.com>
# https://github.com/joao8tunes

import logging
from flask import Flask, request

from source.system_settings import setup_logging


setup_logging(__name__)
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home() -> str:
    """
    Handle GET and POST requests to the root endpoint.

    Parameters
    ----------
    None

    Returns
    -------
    str
        A simple message indicating the API is running.

    Examples
    --------
    >>> client.get('/')
    b'Simple API'
    """
    message = "Simple API"
    print(message)
    logging.info(message)
    logging.debug("Waiting for another HTTP request before running again...")

    return message


@app.route('/hello', methods=['GET', 'POST'])
def hello_world() -> str:
    """
    Handle GET requests to the root endpoint.

    Parameters
    ----------
    None

    Returns
    -------
    str
        A greeting message that includes the 'name' parameter from the query string or "World" if not provided.

    Examples
    --------
    >>> client.get('/hello')
    b'Hello World!'

    >>> client.get('/hello?name=Alice')
    b'Hello Alice!'
    """
    name = request.args.get('name', "World")
    message = f"Hello {name}!"
    print(message)
    logging.info(message)
    logging.debug("Waiting for another HTTP request before running again...")

    return message
