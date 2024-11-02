# import_export_openreplay/models.py
# Brought to you by We Vote. Be good.
# -*- coding: UTF-8 -*-

from django.db import models
import wevote_functions.admin
from wevote_functions.functions import convert_to_int, positive_value_exists


# SESSIONS
class OpenReplaySession(models.Model):
    errors_count = models.PositiveIntegerField(null=True)
    events_count = models.PositiveIntegerField(null=True)
    pages_count = models.PositiveIntegerField(null=True)
    project_id = models.CharField(max_length=255, null=True)
    user_uuid = models.CharField(max_length=36, null=True)
# Id INTEGER,
# projectId VARCHAR(255) ,
# sessionId  VARCHAR(255) ,
# userUuid VARCHAR(255) ,
# userId VARCHAR(255) NOT NULL,
# userAgent VARCHAR(255) ,
# userOs VARCHAR(255) ,
# userBrowser VARCHAR(255) ,
# userDevice VARCHAR(255) ,
# userCountry VARCHAR(255) ,
# startTs VARCHAR(255) ,
# duration VARCHAR(255) ,
# eventsCount VARCHAR(255) ,
# pagesCount VARCHAR(255) ,
# errorsCount VARCHAR(255),


# EVENTS
class OpenReplayEvent(models.Model):
    label = models.TextField(null=True)
    value = models.TextField(null=True)
    selector = models.TextField(null=True)
    type = models.CharField(max_length=255, null=True)
# Id INTEGER,
# sessionId VARCHAR(255),
# messageId  VARCHAR(255) ,
# timestamp VARCHAR(255) ,
# host VARCHAR(255),
# path VARCHAR(255),
# query VARCHAR(255),
# referrer VARCHAR(255),
# baseReferrer VARCHAR(255),
# domBuildingTime VARCHAR(255),
# domContentLoadedTime VARCHAR(255),
# loadTime VARCHAR(255),
# firstPaintTime VARCHAR(255),
# firstContentfulPaintTime VARCHAR(255),
# speedIndex VARCHAR(255),
# visuallyComplete VARCHAR(255),
# timeToInteractive VARCHAR(255),
# responseTime VARCHAR(255),
# responseEnd VARCHAR(255),
# ttfb VARCHAR(255),
# value LONGTEXT,
# duration VARCHAR(255),
# url VARCHAR(255),
# label VARCHAR(255),
# selector LONGTEXT,
# hesitation VARCHAR(255),
# type VARCHAR(255),
