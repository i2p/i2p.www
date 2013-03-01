from flask import Flask, request, g, redirect, url_for, abort, render_template, send_from_directory, safe_join
from flaskext.babel import Babel
from flask.ext.cache import Cache
from docutils.core import publish_parts
import os.path
import os


###########
# Constants

CURRENT_I2P_VERSION = '0.9.4'

CANONICAL_DOMAIN = 'www.i2p2.de'

BLOG_POSTS_PER_FEED = 10
BLOG_POSTS_PER_PAGE = 10
MEETINGS_PER_PAGE = 20

SUPPORTED_LANGS = [
    'en',
    'es',
#    'zh',
    'de',
    'fr',
#    'it',
#    'nl',
#    'ru',
    'sv',
#    'cs',
#    'ar',
#    'el',
    ]

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'pages')
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
BLOG_DIR = os.path.join(os.path.dirname(__file__), 'blog')
MEETINGS_DIR = os.path.join(os.path.dirname(__file__), 'meetings/logs')
SITE_DIR = os.path.join(TEMPLATE_DIR, 'site')
MIRRORS_FILE = os.path.join(TEMPLATE_DIR, 'downloads/mirrors')


###################
# Application setup

app = application = Flask('i2p2www', template_folder=TEMPLATE_DIR, static_url_path='/_static', static_folder=STATIC_DIR)
app.debug =  bool(os.environ.get('APP_DEBUG', 'False'))
babel = Babel(app)
cache = Cache(app, config={
    'CACHE_DEFAULT_TIMEOUT': 600,
    #'CACHE_TYPE': '', # See http://packages.python.org/Flask-Cache/#configuring-flask-cache
    })


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
        # TEMPORARY: enable external themes
        # TODO: Remove this (and the corresponding lines in global/layout.html
        if theme[:7] == 'http://':
            g.exttheme = theme
            theme = 'duck'
    if not os.path.isfile(safe_join(safe_join(STATIC_DIR, 'styles'), '%s/desktop.css' % theme)):
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
import urls
