from voter.models import VoterManager


def create_dev_user():
    status = ""
    success = True
    # To set up this user in the database:
    # 1. Enter your information below.
    first_name = "Samuel"
    last_name = "Adams"
    email = "samuel@adams.com"
    password = "GoodAle1776"
    # 2. Set allow_create to True
    allow_create = False
    # 3. Visit in your browser: http://localhost:8000/voter/create_dev_user
    #    or https://wevotedeveloper.com:8000/voter/create_dev_user
    # After you do all of these steps, you will have an admin account on your machine you can sign in with.

    try:
        if allow_create:
            VoterManager().create_developer(first_name, last_name, email, password)
        else:
            status += "Please set allow_create to True in WeVoteServer/voter/controllers_voter_create.py"
            success = False
    except Exception as e:
        status += "Error creating developer user: " + str(e) + " "
        success = False

    return {
        'email':    email,
        'password': password,
        'status':   status,
        'success':  success,
    }
