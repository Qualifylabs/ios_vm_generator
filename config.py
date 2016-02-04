# -*- coding: utf8 -*-
import os
import tempfile


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
HOST_SHARED_PATH = tempfile.mkdtemp()

# Base
DEBUG = False

# API
API_VERSION = "v0.1"
API_NAME = "ios-vm-generator"
API_IP = "localhost"
API_PORT = None

# Log Files
LOG_FILE = "/var/log/ios-vm-generator.log"

# Image
DEFAULT_BOX = "test"
BOX_SNAPSHOT = "v1"
