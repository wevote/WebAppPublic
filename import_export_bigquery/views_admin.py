# import_export_bigquery/views_admin.py
# Brought to you by We Vote. Be good.
# -*- coding: UTF-8 -*-


from admin_tools.views import redirect_to_sign_in_page
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import localtime, now
from django.db.models import Q
from django.db.models.functions import Length
from office_held.models import OfficeHeld, OfficeHeldManager
from election.models import Election
from politician.models import Politician, PoliticianManager
from voter.models import voter_has_authority
import wevote_functions.admin
from wevote_functions.functions_date import generate_localized_datetime_from_obj, DATE_FORMAT_YMD_HMS
from wevote_settings.constants import IS_BATTLEGROUND_YEARS_AVAILABLE, OFFICE_HELD_YEARS_AVAILABLE


from config.base import get_environment_variable
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages import get_messages
from django.shortcuts import render
import json
import requests
import wevote_functions.admin
from wevote_functions.functions import convert_to_int, positive_value_exists, STATE_CODE_MAP
from .models import BigQueryEvent

logger = wevote_functions.admin.get_logger(__name__)


@login_required
def import_export_bigquery_index_view(request):
    """
    Provide an index of import/export actions (for We Vote data maintenance)
    """
    messages_on_stage = get_messages(request)

    template_values = {
        'messages_on_stage':    messages_on_stage,
    }
    return render(request, 'import_export_bigquery/index.html', template_values)


@login_required
def bigquery_event_list_view(request):
    # admin, analytics_admin, partner_organization, political_data_manager, political_data_viewer, verified_volunteer
    authority_required = {'admin', 'analytics_admin'}
    if not voter_has_authority(request, authority_required):
        return redirect_to_sign_in_page(request, authority_required)

    google_civic_election_id = convert_to_int(request.GET.get('google_civic_election_id', 0))
    messages_on_stage = get_messages(request)
    missing_politician = positive_value_exists(request.GET.get('missing_politician', False))
    bigquery_event_search = request.GET.get('bigquery_event_search', '')
    show_all = positive_value_exists(request.GET.get('show_all', False))
    show_battleground = positive_value_exists(request.GET.get('show_battleground', False))
    show_this_year = convert_to_int(request.GET.get('show_this_year', 9999))
    if show_this_year == 9999:
        datetime_now = localtime(now()).date()  # We Vote uses Pacific Time for TIME_ZONE
        show_this_year = datetime_now.year
    show_ocd_id_state_mismatch = positive_value_exists(request.GET.get('show_ocd_id_state_mismatch', False))
    state_code = request.GET.get('state_code', '')

    # ################################################
    # Maintenance script section START
    # ################################################

    # ################################################
    # Maintenance script section END
    # ################################################

    bigquery_event_count = 0
    bigquery_event_list = []
    state_list = STATE_CODE_MAP
    sorted_state_list = sorted(state_list.items())

    try:
        queryset = BigQueryEvent.objects.all()

        # if positive_value_exists(state_code):
        #     if state_code.lower() == 'na':
        #         queryset = queryset.filter(
        #             Q(state_code__isnull=True) |
        #             Q(state_code='')
        #         )
        #     else:
        #         queryset = queryset.filter(state_code__iexact=state_code)

        # if positive_value_exists(show_representatives_with_email):
        #     queryset = queryset.annotate(representative_email_length=Length('representative_email'))
        #     queryset = queryset.annotate(representative_email2_length=Length('representative_email2'))
        #     queryset = queryset.annotate(representative_email3_length=Length('representative_email3'))
        #     queryset = queryset.filter(
        #         Q(representative_email_length__gt=2) |
        #         Q(representative_email2_length__gt=2) |
        #         Q(representative_email3_length__gt=2)
        #     )

        # if positive_value_exists(missing_politician):
        #     queryset = queryset.filter(
        #         Q(politician_we_vote_id__isnull=True) |
        #         Q(politician_we_vote_id='')
        #     )

        # if positive_value_exists(show_this_year):
        #     if show_this_year in OFFICE_HELD_YEARS_AVAILABLE:
        #         year_field_name = 'year_in_office_' + str(show_this_year)
        #         queryset = queryset.filter(**{year_field_name: True})

        # if positive_value_exists(representative_search):
        #     search_words = representative_search.split()
        #     for one_word in search_words:
        #         filters = []
        #
        #         new_filter = Q(office_held_name__icontains=one_word)
        #         filters.append(new_filter)
        #
        #         new_filter = Q(office_held_we_vote_id=one_word)
        #         filters.append(new_filter)
        #
        #         new_filter = Q(political_party__icontains=one_word)
        #         filters.append(new_filter)
        #
        #         new_filter = (
        #             Q(representative_email__icontains=one_word) |
        #             Q(representative_email2__icontains=one_word) |
        #             Q(representative_email3__icontains=one_word)
        #         )
        #         filters.append(new_filter)
        #
        #         new_filter = Q(representative_name__icontains=one_word)
        #         filters.append(new_filter)
        #
        #         new_filter = (
        #             Q(representative_twitter_handle__icontains=one_word) |
        #             Q(representative_twitter_handle2__icontains=one_word) |
        #             Q(representative_twitter_handle3__icontains=one_word)
        #         )
        #         filters.append(new_filter)
        #
        #         new_filter = Q(we_vote_id=one_word)
        #         filters.append(new_filter)
        #
        #         # Add the first query
        #         if len(filters):
        #             final_filters = filters.pop()
        #
        #             # ...and "OR" the remaining items in the list
        #             for item in filters:
        #                 final_filters |= item
        #
        #             queryset = queryset.filter(final_filters)

        bigquery_event_count = queryset.count()
        if positive_value_exists(show_all):
            bigquery_event_list = list(queryset[:1000])
        else:
            bigquery_event_list = list(queryset[:200])
    except ObjectDoesNotExist:
        # This is fine
        pass

    if positive_value_exists(bigquery_event_count):
        messages.add_message(request, messages.INFO,
                             "{bigquery_event_count:,} bigquery_events found."
                             "".format(bigquery_event_count=bigquery_event_count))

    template_values = {
        'messages_on_stage':                messages_on_stage,
        'missing_politician':               missing_politician,
        'google_civic_election_id':         google_civic_election_id,
        'bigquery_event_list':            bigquery_event_list,
        'bigquery_event_search':          bigquery_event_search,
        'show_all':                         show_all,
        'show_battleground':                show_battleground,
        'show_this_year':                   show_this_year,
        'show_ocd_id_state_mismatch':       show_ocd_id_state_mismatch,
        'state_code':                       state_code,
        'state_list':                       sorted_state_list,
        'years_available':                  OFFICE_HELD_YEARS_AVAILABLE,
    }
    return render(request, 'import_export_bigquery/bigquery_event_list.html', template_values)
