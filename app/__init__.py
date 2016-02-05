# -*- coding: utf8 -*-
from flask import Flask
from vm_operations import device_status_daemon


def create_app():
    app = Flask(__name__)

    app.config.from_pyfile('../config.py')

    if app.config['DEBUG'] is True or app.config['TESTING'] is True:
        app.debug = True

    _url = "/{}/{}".format(app.config['API_NAME'], app.config['API_VERSION'])

    device_status_daemon()

    return app
