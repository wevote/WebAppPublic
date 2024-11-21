# import_export_bigquery/urls.py
# Brought to you by We Vote. Be good.
# -*- coding: UTF-8 -*-

from django.urls import re_path

from . import views_admin

urlpatterns = [
    re_path(r'^$', views_admin.import_export_bigquery_index_view, name='import_export_bigquery_index'),
    re_path(r'^event_list/$', views_admin.bigquery_event_list_view, name='bigquery_event_list'),
]
