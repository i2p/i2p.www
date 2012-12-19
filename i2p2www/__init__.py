from jinja2 import Environment, FileSystemLoader, environmentfilter
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, send_from_directory, safe_join
from flaskext.babel import Babel
from werkzeug.contrib.atom import AtomFeed
from docutils.core import publish_parts
import datetime
import os.path
import os
import fileinput
import codecs
from random import randint
try:
    import json
except ImportError:
    import simplejson as json

from helpers import LazyView, Pagination

CURRENT_I2P_VERSION = '0.9.4'

CANONICAL_DOMAIN = 'www.i2p2.de'

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'pages')
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')

BLOG_DIR = os.path.join(os.path.dirname(__file__), 'blog')
MEETINGS_DIR = os.path.join(os.path.dirname(__file__), 'meetings')

BLOG_ENTRIES_PER_PAGE = 20
MEETINGS_PER_PAGE = 20

MIRRORS_FILE = os.path.join(TEMPLATE_DIR, 'downloads/mirrors')

app = application = Flask('i2p2www', template_folder=TEMPLATE_DIR, static_url_path='/_static', static_folder=STATIC_DIR)
app.debug =  bool(os.environ.get('APP_DEBUG', 'False'))
babel = Babel(app)


######
# URLs

def url(url_rule, import_name, **options):
    view = LazyView('i2p2www.' + import_name)
    app.add_url_rule(url_rule, view_func=view, **options)

url('/', 'views.main_index')
url('/<string:lang>/', 'views.site_show', defaults={'page': 'index'})
url('/<string:lang>/<path:page>', 'views.site_show')

url('/<string:lang>/blog/', 'blog.views.blog_index', defaults={'page': 1})
url('/<string:lang>/blog/page/<int:page>', 'blog.views.blog_index')
url('/<string:lang>/blog/entry/<path:slug>', 'blog.views.blog_entry')
url('/<string:lang>/feed/blog/rss', 'blog.views.blog_rss')
url('/<string:lang>/feed/blog/atom', 'blog.views.blog_atom')


#################
# Babel selectors

@babel.localeselector
def get_locale():
    # If the language is already set from the url, use that
    if hasattr(g, 'lang'):
        return g.lang
    # otherwise try to guess the language from the user accept
    # header the browser transmits. The best match wins.
    return request.accept_languages.best_match(['en', 'es', 'zh', 'de', 'fr', 'it', 'nl', 'ru', 'sv', 'cs', 'ar'])


##########################
# Hooks - helper functions

def after_this_request(f):
    if not hasattr(g, 'after_request_callbacks'):
        g.after_request_callbacks = []
    g.after_request_callbacks.append(f)
    return f


###########################
# Hooks - url preprocessing

@app.url_value_preprocessor
def pull_lang(endpoint, values):
    if not values:
        return
    g.lang=values.pop('lang', None)

@app.url_defaults
def set_lang(endpoint, values):
    if not values:
        return
    if endpoint == 'static':
        # Static urls shouldn't have a lang flag
        # (causes complete reload on lang change)
        return
    if 'lang' in values:
        return
    if hasattr(g, 'lang'):
        values['lang'] = g.lang


########################
# Hooks - before request

# Detect and store chosen theme
@app.before_request
def detect_theme():
    theme = 'duck'
    if 'style' in request.cookies:
        theme = request.cookies['style']
    if 'theme' in request.args.keys():
        theme = request.args['theme']
    if not os.path.isfile(safe_join(safe_join(STATIC_DIR, 'styles'), '%s.css' % theme)):
        theme = 'duck'
    g.theme = theme
    @after_this_request
    def remember_theme(resp):
        if g.theme == 'duck' and 'style' in request.cookies:
            resp.delete_cookie('style')
        elif g.theme != 'duck':
            resp.set_cookie('style', g.theme)
        return resp


#######################
# Hooks - after request

@app.after_request
def call_after_request_callbacks(response):
    for callback in getattr(g, 'after_request_callbacks', ()):
        response = callback(response)
    return response


##################
# Template filters

@app.template_filter('restructuredtext')
def restructuredtext(value):
    parts = publish_parts(source=value, writer_name="html")
    return parts['html_body']


####################
# Context processors

@app.context_processor
def utility_processor():
    # Provide the canonical link to the current page
    def get_canonical_link():
        protocol = request.url.split('//')[0]
        return protocol + '//' + CANONICAL_DOMAIN + request.path

    # Convert an I2P url to an equivalent clearnet one
    i2ptoclear = {
        'www.i2p2.i2p': 'www.i2p2.de',
        #'forum.i2p': 'forum.i2p2.de',
        'trac.i2p2.i2p': 'trac.i2p2.de',
        'mail.i2p': 'i2pmail.org',
        }
    def convert_url_to_clearnet(value):
        if not value.endswith('.i2p'):
            # The url being passed in isn't an I2P url, so just return it
            return value
        if request.headers.get('X-I2P-Desthash') and not request.headers.get('X-Forwarded-Server'):
            # The request is from within I2P, so use I2P url
            return value
        # The request is either directly from clearnet or through an inproxy
        try:
            # Return the known clearnet url corresponding to the I2P url
            return i2ptoclear[value]
        except KeyError:
            # The I2P site has no known clearnet address, so use an inproxy
            return value + '.to'

    # Convert a paginated URL to that of another page
    def url_for_other_page(page):
        args = request.view_args.copy()
        args['page'] = page
        return url_for(request.endpoint, **args)

    # Change the theme of the current page
    def change_theme(theme):
        args = request.view_args.copy()
        args['theme'] = theme
        return url_for(request.endpoint, **args)

    return dict(i2pconv=convert_url_to_clearnet,
                url_for_other_page=url_for_other_page,
                change_theme=change_theme,
                canonical=get_canonical_link)


################
# Error handlers

@app.errorhandler(404)
def page_not_found(error):
    return render_template('global/error_404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('global/error_500.html'), 500


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
    name = str(id) + '.rst'
    path = safe_join(MEETINGS_DIR, name)
    if not os.path.exists(path):
        abort(404)

    # read file
    with codecs.open(path, encoding='utf-8') as fd:
        content = fd.read()

    return publish_parts(source=content, source_path=MEETINGS_DIR, writer_name="html")


##################
# Meeting handlers

# Meeting index
@app.route('/<string:lang>/meetings/', defaults={'page': 1})
@app.route('/<string:lang>/meetings/page/<int:page>')
def meetings_index(page):
    all_meetings = get_meetings()
    meetings = get_for_page(all_meetings, page, MEETINGS_PER_PAGE)
    if not meetings and page != 1:
        abort(404)
    pagination = Pagination(page, MEETINGS_PER_PAGE, len(all_meetings))
    return render_template('meetings/index.html', pagination=pagination, meetings=meetings)

# Renderer for specific meetings
@app.route('/<string:lang>/meetings/<int:id>')
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
@app.route('/<string:lang>/meetings/<int:id>.log')
def meetings_show_log(id):
    return meetings_show(id, log=True)

# Just return the raw .rst for the meeting
@app.route('/<string:lang>/meetings/<int:id>.rst')
def meetings_show_rst(id):
    return meetings_show(id, rst=True)

@app.route('/<string:lang>/feed/meetings/atom')
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


###################
# Download handlers

# Read in mirrors from file
def read_mirrors():
    file = open(MIRRORS_FILE, 'r')
    dat = file.read()
    file.close()
    lines=dat.split('\n')
    ret={}
    for line in lines:
        try:
            obj=json.loads(line)
        except ValueError:
            continue
        if 'protocol' not in obj:
            continue
        protocol=obj['protocol']
        if protocol not in ret:
            ret[protocol]=[]
        ret[protocol].append(obj)
    return ret

# List of downloads
@app.route('/<string:lang>/download')
def downloads_list():
    # TODO: read mirror list or list of available files
    return render_template('downloads/list.html')

# Specific file downloader
@app.route('/<string:lang>/download/<path:file>')
def downloads_select(file):
    if (file == 'debian'):
        return render_template('downloads/debian.html')
    mirrors=read_mirrors()
    data = {
        'version': CURRENT_I2P_VERSION,
        'file': file,
        }
    obj=[]
    for protocol in mirrors.keys():
        a={}
        a['name']=protocol
        a['mirrors']=mirrors[protocol]
        for mirror in a['mirrors']:
            mirror['url']=mirror['url'] % data
        obj.append(a)
    return render_template('downloads/select.html', mirrors=obj, file=file)

@app.route('/download/<string:protocol>/any/<path:file>', defaults={'mirror': None})
@app.route('/download/<string:protocol>/<int:mirror>/<path:file>')
def downloads_redirect(protocol, file, mirror):
    mirrors=read_mirrors()
    if not protocol in mirrors:
        abort(404)
    mirrors=mirrors[protocol]
    data = {
        'version': CURRENT_I2P_VERSION,
        'file': file,
        }
    if mirror:
        return redirect(mirrors[mirror]['url'] % data)
    return redirect(mirrors[randint(0, len(mirrors) - 1)]['url'] % data)


############
# Root files

@app.route('/hosts.txt')
def hosts():
    return send_from_directory(STATIC_DIR, 'hosts.txt', mimetype='text/plain')

@app.route('/robots.txt')
def robots():
    return send_from_directory(STATIC_DIR, 'robots.txt', mimetype='text/plain')


##############
# Legacy paths

@app.route('/meeting<int:id>')
@app.route('/meeting<int:id>.html')
def legacy_meeting(id):
    return redirect(url_for('meetings_show', id=id, lang='en'))

@app.route('/status-<int:year>-<int:month>-<int:day>')
@app.route('/status-<int:year>-<int:month>-<int:day>.html')
def legacy_status(year, month, day):
    return redirect(url_for('blog_entry', lang='en', slug=('%s/%s/%s/status' % (year, month, day))))

LEGACY_MAP={
    'download': 'downloads_list'
}

@app.route('/<string:f>_<string:lang>')
@app.route('/<string:f>_<string:lang>.html')
@app.route('/<string:f>')
@app.route('/<string:f>.html')
def legacy_show(f):
    lang = 'en'
    if hasattr(g, 'lang') and g.lang:
        lang = g.lang
    if f in LEGACY_MAP:
        return redirect(url_for(LEGACY_MAP[f], lang=lang))
    else:
        return redirect(url_for('site_show', lang=lang, page=f))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run(debug=True)
