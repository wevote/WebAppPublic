# apis_v1/documentation_source/backup_one_table_to_s3_doc.py
# Brought to you by We Vote. Be good.
# -*- coding: UTF-8 -*-


def backup_one_table_to_s3_doc_template_values(url_root):
    """
    Show documentation about friendList
    """
    required_query_parameter_list = [
        {
            'name':         'table_name',
            'value':        'string',  # boolean, integer, long, string
            'description':  'the name of the table to save to s3',
        },
        {
            'name':         'api_key',
            'value':        'string (from post, cookie, or get (in that order))',  # boolean, integer, long, string
            'description':  'The unique key provided to any organization using the WeVoteServer APIs',
        },
    ]
    optional_query_parameter_list = [
    ]

    potential_status_codes_list = [
        {
            'code':         'VALID_VOTER_DEVICE_ID_MISSING',
            'description':  'Cannot proceed. A valid voter_device_id parameter was not included.',
        },
        {
            'code':         'VALID_VOTER_ID_MISSING',
            'description':  'Cannot proceed. A valid voter_id was not found.',
        },
    ]

    try_now_link_variables_dict = {
        'table_name':     'campaign_campaignx',
    }

    api_response = '{\n' \
                   '  "success": boolean,\n' \
                   '  "status": string,\n' \
                   '  "temp_file_name": string,\n' \
                   '  "dump_table_to_tmp_completed": string,\n' \
                   '  "tmp_file_to_s3_completed": string,\n' \
                   '  "aws_s3_file_url": string,\n' \
                   '}]'

    template_values = {
        'api_name': 'backupOneTableToS3',
        'api_slug': 'backupOneTableToS3',
        'api_introduction':
            "Uses pg_dump to save a backup image of a postgres file to a tmp file, and copies that temp file as an "
            "AWS s3 file for use by the local instance of server (on a developers Mac).<br>  This allows the developer to "
            "populate their local postgres database with a limited set of files from the master server (see "
            "allowable_tables in retrieve_tables/controllers_master.py)<br>  The response contains an s3 URL to the file "
            "for use from the local server instance.  This is a part of the \"Fast Load\" developer's tool",
        'try_now_link': 'apis_v1:backupOneTableToS3View',
        'try_now_link_variables_dict': try_now_link_variables_dict,
        'url_root': url_root,
        'get_or_post': 'GET',
        'required_query_parameter_list': required_query_parameter_list,
        'optional_query_parameter_list': optional_query_parameter_list,
        'api_response': api_response,
        'api_response_notes':
            "",
        'potential_status_codes_list': potential_status_codes_list,
    }
    return template_values
