# -*- coding: utf8 -*-
import os
import tempfile


BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Base
DEBUG = False

# API
API_VERSION = "v0.1"
API_NAME = "ios-vm-generator"
API_IP = "localhost"
API_PORT = None

# Log Files
LOG_FILE = "/var/log/ios-vm-generator/ios-vm-generator.log"

# Image
DEFAULT_BOX = "qualify-ios"
BOX_SNAPSHOT = "v1.0"
