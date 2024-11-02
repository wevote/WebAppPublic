# import_export_openreplay/views_admin.py
# Brought to you by We Vote. Be good.
# -*- coding: UTF-8 -*-

# from .controllers import augment_one_voter_analytics_action_entries_without_election_id, \
#     augment_voter_analytics_action_entries_without_election_id, \
#     save_organization_daily_metrics, save_organization_election_metrics, \
#     save_sitewide_daily_metrics, save_sitewide_election_metrics, save_sitewide_voter_metrics
# from .models import ACTION_BALLOT_VISIT, \
#     AnalyticsAction, AnalyticsManager, display_action_constant_human_readable, \
#     fetch_action_constant_number_from_constant_string, OrganizationDailyMetrics, OrganizationElectionMetrics, \
#     SitewideDailyMetrics, SitewideElectionMetrics, SitewideVoterMetrics
from admin_tools.views import redirect_to_sign_in_page
from config.base import get_environment_variable
import csv
from datetime import date, timedelta
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages import get_messages
from django.db.models import Q
from django.shortcuts import render
from django.utils.timezone import now
from election.models import Election, ElectionManager
from exception.models import print_to_log
import json
import requests
from socket import timeout
from voter.models import voter_has_authority
import wevote_functions.admin
from wevote_settings.constants import ELECTION_YEARS_AVAILABLE
from wevote_functions.functions import convert_to_int, positive_value_exists, STATE_CODE_MAP
from wevote_functions.functions_date import convert_date_as_integer_to_date, convert_date_to_date_as_integer
from wevote_settings.models import WeVoteSetting, WeVoteSettingsManager

logger = wevote_functions.admin.get_logger(__name__)

