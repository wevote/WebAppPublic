# volunteer_task/urls.py
# Brought to you by We Vote. Be good.
# -*- coding: UTF-8 -*-

from django.urls import re_path

from . import views_admin

urlpatterns = [
    re_path(r'^scoreboard_list_process/$',
            views_admin.scoreboard_list_process_view, name='scoreboard_list_process',),
    re_path(r'^$', views_admin.scoreboard_list_view, name='scoreboard_list',),
]
