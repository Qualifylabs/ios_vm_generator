# -*- coding: utf8 -*-
import os


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DEBUG = False

# API
API_VERSION = "v0.1"
API_NAME = "ios-vm-generator"

# Log Files
LOG_FILE = "/var/log/ios-vm-generator/ios-vm-generator.log"

# Base OSX Image
DEFAULT_BOX = "qualify-ios"
BOX_SNAPSHOT = "v1.0"
