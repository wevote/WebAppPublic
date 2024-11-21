# import_export_bigquery/controllers.py
# Brought to you by We Vote. Be good.
# -*- coding: UTF-8 -*-

import json
import requests
from config.base import get_environment_variable
from exception.models import handle_exception
import wevote_functions.admin


logger = wevote_functions.admin.get_logger(__name__)

BIGQUERY_BASE_URL = get_environment_variable("BIGQUERY_BASE_URL", no_exception=True)
BIGQUERY_PROJECT_KEY = get_environment_variable("BIGQUERY_PROJECT_KEY", no_exception=True)
BIGQUERY_ORGANIZATION_KEY = get_environment_variable("BIGQUERY_ORGANIZATION_KEY", no_exception=True)



