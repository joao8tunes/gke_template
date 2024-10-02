#!/usr/bin/env python
# encoding: utf-8

# João Antunes <joao8tunes@gmail.com>
# https://github.com/joao8tunes

from source.system_settings import setup_logging
from source.app import app

setup_logging(__name__)


if __name__ == '__main__':
    app.run(threaded=True)
