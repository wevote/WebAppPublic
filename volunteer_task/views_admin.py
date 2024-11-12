# volunteer_task/views_admin.py
# Brought to you by We Vote. Be good.
# -*- coding: UTF-8 -*-

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages import get_messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from admin_tools.views import redirect_to_sign_in_page
from datetime import date, timedelta
from time import time
from volunteer_task.models import VolunteerWeeklyMetrics
from voter.models import Voter, voter_has_authority
from wevote_functions.functions import convert_to_int, positive_value_exists
from wevote_functions.functions_date import convert_date_to_date_as_integer
from .controllers import update_weekly_volunteer_metrics
from .models import VolunteerTeam, VolunteerTeamMember

WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


@csrf_exempt
@login_required
def scoreboard_list_view(request):
    # admin, analytics_admin, partner_organization, political_data_manager, political_data_viewer, verified_volunteer
    authority_required = {'analytics_admin', 'political_data_manager'}
    if not voter_has_authority(request, authority_required):
        return redirect_to_sign_in_page(request, authority_required)

    performance_dict = (request.GET.get('performance_dict', {}))
    if not performance_dict:
        performance_list = []
        performance_dict = {
            'scoreboard_list_view': performance_list,
        }
    else:
        performance_dict = eval(performance_dict)  # Keep existing data
        performance_list = performance_dict.get('scoreboard_list_view', [])
    status = ""
    success = True
    team_we_vote_id = request.GET.get('team_we_vote_id', False)
    recalculate_all = request.GET.get('recalculate_all', False)

    volunteer_team_list = []
    t0 = time()
    try:
        queryset = VolunteerTeam.objects.using('readonly').all().order_by('team_name')
        volunteer_team_list = list(queryset)
    except Exception as e:
        message = "COULD_NOT_GET_VOLUNTEER_TEAM_LIST1: " + str(e) + " "
        messages.add_message(request, messages.ERROR, message)
    t1 = time()
    time_difference = t1 - t0
    performance_snapshot1 = {
        'name': 'VolunteerTeam retrieve',
        'description': 'Retrieve VolunteerTeam list from database',
        'time_difference': time_difference,
    }
    performance_list.append(performance_snapshot1)

    volunteer_team_member_list = []
    voter_team_member_we_vote_id_list = []
    volunteer_team_name = ''
    which_day_is_end_of_week = 6  # Monday is 0 and Sunday is 6
    which_day_is_end_of_week_display = WEEKDAYS[which_day_is_end_of_week]
    if positive_value_exists(team_we_vote_id):
        try:
            volunteer_team = VolunteerTeam.objects.get(we_vote_id=team_we_vote_id)
            volunteer_team_name = volunteer_team.team_name
            which_day_is_end_of_week = volunteer_team.which_day_is_end_of_week
            which_day_is_end_of_week_display = WEEKDAYS[which_day_is_end_of_week]
        except Exception as e:
            status += "ERROR_FIND_VOLUNTEER_TEAM2: " + str(e) + " "

        try:
            queryset = VolunteerTeamMember.objects.using('readonly').all()
            queryset = queryset.filter(team_we_vote_id=team_we_vote_id)
            # Get the voter objects
            volunteer_team_member_list = list(queryset)
            # Just get the voter_we_vote_id's
            queryset_flat = queryset.values_list('voter_we_vote_id', flat=True).distinct()
            voter_team_member_we_vote_id_list = list(queryset_flat)
        except Exception as e:
            status += "ERROR_FIND_VOLUNTEER_TEAM_MEMBERS2: " + str(e) + " "

    t0 = time()
    results = update_weekly_volunteer_metrics(
        which_day_is_end_of_week=which_day_is_end_of_week,
        recalculate_all=recalculate_all)
    update_performance_list = results['performance_list']
    performance_dict['update_weekly_volunteer_metrics'] = update_performance_list
    t1 = time()
    time_difference = t1 - t0
    performance_snapshot = {
        'name': 'update_weekly_volunteer_metrics',
        'description': 'Calculates and updates weekly metrics',
        'time_difference': time_difference,
    }
    performance_list.append(performance_snapshot)

    # earliest_for_display_date_integer = 20240410
    today = date.today()
    earliest_for_display_date = today - timedelta(days=30)
    earliest_for_display_date_integer = convert_date_to_date_as_integer(earliest_for_display_date)

    scoreboard_list = []
    t0 = time()
    try:
        queryset = VolunteerWeeklyMetrics.objects.using('readonly').all()  # 'analytics'
        # We store summaries for the last 7 days, so we can have the deadline be different team-by-team
        queryset = queryset.filter(which_day_is_end_of_week=which_day_is_end_of_week)
        if positive_value_exists(earliest_for_display_date_integer):
            queryset = queryset.filter(end_of_week_date_integer__gte=earliest_for_display_date_integer)
        if positive_value_exists(team_we_vote_id):
            queryset = queryset.filter(voter_we_vote_id__in=voter_team_member_we_vote_id_list)
        scoreboard_list = list(queryset)
    except Exception as e:
        status += "ERROR_RETRIEVING_VOLUNTEER_TASK_COMPLETED_LIST: " + str(e) + ' '
        success = False
    t1 = time()
    time_difference = t1 - t0
    performance_snapshot = {
        'name': 'Retrieve VolunteerWeeklyMetrics list from database',
        'description': '',
        'time_difference': time_difference,
    }
    performance_list.append(performance_snapshot)

    actions_completed_dict = {}
    end_of_week_date_integer_list = []
    individual_score_dict = {}
    team_actions_completed_dict = {}
    team_score_dict = {}
    voter_display_name_by_voter_we_vote_id_dict = {}
    voter_we_vote_id_list = []

    t0 = time()
    for one_person_one_week in scoreboard_list:
        if one_person_one_week.end_of_week_date_integer not in end_of_week_date_integer_list:
            end_of_week_date_integer_list.append(one_person_one_week.end_of_week_date_integer)
        end_of_week_date_integer = one_person_one_week.end_of_week_date_integer
        voter_we_vote_id = one_person_one_week.voter_we_vote_id
        voter_display_name = one_person_one_week.voter_display_name
        voter_display_name_by_voter_we_vote_id_dict[voter_we_vote_id] = voter_display_name
        if voter_we_vote_id not in actions_completed_dict:
            actions_completed_dict[voter_we_vote_id] = {}
        if voter_we_vote_id not in individual_score_dict:
            individual_score_dict[voter_we_vote_id] = {}
        if voter_we_vote_id not in voter_we_vote_id_list:
            voter_we_vote_id_list.append(voter_we_vote_id)
        if end_of_week_date_integer not in actions_completed_dict[voter_we_vote_id]:
            actions_completed_dict[voter_we_vote_id][end_of_week_date_integer] = {
                'candidates_created': one_person_one_week.candidates_created,
                'duplicate_politician_analysis': one_person_one_week.duplicate_politician_analysis,
                'election_retrieve_started': one_person_one_week.election_retrieve_started,
                'match_candidates_to_politicians': one_person_one_week.match_candidates_to_politicians,
                'politicians_augmented': one_person_one_week.politicians_augmented,
                'politicians_deduplicated': one_person_one_week.politicians_deduplicated,
                'politicians_photo_added': one_person_one_week.politicians_photo_added,
                'politicians_requested_changes': one_person_one_week.politicians_requested_changes,
                'positions_saved': one_person_one_week.positions_saved,
                'position_comments_saved': one_person_one_week.position_comments_saved,
                'twitter_bulk_retrieve': one_person_one_week.twitter_bulk_retrieve,
                'voter_guide_possibilities_created': one_person_one_week.voter_guide_possibilities_created,
            }
        if end_of_week_date_integer not in team_actions_completed_dict:
            team_actions_completed_dict[end_of_week_date_integer] = {
                'candidates_created': 0,
                'duplicate_politician_analysis': 0,
                'election_retrieve_started': 0,
                'match_candidates_to_politicians': 0,
                'politicians_augmented': 0,
                'politicians_deduplicated': 0,
                'politicians_photo_added': 0,
                'politicians_requested_changes': 0,
                'positions_saved': 0,
                'position_comments_saved': 0,
                'twitter_bulk_retrieve': 0,
                'voter_guide_possibilities_created': 0,
            }
        team_actions_completed_dict[end_of_week_date_integer] = {
            'candidates_created':
                team_actions_completed_dict[end_of_week_date_integer]['candidates_created'] +
                one_person_one_week.candidates_created,
            'duplicate_politician_analysis':
                team_actions_completed_dict[end_of_week_date_integer]['duplicate_politician_analysis'] +
                one_person_one_week.duplicate_politician_analysis,
            'election_retrieve_started':
                team_actions_completed_dict[end_of_week_date_integer]['election_retrieve_started'] +
                one_person_one_week.election_retrieve_started,
            'match_candidates_to_politicians':
                team_actions_completed_dict[end_of_week_date_integer]['match_candidates_to_politicians'] +
                one_person_one_week.match_candidates_to_politicians,
            'politicians_augmented':
                team_actions_completed_dict[end_of_week_date_integer]['politicians_augmented'] +
                one_person_one_week.politicians_augmented,
            'politicians_deduplicated':
                team_actions_completed_dict[end_of_week_date_integer]['politicians_deduplicated'] +
                one_person_one_week.politicians_deduplicated,
            'politicians_photo_added':
                team_actions_completed_dict[end_of_week_date_integer]['politicians_photo_added'] +
                one_person_one_week.politicians_photo_added,
            'politicians_requested_changes':
                team_actions_completed_dict[end_of_week_date_integer]['politicians_requested_changes'] +
                one_person_one_week.politicians_requested_changes,
            'positions_saved':
                team_actions_completed_dict[end_of_week_date_integer]['positions_saved'] +
                one_person_one_week.positions_saved,
            'position_comments_saved':
                team_actions_completed_dict[end_of_week_date_integer]['position_comments_saved'] +
                one_person_one_week.position_comments_saved,
            'twitter_bulk_retrieve':
                team_actions_completed_dict[end_of_week_date_integer]['twitter_bulk_retrieve'] +
                one_person_one_week.twitter_bulk_retrieve,
            'voter_guide_possibilities_created':
                team_actions_completed_dict[end_of_week_date_integer]['voter_guide_possibilities_created'] +
                one_person_one_week.voter_guide_possibilities_created,
        }
    t1 = time()
    time_difference = t1 - t0
    performance_snapshot = {
        'name': 'Looping through data pulled from VolunteerWeeklyMetrics',
        'description': '',
        'time_difference': time_difference,
    }
    performance_list.append(performance_snapshot)

    end_of_week_date_integer_list = sorted(end_of_week_date_integer_list)

    # ########################################
    # Work on individual Volunteer statistics
    weekly_metrics_fields = [
        'candidates_created', 'duplicate_politician_analysis', 'election_retrieve_started',
        'match_candidates_to_politicians', 'politicians_augmented', 'politicians_deduplicated',
        'politicians_photo_added', 'politicians_requested_changes', 'positions_saved',
        'position_comments_saved', 'twitter_bulk_retrieve', 'voter_guide_possibilities_created',
    ]
    t0 = time()
    for voter_we_vote_id in voter_we_vote_id_list:
        # Set these values to true if we have any tasks completed in any of the weeks we are displaying
        individual_score_dict[voter_we_vote_id]['voter_display_name'] = \
            voter_display_name_by_voter_we_vote_id_dict[voter_we_vote_id]
        for weekly_metric_key in weekly_metrics_fields:
            individual_score_dict[voter_we_vote_id][weekly_metric_key] = 0
        individual_score_dict[voter_we_vote_id]['volunteer_task_total'] = 0
        for end_of_week_date_integer in end_of_week_date_integer_list:
            if end_of_week_date_integer in actions_completed_dict[voter_we_vote_id]:
                candidates_created = \
                    actions_completed_dict[voter_we_vote_id][end_of_week_date_integer]['candidates_created']
                duplicate_politician_analysis = \
                    actions_completed_dict[voter_we_vote_id][end_of_week_date_integer]['duplicate_politician_analysis']
                election_retrieve_started = \
                    actions_completed_dict[voter_we_vote_id][end_of_week_date_integer]['election_retrieve_started']
                match_candidates_to_politicians = \
                    actions_completed_dict[voter_we_vote_id][end_of_week_date_integer][
                        'match_candidates_to_politicians']
                politicians_augmented = \
                    actions_completed_dict[voter_we_vote_id][end_of_week_date_integer]['politicians_augmented']
                politicians_deduplicated = \
                    actions_completed_dict[voter_we_vote_id][end_of_week_date_integer]['politicians_deduplicated']
                politicians_photo_added = \
                    actions_completed_dict[voter_we_vote_id][end_of_week_date_integer]['politicians_photo_added']
                politicians_requested_changes = \
                    actions_completed_dict[voter_we_vote_id][end_of_week_date_integer]['politicians_requested_changes']
                positions_saved = \
                    actions_completed_dict[voter_we_vote_id][end_of_week_date_integer]['positions_saved']
                position_comments_saved = \
                    actions_completed_dict[voter_we_vote_id][end_of_week_date_integer]['position_comments_saved']
                twitter_bulk_retrieve = \
                    actions_completed_dict[voter_we_vote_id][end_of_week_date_integer]['twitter_bulk_retrieve']
                voter_guide_possibilities_created = \
                    actions_completed_dict[voter_we_vote_id][end_of_week_date_integer][
                        'voter_guide_possibilities_created']
                volunteer_task_total = \
                    candidates_created + duplicate_politician_analysis + election_retrieve_started + \
                    match_candidates_to_politicians + \
                    politicians_augmented + politicians_deduplicated + politicians_photo_added + \
                    politicians_requested_changes + positions_saved + position_comments_saved + \
                    twitter_bulk_retrieve + voter_guide_possibilities_created
            else:
                candidates_created = 0
                duplicate_politician_analysis = 0
                election_retrieve_started = 0
                match_candidates_to_politicians = 0
                politicians_augmented = 0
                politicians_deduplicated = 0
                politicians_photo_added = 0
                politicians_requested_changes = 0
                positions_saved = 0
                position_comments_saved = 0
                twitter_bulk_retrieve = 0
                voter_guide_possibilities_created = 0
                volunteer_task_total = 0
            individual_score_dict[voter_we_vote_id][end_of_week_date_integer] = {
                'candidates_created': candidates_created,
                'duplicate_politician_analysis': duplicate_politician_analysis,
                'election_retrieve_started': election_retrieve_started,
                'match_candidates_to_politicians': match_candidates_to_politicians,
                'politicians_augmented': politicians_augmented,
                'politicians_deduplicated': politicians_deduplicated,
                'politicians_photo_added': politicians_photo_added,
                'politicians_requested_changes': politicians_requested_changes,
                'positions_saved': positions_saved,
                'position_comments_saved': position_comments_saved,
                'twitter_bulk_retrieve': twitter_bulk_retrieve,
                'volunteer_task_total': volunteer_task_total,
                'voter_guide_possibilities_created': voter_guide_possibilities_created,
            }

            if candidates_created > 0:
                individual_score_dict[voter_we_vote_id]['candidates_created'] += candidates_created
                individual_score_dict[voter_we_vote_id]['volunteer_task_total'] += candidates_created
            if duplicate_politician_analysis > 0:
                individual_score_dict[voter_we_vote_id]['duplicate_politician_analysis'] += \
                    duplicate_politician_analysis
                individual_score_dict[voter_we_vote_id]['volunteer_task_total'] += duplicate_politician_analysis
            if election_retrieve_started > 0:
                individual_score_dict[voter_we_vote_id]['election_retrieve_started'] += election_retrieve_started
                individual_score_dict[voter_we_vote_id]['volunteer_task_total'] += election_retrieve_started
            if match_candidates_to_politicians > 0:
                individual_score_dict[voter_we_vote_id]['match_candidates_to_politicians'] += \
                    match_candidates_to_politicians
                individual_score_dict[voter_we_vote_id]['volunteer_task_total'] += match_candidates_to_politicians
            if politicians_augmented > 0:
                individual_score_dict[voter_we_vote_id]['politicians_augmented'] += politicians_augmented
                individual_score_dict[voter_we_vote_id]['volunteer_task_total'] += politicians_augmented
            if politicians_deduplicated > 0:
                individual_score_dict[voter_we_vote_id]['politicians_deduplicated'] += politicians_deduplicated
                individual_score_dict[voter_we_vote_id]['volunteer_task_total'] += politicians_deduplicated
            if politicians_photo_added > 0:
                individual_score_dict[voter_we_vote_id]['politicians_photo_added'] += politicians_photo_added
                individual_score_dict[voter_we_vote_id]['volunteer_task_total'] += politicians_photo_added
            if politicians_requested_changes > 0:
                individual_score_dict[voter_we_vote_id]['politicians_requested_changes'] += \
                    politicians_requested_changes
                individual_score_dict[voter_we_vote_id]['volunteer_task_total'] += politicians_requested_changes
            if positions_saved > 0:
                individual_score_dict[voter_we_vote_id]['positions_saved'] += positions_saved
                individual_score_dict[voter_we_vote_id]['volunteer_task_total'] += positions_saved
            if position_comments_saved > 0:
                individual_score_dict[voter_we_vote_id]['position_comments_saved'] += position_comments_saved
                individual_score_dict[voter_we_vote_id]['volunteer_task_total'] += position_comments_saved
            if twitter_bulk_retrieve > 0:
                individual_score_dict[voter_we_vote_id]['twitter_bulk_retrieve'] += twitter_bulk_retrieve
                individual_score_dict[voter_we_vote_id]['volunteer_task_total'] += twitter_bulk_retrieve
            if voter_guide_possibilities_created > 0:
                individual_score_dict[voter_we_vote_id]['voter_guide_possibilities_created'] += \
                    voter_guide_possibilities_created
                individual_score_dict[voter_we_vote_id]['volunteer_task_total'] += \
                    voter_guide_possibilities_created
    t1 = time()
    time_difference = t1 - t0
    performance_snapshot = {
        'name': 'Looping through voter_we_vote_id_list to generate individual_score_dict',
        'description': '',
        'time_difference': time_difference,
    }
    performance_list.append(performance_snapshot)

    try:
        voter_we_vote_id_list_modified = \
            sorted(voter_we_vote_id_list,
                   key=lambda x: (-convert_to_int(individual_score_dict[x]['volunteer_task_total'])))
    except Exception as e:
        voter_we_vote_id_list_modified = voter_we_vote_id_list

    # ############################
    # Now work on Team statistics
    team_score_dict['team_name'] = volunteer_team_name
    team_score_dict['which_day_is_end_of_week_display'] = which_day_is_end_of_week_display

    # Below, set these values to true if we have any tasks completed in any of the weeks we are displaying
    t0 = time()
    for weekly_metric_key in weekly_metrics_fields:
        team_score_dict[weekly_metric_key] = 0
    team_score_dict['volunteer_task_total'] = 0
    for end_of_week_date_integer in end_of_week_date_integer_list:
        if end_of_week_date_integer in team_actions_completed_dict:
            candidates_created = \
                team_actions_completed_dict[end_of_week_date_integer]['candidates_created']
            duplicate_politician_analysis = \
                team_actions_completed_dict[end_of_week_date_integer]['duplicate_politician_analysis']
            election_retrieve_started = \
                team_actions_completed_dict[end_of_week_date_integer]['election_retrieve_started']
            match_candidates_to_politicians = \
                team_actions_completed_dict[end_of_week_date_integer]['match_candidates_to_politicians']
            politicians_augmented = \
                team_actions_completed_dict[end_of_week_date_integer]['politicians_augmented']
            politicians_deduplicated = \
                team_actions_completed_dict[end_of_week_date_integer]['politicians_deduplicated']
            politicians_photo_added = \
                team_actions_completed_dict[end_of_week_date_integer]['politicians_photo_added']
            politicians_requested_changes = \
                team_actions_completed_dict[end_of_week_date_integer]['politicians_requested_changes']
            positions_saved = \
                team_actions_completed_dict[end_of_week_date_integer]['positions_saved']
            position_comments_saved = \
                team_actions_completed_dict[end_of_week_date_integer]['position_comments_saved']
            twitter_bulk_retrieve = \
                team_actions_completed_dict[end_of_week_date_integer]['twitter_bulk_retrieve']
            voter_guide_possibilities_created = \
                team_actions_completed_dict[end_of_week_date_integer]['voter_guide_possibilities_created']
            volunteer_task_total = \
                candidates_created + duplicate_politician_analysis + election_retrieve_started + \
                match_candidates_to_politicians + \
                politicians_augmented + politicians_deduplicated + politicians_photo_added + \
                politicians_requested_changes + positions_saved + position_comments_saved + \
                twitter_bulk_retrieve + voter_guide_possibilities_created
        else:
            candidates_created = 0
            duplicate_politician_analysis = 0
            election_retrieve_started = 0
            match_candidates_to_politicians = 0
            politicians_augmented = 0
            politicians_deduplicated = 0
            politicians_photo_added = 0
            politicians_requested_changes = 0
            positions_saved = 0
            position_comments_saved = 0
            twitter_bulk_retrieve = 0
            voter_guide_possibilities_created = 0
            volunteer_task_total = 0
        team_score_dict[end_of_week_date_integer] = {
            'candidates_created': candidates_created,
            'duplicate_politician_analysis': duplicate_politician_analysis,
            'election_retrieve_started': election_retrieve_started,
            'match_candidates_to_politicians': match_candidates_to_politicians,
            'politicians_augmented': politicians_augmented,
            'politicians_deduplicated': politicians_deduplicated,
            'politicians_photo_added': politicians_photo_added,
            'politicians_requested_changes': politicians_requested_changes,
            'positions_saved': positions_saved,
            'position_comments_saved': position_comments_saved,
            'twitter_bulk_retrieve': twitter_bulk_retrieve,
            'volunteer_task_total': volunteer_task_total,
            'voter_guide_possibilities_created': voter_guide_possibilities_created,
        }

        if candidates_created > 0:
            team_score_dict['candidates_created'] += candidates_created
            team_score_dict['volunteer_task_total'] += candidates_created
        if duplicate_politician_analysis > 0:
            team_score_dict['duplicate_politician_analysis'] += duplicate_politician_analysis
            team_score_dict['volunteer_task_total'] += duplicate_politician_analysis
        if election_retrieve_started > 0:
            team_score_dict['election_retrieve_started'] += election_retrieve_started
            team_score_dict['volunteer_task_total'] += election_retrieve_started
        if match_candidates_to_politicians > 0:
            team_score_dict['match_candidates_to_politicians'] += match_candidates_to_politicians
            team_score_dict['volunteer_task_total'] += match_candidates_to_politicians
        if politicians_augmented > 0:
            team_score_dict['politicians_augmented'] += politicians_augmented
            team_score_dict['volunteer_task_total'] += politicians_augmented
        if politicians_deduplicated > 0:
            team_score_dict['politicians_deduplicated'] += politicians_deduplicated
            team_score_dict['volunteer_task_total'] += politicians_deduplicated
        if politicians_photo_added > 0:
            team_score_dict['politicians_photo_added'] += politicians_photo_added
            team_score_dict['volunteer_task_total'] += politicians_photo_added
        if politicians_requested_changes > 0:
            team_score_dict['politicians_requested_changes'] += politicians_requested_changes
            team_score_dict['volunteer_task_total'] += politicians_requested_changes
        if positions_saved > 0:
            team_score_dict['positions_saved'] += positions_saved
            team_score_dict['volunteer_task_total'] += positions_saved
        if position_comments_saved > 0:
            team_score_dict['position_comments_saved'] += position_comments_saved
            team_score_dict['volunteer_task_total'] += position_comments_saved
        if twitter_bulk_retrieve > 0:
            team_score_dict['twitter_bulk_retrieve'] += twitter_bulk_retrieve
            team_score_dict['volunteer_task_total'] += twitter_bulk_retrieve
        if voter_guide_possibilities_created > 0:
            team_score_dict['voter_guide_possibilities_created'] += \
                voter_guide_possibilities_created
            team_score_dict['volunteer_task_total'] += \
                voter_guide_possibilities_created
    t1 = time()
    time_difference = t1 - t0
    performance_snapshot = {
        'name': 'Adding up scores across all weeks',
        'description': '',
        'time_difference': time_difference,
    }
    performance_list.append(performance_snapshot)

    possible_team_member_list = []
    try:
        queryset = Voter.objects.using('readonly').all().order_by('first_name')
        queryset = queryset.filter(is_political_data_manager=True)
        queryset = queryset.exclude(we_vote_id__in=voter_team_member_we_vote_id_list)
        possible_team_member_list = list(queryset)
    except Exception as e:
        message = "COULD_NOT_GET_POSSIBLE_MEMBER_LIST: " + str(e) + " "
        messages.add_message(request, messages.ERROR, message)

    messages_on_stage = get_messages(request)
    template_values = {
        'end_of_week_date_integer_list':    end_of_week_date_integer_list,
        'messages_on_stage':                messages_on_stage,
        'individual_score_dict':            individual_score_dict,
        'performance_dict':                 performance_dict,
        'scoreboard_list':                  scoreboard_list,
        'possible_team_member_list':        possible_team_member_list,
        'team_score_dict':                  team_score_dict,
        'team_we_vote_id':                  team_we_vote_id,
        'volunteer_team_list':              volunteer_team_list,
        'volunteer_team_member_list':       volunteer_team_member_list,
        'voter_we_vote_id_list':            voter_we_vote_id_list_modified,
    }
    return render(request, 'volunteer_task/scoreboard_list.html', template_values)


@csrf_exempt
@login_required
def scoreboard_list_process_view(request):
    # admin, analytics_admin, partner_organization, political_data_manager, political_data_viewer, verified_volunteer
    authority_required = {'analytics_admin', 'political_data_manager'}
    if not voter_has_authority(request, authority_required):
        return redirect_to_sign_in_page(request, authority_required)

    status = ""
    success = True
    add_team_member_we_vote_id = request.POST.get('add_team_member_we_vote_id', False)
    team_we_vote_id = request.POST.get('team_we_vote_id', False)

    volunteer_team_member_list = []

    if positive_value_exists(team_we_vote_id):
        try:
            queryset = VolunteerTeamMember.objects.using('readonly').all()
            queryset = queryset.filter(team_we_vote_id=team_we_vote_id)
            # Get the voter objects
            volunteer_team_member_list = list(queryset)
        except Exception as e:
            status += "ERROR_FIND_VOLUNTEER_TEAM_MEMBERS1: " + str(e) + " "

    # ##########################################################################
    # Delete selected voters from team
    for volunteer_team_member in volunteer_team_member_list:
        # Delete this voter from the team
        delete_variable_name = "delete_volunteer_team_member_" + str(volunteer_team_member.id)
        delete_voter_from_team = positive_value_exists(request.POST.get(delete_variable_name, False))
        voter_to_delete_we_vote_id = request.POST.get(delete_variable_name, False)
        if positive_value_exists(delete_voter_from_team):
            if positive_value_exists(team_we_vote_id) and positive_value_exists(voter_to_delete_we_vote_id):
                try:
                    number_deleted, details = VolunteerTeamMember.objects \
                        .filter(
                            team_we_vote_id=team_we_vote_id,
                            voter_we_vote_id=voter_to_delete_we_vote_id,
                        ) \
                        .delete()
                    messages.add_message(request, messages.INFO,
                                         "Deleted VolunteerTeamMember ({number_deleted})."
                                         .format(number_deleted=number_deleted))
                except Exception as e:
                    messages.add_message(request, messages.ERROR, 'Could not delete team membership1: ' + str(e))
            else:
                messages.add_message(request, messages.ERROR, 'Could not delete team membership1.')

    if positive_value_exists(team_we_vote_id) and positive_value_exists(add_team_member_we_vote_id):
        try:
            defaults = {
                'team_we_vote_id': team_we_vote_id,
                'voter_we_vote_id': add_team_member_we_vote_id,
            }
            volunteer_team_member, volunteer_team_member_created = \
                VolunteerTeamMember.objects.update_or_create(
                    team_we_vote_id=team_we_vote_id,
                    voter_we_vote_id=add_team_member_we_vote_id,
                    defaults=defaults,
                )
            if volunteer_team_member_created:
                message = \
                    "Successfully added {voter_we_vote_id}. ".format(
                        voter_we_vote_id=add_team_member_we_vote_id)
            else:
                message = \
                    "{voter_we_vote_id} is already a member. ".format(
                        voter_we_vote_id=add_team_member_we_vote_id)
            messages.add_message(request, messages.INFO, message)
        except Exception as e:
            message = "COULD_NOT_ADD_TEAM_MEMBER: " + str(e) + " "
            messages.add_message(request, messages.ERROR, message)

    return HttpResponseRedirect(reverse('volunteer_task:scoreboard_list', args=()) +
                                "?team_we_vote_id=" + team_we_vote_id)
