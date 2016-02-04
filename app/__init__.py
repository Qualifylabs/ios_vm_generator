# -*- coding: utf8 -*-
import logging
import sched
import time
from flask import Flask
from vm_operations import device_status_daemon


def create_app():
    app = Flask(__name__)

    app.config.from_pyfile('../config.py')

    file_handler = logging.FileHandler(
        filename='{}'.format(app.config['LOG_FILE']))
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        # '[in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(file_handler)
    if app.config['DEBUG'] is True or app.config['TESTING'] is True:
        app.debug = True

    _url = "/{}/{}".format(app.config['API_NAME'], app.config['API_VERSION'])

    device_status_daemon()

    return app
