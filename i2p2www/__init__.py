from flask import Flask, request, g, redirect, url_for, abort, render_template, send_from_directory, safe_join
from flaskext.babel import Babel
from werkzeug.routing import BaseConverter
from docutils.core import publish_parts
import os.path
import os

from helpers import LazyView, Pagination

CURRENT_I2P_VERSION = '0.9.4'

CANONICAL_DOMAIN = 'www.i2p2.de'

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'pages')
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')

BLOG_DIR = os.path.join(os.path.dirname(__file__), 'blog')
MEETINGS_DIR = os.path.join(os.path.dirname(__file__), 'meetings/logs')

BLOG_ENTRIES_PER_PAGE = 20
MEETINGS_PER_PAGE = 20

MIRRORS_FILE = os.path.join(TEMPLATE_DIR, 'downloads/mirrors')

app = application = Flask('i2p2www', template_folder=TEMPLATE_DIR, static_url_path='/_static', static_folder=STATIC_DIR)
app.debug =  bool(os.environ.get('APP_DEBUG', 'False'))
babel = Babel(app)


#######################
# Custom URL converters

class LangConverter(BaseConverter):
    def __init__(self, url_map):
        super(LangConverter, self).__init__(url_map)
        self.regex = '(?:[a-z]{2})(-[a-z]{2})?'

    def to_python(self, value):
        parts = value.split('-')
        if len(parts) == 2:
            return parts[0] + '_' + parts[1].upper()
        return value

    def to_url(self, value):
        parts = value.split('_')
        if len(parts) == 2:
            return parts[0] + '-' + parts[1].lower()
        return value

app.url_map.converters['lang'] = LangConverter


######
# URLs

def url(url_rule, import_name, **options):
    view = LazyView('i2p2www.' + import_name)
    app.add_url_rule(url_rule, view_func=view, **options)

url('/', 'views.main_index')
url('/<lang:lang>/', 'views.site_show', defaults={'page': 'index'})
url('/<lang:lang>/<path:page>', 'views.site_show')

url('/<lang:lang>/blog/', 'blog.views.blog_index', defaults={'page': 1})
url('/<lang:lang>/blog/page/<int:page>', 'blog.views.blog_index')
url('/<lang:lang>/blog/entry/<path:slug>', 'blog.views.blog_entry')
url('/<lang:lang>/feed/blog/rss', 'blog.views.blog_rss')
url('/<lang:lang>/feed/blog/atom', 'blog.views.blog_atom')

url('/<lang:lang>/meetings/', 'meetings.views.meetings_index', defaults={'page': 1})
url('/<lang:lang>/meetings/page/<int:page>', 'meetings.views.meetings_index')
url('/<lang:lang>/meetings/<int:id>', 'meetings.views.meetings_show')
url('/<lang:lang>/meetings/<int:id>.log', 'meetings.views.meetings_show_log')
url('/<lang:lang>/meetings/<int:id>.rst', 'meetings.views.meetings_show_rst')
url('/<lang:lang>/feed/meetings/atom', 'meetings.views.meetings_atom')

url('/<lang:lang>/download', 'downloads.downloads_list')
url('/<lang:lang>/download/<path:file>', 'downloads.downloads_select')
url('/download/<string:protocol>/any/<path:file>', 'downloads.downloads_redirect', defaults={'mirror': None})
url('/download/<string:protocol>/<int:mirror>/<path:file>', 'downloads.downloads_redirect')

url('/meeting<int:id>', 'legacy.legacy_meeting')
url('/meeting<int:id>.html', 'legacy.legacy_meeting')
url('/status-<int:year>-<int:month>-<int:day>', 'legacy.legacy_status')
url('/status-<int:year>-<int:month>-<int:day>.html', 'legacy.legacy_status')
url('/<string:f>_<lang:lang>', 'legacy.legacy_show')
url('/<string:f>_<lang:lang>.html', 'legacy.legacy_show')
url('/<string:f>/', 'legacy.legacy_show')
url('/<string:f>.html', 'legacy.legacy_show')

url('/hosts.txt', 'views.hosts')
url('/robots.txt', 'views.robots')
url('/favicon.ico', 'views.favicon')


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


################
# Error handlers

@app.errorhandler(404)
def page_not_found(error):
    return render_template('global/error_404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('global/error_500.html'), 500


# Import these to ensure they get loaded
import templatevars

if __name__ == '__main__':
    app.run(debug=True)
