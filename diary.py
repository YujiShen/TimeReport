import requests
from requests_oauthlib import OAuth2Session
import json
import pandas as pd

client_id = "androidClient"
client_secret = "secret"
lines = [line.rstrip('\n') for line in open('pass.txt')]
username = lines[0]
password = lines[1]
dev_token = lines[2]

authorization_url = "https://app.atimelogger.com/oauth/token?username={0}&password={1}&grant_type=password".format(username, password)
token = requests.post(authorization_url, auth=(client_id, client_secret))
access_token = json.loads(token.text)['access_token']

r_type = requests.get("https://app.atimelogger.com/api/v2/types", 
                 headers = {'Authorization': "bearer " + access_token})
json_type = json.loads(r_type.text)

dict_group = {d['guid']:d['name'] for d in json_type['types'] if d['group']}
dict_type = {}
dict_id = {}
for d in json_type['types']:
    if not d['group']:
        parent_name = dict_group[d['parent']['guid']] if d['parent'] != None else None
        dict_type[d['guid']] = (d['name'], parent_name)
        dict_id[d['name']] = (d['guid'], parent_name)

from datetime import datetime, date, timedelta
def getTime(unixSecond):
    """"
    unixSecond: unix timestamp
    returns: string format of date time for unix timestamp
    """
    return str(datetime.fromtimestamp(unixSecond))

def getDelta(duration):
    """"
    duration: duration in second
    returns: string format of duration
    """
    return str(timedelta(seconds = duration)).split('.')[0]

def getThisWeek(past = False):
    """"
    past: whether the week want has past or not, if 'True', get last week
    returns: tuple of begin and end of the week in seconds (integer)
    """
    today = date.today()
    if(past):
        d = timedelta(today.weekday())
        end = today - d
        begin = end - timedelta(7)
    else:
        end = today + timedelta(1)
        d = timedelta(today.weekday())
        begin = today - d
    begin_s = int(begin.strftime("%s"))
    end_s = int(end.strftime("%s"))
    return (begin_s, end_s)

today = date.today()
day_delta = timedelta(1)
yesterday = today - day_delta
## Following method will generate 4-hours difference with actual time
# today_s = (today - date(1970,1,1)).total_seconds()
# yesterday_s = (yesterday - date(1970,1,1)).total_seconds()
today_s = today.strftime("%s")
yesterday_s = yesterday.strftime("%s")
params = {'from': int(yesterday_s), 'to': int(today_s)}

r_today = requests.get("https://app.atimelogger.com/api/v2/intervals", 
                 params = params, headers = {'Authorization': "bearer " + access_token})
intervals = json.loads(r_today.text)['intervals']

from collections import defaultdict

task = defaultdict(dict)
for d in intervals:
    if d['comment']:
        task[d['comment']]['Group'] = dict_type[d['type']['guid']][1] if dict_type[d['type']['guid']][1] else dict_type[d['type']['guid']][0]
        if "Time" in task[d['comment']].keys():
            task[d['comment']]['Time'] += (d['to'] - d['from'])
            task[d['comment']]['N'] += 1
        else:
            task[d['comment']]['Time'] = (d['to'] - d['from'])
            task[d['comment']]['N'] = 1

task_list = []
for k, v in task.items():
    task_list.append([k, v['Group'], getDelta(v['Time']), str(v['N']), getDelta(v['Time']/v['N'])])

from evernote.api.client import EvernoteClient
client = EvernoteClient(token=dev_token, sandbox=False)
noteStore = client.get_note_store()

## search diary template
from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
noteStore = client.get_note_store()
search = NoteFilter()
search.words = "Daily Review Template"
search.ascending = False

spec = NotesMetadataResultSpec()
spec.includeTitle = True

ourNoteList = noteStore.findNotesMetadata(dev_token, search, 0, 100, spec)
template = noteStore.getNoteContent(dev_token, ourNoteList.notes[0].guid)

## get Diary notebook guid
notebooks = noteStore.listNotebooks()
for n in notebooks:
    if(n.name == 'Diary'):
        diary_notebook = n.guid

start = template.find("<tr>", template.find("<tr>") + 1)
end = template.find("</tr>", template.find("</tr>") + 1)
row_template = template[start:end+len("</tr>")]

rows = ""
for task in task_list:
    row = row_template
    for item in task:
        # "&" will cause error when parsing HTML to create note
        item = str(item).replace("&", "&amp;")
        row = row.replace('<br/>', item, 1)
    rows += row
rows
diary = template[:start] + str(rows) + template[end+len('</tr>'):]
title = str(yesterday).replace("-", "")

import evernote.edam.type.ttypes as Types
note = Types.Note()
note.title = title
note.content = diary
note.notebookGuid = diary_notebook
note = noteStore.createNote(note)
