"""This module connect aTimeLogger API."""
import requests
import json
import arrow
from datetime import datetime

INTERVAL_MAX = 100000
DAYS_NEW = 2


def get_time_token():
    """
    Return access token for aTimeLogger.
    See the post for more info about the API, http://blog.timetrack.io/rest-api/
    """
    client_id = "androidClient"
    client_secret = "secret"

    # get username and password from text file
    lines = [line.rstrip('\n') for line in open('pass.txt')]
    username, password, dev_token = lines

    authorization_url = "https://app.atimelogger.com/oauth/token?username={0}&password={1}&grant_type=password". \
        format(username, password)
    token = requests.post(authorization_url, auth=(client_id, client_secret))
    time_token = json.loads(token.text)['access_token']
    return time_token


def get_types(time_token):
    """
    Retrieve types data from aTimeLogger.
    :param time_token: access token to request data.
    :return: A list of dict for types data.
    """
    r_type = requests.get("https://app.atimelogger.com/api/v2/types",
                          headers={'Authorization': "bearer " + time_token})
    types = json.loads(r_type.text)
    return types['types']


def get_all_intervals(time_token):
    """
    Retrieve all intervals data from aTimeLogger. Number of entries is limited by INTERVAL_MAX.
    :param time_token: access token to request data.
    :return: A list of dict for intervals data.
    """
    r_interval = requests.get("https://app.atimelogger.com/api/v2/intervals",
                              params={'limit': INTERVAL_MAX, 'order': 'asc'},
                              headers={'Authorization': "bearer " + time_token})
    intervals = json.loads(r_interval.text)
    return intervals['intervals']


def get_new_intervals(time_token):
    """
    Retrieve new intervals data from aTimeLogger. New intervals is defined by DAYS_NEW.
    :param time_token: access token to request data.
    :return: A list of dict for intervals data.
    """
    now = arrow.get(datetime.now(), 'US/Eastern')
    start = now.replace(days=-DAYS_NEW).floor('day')
    r_interval = requests.get("https://app.atimelogger.com/api/v2/intervals",
                              params={'from': str(start.timestamp), 'to': str(now.timestamp)},
                              headers={'Authorization': "bearer " + time_token})
    intervals = json.loads(r_interval.text)
    return intervals['intervals']
