# import_export_openreplay/urls.py
# Brought to you by We Vote. Be good.
# -*- coding: UTF-8 -*-

from django.urls import re_path

from . import views_admin

urlpatterns = [
    re_path(r'^$', views_admin.import_export_openreplay_index_view, name='import_export_openreplay_index'),
    re_path(r'^event_list/$', views_admin.openreplay_event_list_view, name='openreplay_event_list'),
]
