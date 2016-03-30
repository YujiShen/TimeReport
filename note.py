import evernote.edam.type.ttypes as ever_types
from evernote.api.client import EvernoteClient
import binascii
import hashlib
from analysis import LEVEL2STR
from time_func import ts2datetime
import re

DIARY = "c0e4e8e9-465f-4ebc-9053-88878e09eedf"
REVIEW = '17caf5bc-7295-4e55-ac16-3d291f587946'
DAILY_TAG = """<div>
    <ul style="list-style-type: none; padding: 0; margin: 0 0 10px 0;">
        <li style="background-color: #444444; color: #eeeeee; font-weight: bold; display: inline; padding: 3px 6px 3px 6px; margin-right: 12px;">Y%Y</li>
        <li style="background-color: #444444; color: #eeeeee; font-weight: bold; display: inline; padding: 3px 6px 3px 6px; margin-right: 12px;">M%m</li>
        <li style="background-color: #444444; color: #eeeeee; font-weight: bold; display: inline; padding: 3px 6px 3px 6px; margin-right: 12px;">D%d</li>
        <li style="background-color: #444444; color: #eeeeee; font-weight: bold; display: inline; padding: 3px 6px 3px 6px; margin-right: 12px;">W%V</li>
        <li style="background-color: #444444; color: #eeeeee; font-weight: bold; display: inline; padding: 3px 6px 3px 6px; margin-right: 12px;">DY%j</li>
        <li style="background-color: #444444; color: #eeeeee; font-weight: bold; display: inline; padding: 3px 6px 3px 6px; margin-right: 12px;">WD%a</li>
    </ul>
</div>"""


def get_note_token():
    """Return dev_token for Evernote."""
    lines = [line.rstrip('\n') for line in open('pass.txt')]
    dev_token = lines[2]
    return dev_token


def headify(word):
    """
    Make given string to heading style in Evernote.
    :param word: str to format.
    :return: formatted string.
    """
    heading = '<div><span style="font-size: 20px;"><b>' \
              '<span style="font-family: Verdana;">{0}</span></b></span></div>'.format(word)
    return heading


def create_resources(file_list=None):
    """
    Transform image to Evernote resource object.
    :param file_list: a list of image file path.
    :return: a list of resource objects.
    """
    resources = []
    if file_list:
        for file_name in file_list:
            image = open(file_name, 'rb').read()
            md5 = hashlib.md5()
            md5.update(image)
            hash_value = md5.digest()

            data = ever_types.Data()
            data.size = len(image)
            data.bodyHash = hash_value
            data.body = image

            resource = ever_types.Resource()
            resource.mime = 'image/png'
            resource.data = data
            resources.append(resource)
    return resources


def resoursify(resource, width=None):
    """
    Make given Evernote resource object have right xml format for insertion.
    :param resource: Evernote resource object from create_resource().
    :param width: the width of image in Evernote.
    :return: a resource after formatted.
    """
    hex_hash = binascii.hexlify(resource.data.bodyHash)
    if width:
        resource = "<en-media type=\"%s\" hash=\"%s\" width=\"%d\"/><br />" % \
                    (resource.mime, hex_hash, width)
    else:
        resource = "<en-media type=\"%s\" hash=\"%s\" /><br />" % \
                    (resource.mime, hex_hash)
    return resource


def connect_note():
    """Connect to Evernote API."""
    dev_token = get_note_token()
    client = EvernoteClient(token=dev_token, sandbox=False)
    note_store = client.get_note_store()
    return dev_token, note_store


def create_note(auth_token, note_store, level, note_title,
                resources=None, headings=None, widths=None,
                tag=None, intro=None, ending=None):
    """
    Create note in Evernote.
    :param auth_token: development token.
    :param note_store: note store object.
    :param level: (int) time frame number.
    :param note_title: (str) title for note.
    :param resources: (list) resources (images) add into note.
    :param headings: (list) headers for images.
    :param widths: (list) width of image.
    :param tag: (str) a div contain list of tags for future search.
    :param intro: (str) Some text add before all images.
    :param ending: (str) Other title add after all images.
    :return: note.
    """
    # Create note object
    our_note = ever_types.Note()
    our_note.title = note_title

    # Build body of note
    note_body = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    note_body += "<!DOCTYPE en-note SYSTEM \"http://xml.evernote.com/pub/enml2.dtd\">"
    note_body += "<en-note>"
    if tag is not None:
        note_body += tag
    if intro is not None:
        note_body = note_body + intro + '<br /><br />'
    if resources:
        # Add Resource objects to note body
        our_note.resources = resources
        for resource, heading, width in zip(resources, headings, widths):
            heading = headify(heading)
            note_body += heading
            resource = resoursify(resource, width)
            note_body += resource
    if ending is None:
        ending = "Have a nice {0}!".format(LEVEL2STR[level][:-1])
    note_body += headify(ending)
    note_body += "<br /></en-note>"

    our_note.content = note_body
    if level == 0:
        our_note.notebookGuid = DIARY
    else:
        our_note.notebookGuid = REVIEW

    note = note_store.createNote(auth_token, our_note)
    return note


def find_notebook_guid(auth_token, note_store, notebook):
    """
    Find guid for notebook in Evernote.
    :param auth_token: development token.
    :param note_store: note store object.
    :param notebook: (str) notebook name.
    :return: (list) all guid satisfied with search.
    """
    dev_token, note_store = connect_note()
    notebooks = note_store.listNotebooks()
    guids = []
    for n in notebooks:
        if n.name == notebook:
            guids.append(n.guid)
    return guids


def find_note(keywords):
    """
    Find note content by keyword.
    :param keywords: (str) keyword for search.
    :return: (str) first result content.
    """
    from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
    dev_token, note_store = connect_note()
    search = NoteFilter()
    search.words = keywords
    search.ascending = False

    spec = NotesMetadataResultSpec()
    spec.includeTitle = True

    our_note_list = note_store.findNotesMetadata(dev_token, search, 0, 100, spec)
    note_content = note_store.getNoteContent(dev_token, our_note_list.notes[0].guid)
    return note_content


def create_tag(tag_list):
    """
    Create tags like element for notes from tag list.
    :param tag_list: a list of tag string.
    :return: (str) html for tags.
    """
    tag_span = """<span style="background-color: gainsboro; color: dimgray; font-weight: bold; font-size:90%;padding: 3px 8px; border-radius: 12px;white-space:nowrap;">{0}</span>&nbsp;&nbsp;"""
    tag_div_start = """<div style="margin:0px 0 7px 0;">"""
    tag_div_end = """</div>"""
    result = tag_div_start
    for tag in tag_list:
        result += tag_span.format(tag)
    result += tag_div_end
    return result


def date_tag(timestamp, level, tzinfo='US/Eastern'):
    """
    Create tags element for notes.
    :param timestamp: unix start time of the date.
    :param level: (int) time frame number.
    :param tzinfo: time zone.
    :return: (str) html tags.
    """
    date_time = ts2datetime(timestamp, tzinfo)
    tag_list = None
    if level == 0:
        tag_list = date_time.strftime('Y%Y,M%m,D%d,W%V,DY%j,WD%a').split(",")
    elif level == 1:
        tag_list = date_time.strftime('Y%Y,W%V').split(",")
    elif level == 2:
        tag_list = date_time.strftime('Y%Y,M%m').split(",")
    tag_html = create_tag(tag_list)
    return tag_html


def insert_tag(tag_list, note):
    """
    Insert tags into beginning of note content.
    :param tags: (list) list of tags.
    :param note: (note) an Evernote note object.
    :return: (note) note with new content.
    """
    tags = create_tag(tag_list)
    content = note.content
    m = re.search('.*<en-note[^>]*>', content, re.DOTALL)
    end = m.end()
    part_1, part_2 = content[:end], content[end:]
    new_content = part_1 + tags + part_2
    note.content = new_content
    return note