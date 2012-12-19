import codecs
from flask import abort, render_template, request, safe_join
import os.path
from werkzeug.contrib.atom import AtomFeed

from i2p2www import MEETINGS_DIR, MEETINGS_PER_PAGE
from i2p2www.helpers import Pagination, get_for_page
from i2p2www.meetings.helpers import get_meetings, get_meetings_feed_items


##################
# Meeting handlers

# Meeting index
def meetings_index(page):
    all_meetings = get_meetings()
    meetings = get_for_page(all_meetings, page, MEETINGS_PER_PAGE)
    if not meetings and page != 1:
        abort(404)
    pagination = Pagination(page, MEETINGS_PER_PAGE, len(all_meetings))
    return render_template('meetings/index.html', pagination=pagination, meetings=meetings)

# Renderer for specific meetings
def meetings_show(id, log=False, rst=False):
    """
    Render the meeting X.
    Either display the raw IRC .log or render as html and include .rst as header if it exists
    """
    # generate file name for the raw meeting file(and header)
    lname = str(id) + '.log'
    hname = str(id) + '.rst'
    lfile = safe_join(MEETINGS_DIR, lname)
    hfile = safe_join(MEETINGS_DIR, hname)

    # check if meeting file exists and throw error if it does not..
    if not os.path.exists(lfile):
        abort(404)

    # if the user just wanted the .log
    if log:
        # hmm... maybe replace with something non-render_template like?
        #        return render_template('meetings/show_raw.html', log=log)
        return send_from_directory(MEETINGS_DIR, lname, mimetype='text/plain')

    log=''
    header=None

    # try to load header if that makes sense
    if os.path.exists(hfile):
        # if the user just wanted the .rst...
        if rst:
            return send_from_directory(MEETINGS_DIR, hname, mimetype='text/plain')

        # open the file as utf-8 file
        with codecs.open(hfile, encoding='utf-8') as fd:
            header = fd.read()
    elif rst:
        abort(404)

    # load log
    with codecs.open(lfile, encoding='utf-8') as fd:
        log = fd.read()

    return render_template('meetings/show.html', log=log, header=header, id=id)

# Just return the raw .log for the meeting
def meetings_show_log(id):
    return meetings_show(id, log=True)

# Just return the raw .rst for the meeting
def meetings_show_rst(id):
    return meetings_show(id, rst=True)

def meetings_atom():
    feed = AtomFeed('I2P Meetings', feed_url=request.url, url=request.url_root)
    items = get_meetings_feed_items(10)
    for item in items:
        feed.add(item['title'],
                 item['content'],
                 title_type='html',
                 content_type='html',
                 url=item['url'],
                 updated=item['updated'])
    return feed.get_response()
