# import_export_bigquery/models.py
# Brought to you by We Vote. Be good.
# -*- coding: UTF-8 -*-

from django.db import models
import wevote_functions.admin
from wevote_functions.functions import convert_to_int, positive_value_exists


# DALE NOTE: These are dummy tables and should be replaced with actual tables needed for BigQuery integration
class BigQuerySession(models.Model):
    errors_count = models.PositiveIntegerField(null=True)
    events_count = models.PositiveIntegerField(null=True)
    pages_count = models.PositiveIntegerField(null=True)
    project_id = models.CharField(max_length=255, null=True)
    user_uuid = models.CharField(max_length=36, null=True)


class BigQueryEvent(models.Model):
    label = models.TextField(null=True)
    value = models.TextField(null=True)
    selector = models.TextField(null=True)
    type = models.CharField(max_length=255, null=True)
