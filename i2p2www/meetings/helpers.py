import codecs
import datetime
from docutils.core import publish_parts
from flask import abort, g, safe_join, url_for
import os
import os.path

from i2p2www import MEETINGS_DIR


########################
# Meeting helper methods

def get_meetings_feed_items(num=0):
    meetings = get_meetings(num)
    items = []
    for meeting in meetings:
        a = {}
        a['title'] = meeting['parts']['title']
        a['content'] = meeting['parts']['fragment']
        a['url'] = url_for('meetings_show', lang=g.lang, id=meeting['id'])
        a['updated'] = (meeting['date'] if meeting['date'] else datetime.datetime(0))
        items.append(a)
    return items

def get_meetings(num=0):
    meetings_ids = get_meetings_ids(num)
    meetings = []
    for id in meetings_ids:
        parts = render_meeting_rst(id)
        if parts:
            try:
                date = datetime.datetime.strptime(parts['title'], 'I2P dev meeting, %B %d, %Y &#64; %H:%M %Z')
            except ValueError:
                try:
                    date = datetime.datetime.strptime(parts['title'], 'I2P dev meeting, %B %d, %Y')
                except ValueError:
                    date = None
            a = {}
            a['id'] = id
            a['date'] = date
            a['parts'] = parts
            meetings.append(a)
    return meetings

def get_meetings_ids(num=0):
    """
    Returns the latest #num valid meetings, or all meetings if num=0.
    """
    # list of meetings
    meetings=[]
    # walk over all directories/files
    for v in os.walk(MEETINGS_DIR):
        # iterate over all files
        for f in v[2]:
            # ignore all non-.rst files
            if not f.endswith('.rst'):
                continue
            meetings.append(int(f[:-4]))
    meetings.sort()
    meetings.reverse()
    if (num > 0):
        return meetings[:num]
    return meetings

def render_meeting_rst(id):
    # check if that file actually exists
    name = '%03d.rst' % id
    path = safe_join(MEETINGS_DIR, name)
    if not os.path.exists(path):
        abort(404)

    # read file
    with codecs.open(path, encoding='utf-8') as fd:
        content = fd.read()

    return publish_parts(source=content, source_path=MEETINGS_DIR, writer_name="html")
