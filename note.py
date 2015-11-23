import evernote.edam.type.ttypes as ever_types
from evernote.api.client import EvernoteClient
import binascii
import hashlib
from analysis import LEVEL2STR

DIARY = "c0e4e8e9-465f-4ebc-9053-88878e09eedf"
REVIEW = '17caf5bc-7295-4e55-ac16-3d291f587946'


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
                intro=None, ending=None):
    """
    Create note in Evernote.
    :param auth_token: development token.
    :param note_store: note store object.
    :param level: (int) time frame number.
    :param note_title: (str) title for note.
    :param resources: (list) resources (images) add into note.
    :param headings: (list) headers for images.
    :param widths: (list) width of image.
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


def find_notebook_guid(notebook):
    """
    Find guid for notebook in Evernote.
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
